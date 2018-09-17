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
if not basePath.endswith('/'):
    basePath = f'{basePath}/'

def handle_error(e):
    return redirect(f'{basePath}ui/')

def main():
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Rhea Knowledge Beacon API'})

    app.add_error_handler(404, handle_error)

    app.run(port=8080)


if __name__ == '__main__':
    main()
