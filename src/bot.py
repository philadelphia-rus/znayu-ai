"""This is a simple bot TG bot which responds to every message!"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from db_answer import generate_answer, load_faq_jsonl


def get_env(
    required: list = False, filter: bool = True, use_dotenv: bool = True
) -> dict:
    """Get required environment variables"""
    # Load environment variables
    if use_dotenv:
        load_dotenv()

    res = os.environ

    # Check if all required variables are set
    for var in required:
        if var not in res:
            raise ValueError(f"Environment variable {var} is not set!")

    # Filter out non-required variables
    if filter:
        res = {k: v for k, v in res.items() if k in required}

    return res


# ========================================
# Bot initialization & Config
# ========================================
LOGGING_LEVEL = logging.INFO
USE_DOTENV = True
ENABLE_OPENAI = True
# ========================================
required_envs = ["TELEGRAM_BOT_TOKEN"]
if ENABLE_OPENAI:
    required_envs += ["OPENAI_API_KEY"]
env = get_env(required=required_envs, use_dotenv=USE_DOTENV)
OPENAI_TOKEN = env["OPENAI_API_KEY"]
TELGRAM_TOKEN = env["TELEGRAM_BOT_TOKEN"]
locale = {
    "start": "Привет! Я бот, который отвечает на вопросы по базе знаний!\n",
    "help": "Это просто бот, который отвечает на вопросы по базе знаний!",
    "error": "Я не понимаю, что ты от меня хочешь!",
    "add_knowledge_1": "Какой вопрос ты хочешь добавить?",
    "add_knowledge_2": "Какой ответ ты хочешь добавить?",
    "add_knowledge_3": "Вопрос и ответ добавлены!",
}
faq = load_faq_jsonl()
faq_strings = [faq_item["prompt"] + faq_item["completion"] for faq_item in faq]
# ========================================
storage = MemoryStorage()
bot = Bot(token=TELGRAM_TOKEN)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=LOGGING_LEVEL)
# ========================================


# ========================================
# Handlers
# ========================================


class FormNewKnowledge(StatesGroup):
    question = State()
    answer = State()


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    """Start command handler"""
    await message.answer(
        locale["start"],
        parse_mode="HTML",
    )


@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    """Help command handler"""
    await message.answer(
        locale["help"],
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@dp.message_handler(commands=["add_knowledge"])
async def add_knowledge(message: types.Message):
    """Add knowledge command handler"""
    await FormNewKnowledge.question.set()
    await message.reply(locale["add_knowledge_1"])


@dp.message_handler(state=FormNewKnowledge.question)
async def process_question(message: types.Message, state: FSMContext):
    """Process question"""
    async with state.proxy() as data:
        data["question"] = message.text
    await FormNewKnowledge.next()
    await message.reply(locale["add_knowledge_2"])


@dp.message_handler(state=FormNewKnowledge.answer)
async def process_answer(message: types.Message, state: FSMContext):
    """Process answer"""
    async with state.proxy() as data:
        data["answer"] = message.text
    await FormNewKnowledge.next()
    await message.reply(locale["add_knowledge_3"])
    faq_strings.append(data["question"] + data["answer"])
    await state.finish()


@dp.message_handler(commands=["ask"])
async def ask(message: types.Message):
    """Return inference"""
    query = " ".join(message.text.split(" ")[1:])
    ans = generate_answer(query, faq_strings, top_n=5)
    await message.reply(
        ans,
        parse_mode="HTML",
    )


@dp.message_handler()
async def general(message: types.Message):
    """Any text message will be processed here"""
    query = message.text
    ans = generate_answer(query, faq_strings, top_n=5)
    await message.answer(
        ans,
        parse_mode="HTML",
    )


# ========================================
# Main
# ========================================


async def main():
    """Start the bot"""
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
