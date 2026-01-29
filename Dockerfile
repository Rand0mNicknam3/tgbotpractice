FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /mybot

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["python","app.py"]
