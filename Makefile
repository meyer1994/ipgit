.PHONY: install


install:
	wget -q https://dist.ipfs.io/go-ipfs/v0.6.0/go-ipfs_v0.6.0_linux-amd64.tar.gz
	tar -xzvf go-ipfs_v0.6.0_linux-amd64.tar.gz
	install go-ipfs/ipfs /bin
