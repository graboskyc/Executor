FROM python:3.13-bookworm

WORKDIR /usr/src/app

RUN apt update && apt install -y curl unzip
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Install Go
RUN curl -fsSLO https://go.dev/dl/go1.22.0.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz \
    && rm go1.22.0.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:$PATH"

COPY ./* .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]