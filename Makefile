
env:
	virtualenv -p python3.6 venv && source venv/bin/activate

install:
	pip install -e controller/
	pip install -r server/requirements.txt

run:
	cd server && python -m swagger_server
