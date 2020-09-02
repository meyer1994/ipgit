.PHONY: clean local

HOST=http://localhost:8000


local:
	git remote add local $(HOST)


clean:
	git remote remove local
