## Introduction
It is an assignment to collect Actual or estimated wind and solar power generation data from  [here](https://bmrs.elexon.co.uk/actual-or-estimated-wind-and-solar-power-generation).This airflow dag runs every 30 minutes interval.

## Pre-requisites
1. A Postgres database as the destination

## DEV SETUP
1. Requirements
    - Docker installed
    - Docker Compose installed
2. Clone the repo.
3. Rename `.env-example` to `.env`
4. Change the value of variables in `.env` according to your requirements.
5. Run `docker-compose up -d  --build` to start the airflow server.
6. Browse: `http://localhost:8080` to access the airflow UI. The credentials are `admin` and `admin`.

## Testing
It is recommended to perform unit test before commiting the code. To run unit test, run the following command

`pytest`

The test contains the following:
1. Integrity test on the Dag
2. Unit test on the Dag tasks
3. Unit test on every relevant function

Basic test:
Run the dag `python dags/dag_psr_sync.py`


## Type Checking and Linting
This repo uses `pre-commit` hooks to check type and linting before committing the code.

Install `pre-commit` by running `pip install pre-commit` and then run `pre-commit install` to install the hooks.

Perform below commands to:
1. Type Checking
`mypy . --pdb`
`mypy dags\.`
`mypy tests\.`
2. Linting
`ruff check .`

or full scan with `pre-commit run --all-files`

## Great Expectations
Great Expectations already run along with airflow server. If you need to recreate (For example, if you have changed the init file) it run the following command:

`python ./quality/gx_init.py --mode recreate`
