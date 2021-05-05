FROM ipfs/go-ipfs:latest as ipfs
FROM python:3.9.5-slim

WORKDIR /app

COPY --from=ipfs /usr/local/bin/ipfs /bin/ipfs

RUN apt update \
    && apt install -y git \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./ ./

CMD ipfs daemon --init \
    & uvicorn ipgit:app --host 0.0.0.0 --port 8000
