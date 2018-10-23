venv:
	virtualenv -p python3.6 venv

install:
	pip install .
	pip install beacon/

dev-install:
	pip install -e .
	pip install beacon/

run:
	cd beacon && python -m swagger_server

docker-build:
	docker build -t ncats:rhea-beacon .

docker-run:
	docker run -d --rm -p 8079:8080 --name rheab ncats:rhea-beacon

docker-stop:
	docker stop rheab

docker-logs:
	docker logs -f rheab
