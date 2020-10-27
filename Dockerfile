FROM ipfs/go-ipfs:latest as ipfs
FROM python:3.8-slim

WORKDIR /home

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY --from=ipfs /usr/local/bin/ipfs /bin/ipfs

RUN apt update \
    && apt install -y git \
    && rm -rf /var/lib/apt/lists/*

COPY ./ ./

CMD ipfs daemon --init \
    & sleep 5 \
    && uvicorn ipgit:app --host 0.0.0.0 --port 8000
