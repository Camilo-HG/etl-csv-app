# etl-csv-app
A simple app to perform ETL from CSV files

# Project setup

You can find project's specification and dependencies at `pyproject.toml` file.
Please create a python virtual environment and install all these dependencies.

## Coding standards

In order to enforce best coding practices and that the python code is compliant with
community coding standards (PEP8 compliant), I use [flake8](https://flake8.pycqa.org/en/latest/)
and [Black](https://black.readthedocs.io/en/stable/) tools integrated to
[pre-commit](https://pre-commit.com).

Once you install all dependencies (where `pre-commit` is included), please run at the root folder:

```shell
pre-commit install
```
