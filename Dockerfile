FROM python:slim

WORKDIR /home
COPY ./ ./

RUN apt update && apt install -y git && rm -rf /var/lib/apt/lists/*
COPY --from=ipfs/go-ipfs:latest /usr/local/bin/ipfs /bin/ipfs
RUN pip install -r requirements.txt

CMD ipfs daemon --init & sleep 5 && uvicorn ipgit:app --host 0.0.0.0 --port 8000
