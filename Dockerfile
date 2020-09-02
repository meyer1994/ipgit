FROM python:slim

COPY ./ ./

# Install needed tools
RUN apt update
RUN apt install -y wget git make

# Install IPFS
RUN wget -q https://dist.ipfs.io/go-ipfs/v0.6.0/go-ipfs_v0.6.0_linux-amd64.tar.gz
RUN tar -xzvf go-ipfs_v0.6.0_linux-amd64.tar.gz
RUN install go-ipfs/ipfs /bin

# Basic requirements
RUN pip install -r requirements.txt
