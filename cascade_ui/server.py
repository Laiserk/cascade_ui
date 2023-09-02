"""
Copyright 2023 Oleg Sevostyanov, Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
