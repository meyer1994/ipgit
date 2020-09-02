.PHONY: clean repo

REPO=.repo
HOST=http://localhost:8000


repo:
	git init --bare $(REPO)
	cp -v post-update $(REPO)/hooks/post-update
	chmod +x $(REPO)/hooks/post-update
	git remote add ipfs $(REPO)
	git remote add local $(HOST)


clean:
	rm -rf $(REPO)
	git remote remove ipfs
	git remote remove local
