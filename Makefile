install:
	cp -n config.yaml-template config.yaml
	pip install -r requirements.txt
	cd server/ && python setup.py install
	cd client/ && python setup.py install
	cd rhea/ && python setup.py install

# Creating the configuration file without installing
configure:
	cp -n config.yaml-template config.yaml

run:
	cd server && python -m swagger_server
