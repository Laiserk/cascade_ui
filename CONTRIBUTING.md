# Contributing
Pull requests and issues are welcome! For major changes, please open an issue first to discuss what you would like to change.
  
Please make sure to update tests and docs as appropriate.

## Developer setup

Go to the repo's root dir and install the package with
```bash
pip3 install -e .
```
*(You may want to create a venv for this)*

Then create dummy workspace for tests

```bash
python3 scripts/create_dummy_workspace.py
```

Run server inside this workspace (use latest Cascade)

```bash
cd dummy_workspace
venv\scripts\activate
```

```bash
cascade ui
```

This will run a uvicorn server with
Swagger docs are at http://localhost:8000/docs
