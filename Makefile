venv:
	virtualenv -p python3.6 venv

install:
	pip install .
	pip install beacon/

dev-install:
	pip install -e .
	pip install beacon/

generate:
	wget -c http://central.maven.org/maven2/io/swagger/swagger-codegen-cli/2.3.1/swagger-codegen-cli-2.3.1.jar -O swagger-codegen-cli.jar
	java -jar swagger-codegen-cli.jar generate -i api/1.3.0.yaml -l python-flask -o beacon

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
