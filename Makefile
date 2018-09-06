
venv:
	virtualenv -p python3.6 venv

install:
	pip install controller/
	pip install -r server/requirements.txt

run:
	cd server && python -m swagger_server

docker-build:
	docker build -t ncats:rhea-beacon .

docker-run:
	docker run -d --rm -p 8090:8080 --name rheab ncats:rhea-beacon

docker-stop:
	docker stop rheab

docker-logs:
	docker logs -f rheab
