FROM python:3.8.8

COPY ./app /usr/src/app

WORKDIR /usr/src/app

RUN pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
