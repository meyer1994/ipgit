FROM python:slim

COPY ./ ./

RUN apt update
RUN apt install -y wget git make
RUN make install
RUN pip install -r requirements.txt
