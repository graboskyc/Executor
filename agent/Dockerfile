FROM python:3.13-bookworm

WORKDIR /usr/src/app

RUN apt update && apt install -y nodejs

COPY ./* .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]