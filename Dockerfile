FROM python:3.9
EXPOSE 8069
WORKDIR /code
COPY ./requirements/prod.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /code/src
COPY .env /code/.env
ENV PYTHONPATH=/code/src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8069"]
