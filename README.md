# Rhea Beacon

Knowledge beacon wrapper for https://www.rhea-db.org/

Hosted at https://kba.ncats.io/beacon/rhea/

Python Beacon client https://github.com/NCATS-Tangerine/tkbeacon-python-client

## Getting started

This project was developed using Python 3.6, and it is advised that you use this version.

### Create virtual environment

It is helpful to keep a local virtual environment in which all local dependencies as well as the application can be installed.

```sh
virtualenv -p python3.6 venv
source venv/bin/activate
```

### Configuring

The [config/config.yaml](config/config.yaml) file can be modified to change some behaviours of this application.

### Getting the data

Use [data/Makefile](data/Makefile) for downloading and pre-processing the needed files. First enter the `data` directory, and then use the `make setup` command:
```shell
cd data
make setup
```
This will run execute the `data/generate_ec_names.py` script. It should clean up after itself, and leave behind two new files: `ecc_names.csv`, and `rhea2xrefs.tsv`. The application will use them to perform keyword searches on enzymes, and to look up xrefs for identifiers.

### Installing the application

The [Makefile](Makefile) in the root directory can be used to install the application. Make sure you are back in the root directory, and run it:

```shell
cd ..
make install
```

**Note:** if you make changes to `config/config.yaml` you will need to re-install the application for those results to be used. Alternatively, you can use the command `make dev-install` to avoid needing to re-install each time you make a change.

### Running

The [Makefile](Makefile) in the root directory can be used to run the application:

```shell
make run
```

View it at http://localhost:8080

Alternatively you can run the application within a [Docker](https://docs.docker.com/engine/installation/) container:

```shell
make docker-build
make docker-run
```

View it at http://localhost:8079

To stop the docker container you can use the command:

```shell
make docker-stop
```

## Project structure


The `beacon` package was generated with Swagger, and the `beacon_controller` package is where all the implementation details are kept.

The `beacon` package can be regenerated with the Make command. But first make sure to update the `SPECIFICATION` parameter in [Makefile](Makefile) first if the specification file has a new name.

```
make regenerate
```

Alternatively, you can run swagger-codegen-cli.jar directly:

```
java -jar swagger-codegen-cli.jar generate -i <path-to-specification-file> -l python-flask -o beacon
```

Do a careful `git diff` review of the project after regenerating to make sure that nothing vital was overwritten, and to see all the changes made. Since we keep all implementation details in `beacon_controller` there shouldn't be much to worry about, and the only thing you will need to do is plug the `beacon_controller` package back in. Again, a `git diff` will show where this needs to be done.
