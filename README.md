# cascade_ui
This is a web-based UI for Cascade - MLOps solution for individuals or small teams

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

Run server inside this workspace

```bash
cd dummy_workspace
venv\scripts\activate
```

Windows

```bash
python3 ../cascade_ui/server.py
```

Linux
```bash
python3 ../cascade_ui/server.py
```

This will run a uvicorn server with
Swagger docs at http://localhost:8000/docs
