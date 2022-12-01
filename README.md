# Alembic migration testing system
---

### Usage
Under development
### Prepare dev environment
#### Install root project
If you are a poetry user (better way):
```
$ poetry install && poetry shell
$ pre-commit install
```
If you are a pip user:
```
$ python3 -m venv ./.venv && source ./.venv/bin/activate && pip install -r requirements.txt && pip install -e .
$ pre-commit install
```
#### Install test project
If you are a poetry user (better way):
```
$ cd test

# if you currently using local dev env
$ deactivate

$ poetry install && poetry shell
```
If you are a pip user:
```
$ cd test

# if you currently using local dev env
$ deactivate

$ python3 -m venv ./.venv && source ./.venv/bin/activate && pip install -r requirements.txt && pip install -e .
```
