import os
import uvicorn
from argparse import ArgumentParser
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import logging


SCRIPT_DIR = os.path.dirname(__file__)

logging.basicConfig(level="INFO")
logger = logging.getLogger(__file__)

app = FastAPI()


@app.get("/")
def root() -> HTMLResponse:
    root = os.path.join(os.path.dirname(SCRIPT_DIR), "web", "index.html")
    with open(root, "r") as f:
        html = f.read()
    return HTMLResponse(content=html)


@app.get("/repos")
def repos():
    return HTMLResponse()


parser = ArgumentParser()
parser.add_argument(
    "--path", type=str, help="Path of the workspace where to start UI", default="."
)
args = parser.parse_args()

cwd = os.path.abspath(args.path)

if __name__ == "__main__":
    logger.info(f"Starting in {cwd}")
    if not os.path.exists(cwd):
        raise FileNotFoundError(f"The path you passed {cwd} does not exists")

    uvicorn.run(app)
