FROM python:3.13-bookworm

WORKDIR /usr/src/app

COPY ./* .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]