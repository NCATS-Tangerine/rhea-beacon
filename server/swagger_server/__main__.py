#!/usr/bin/env python3

import connexion
import yaml
import os

from swagger_server import encoder

from flask import redirect

app = connexion.App(__name__, specification_dir='./swagger/')

with open(os.path.join(app.specification_dir, 'swagger.yaml')) as f:
    d = yaml.load(f)

basePath = d['basePath']

@app.route(basePath)
def ui():
    return redirect(f'{basePath}/ui')

def main():
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Translator Knowledge Beacon API'})
    app.run(port=8080)


if __name__ == '__main__':
    main()
