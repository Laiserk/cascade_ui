# Contributing
Pull requests and issues are welcome! For major changes, please open an issue first to discuss what you would like to change.
  
Please make sure to update tests and docs as appropriate.

## Developer setup

1. Follow [UI docs](cascade_ui/web/README.md) to build the web part locally.

2. Go to the repo's root dir and install the package with
```bash
pip3 install -e .
```
*(You may want to create a venv for this)*

3. Then create dummy workspace for tests

```bash
python3 scripts/create_dummy_workspace.py
```

4. Run server inside this workspace (use latest Cascade)

```bash
cd dummy_workspace
```

```bash
cascade ui
```

This will run a uvicorn server with
Swagger docs are at http://localhost:8000/docs
