FROM python:3.6

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY controller /usr/src/app/controller
COPY server /usr/src/app/server

RUN pip3 install --no-cache-dir -r server/requirements.txt && pip install controller/

WORKDIR /usr/src/app/server

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
