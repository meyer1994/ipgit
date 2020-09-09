.PHONY: clean local install serve

HOST=http://localhost:8000/dev


serve:
	uvicorn ipgit:app --reload


local:
	git remote add local $(HOST)


clean:
	git remote remove local


install:
	wget -q https://dist.ipfs.io/go-ipfs/v0.6.0/go-ipfs_v0.6.0_linux-amd64.tar.gz
	tar -xzf go-ipfs_v0.6.0_linux-amd64.tar.gz
	install go-ipfs/ipfs /bin
	rm -rf go-ipfs go-ipfs_v0.6.0_linux-amd64.tar.gz
