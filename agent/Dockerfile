FROM python:3.13-bookworm

WORKDIR /usr/src/app

RUN apt update && apt install -y curl unzip
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

COPY ./* .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]