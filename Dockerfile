FROM python:slim

COPY ./ ./

# Install needed tools
RUN apt update
RUN apt install -y wget git make

# Install IPFS
RUN make install

# Basic requirements
RUN pip install -r requirements.txt
