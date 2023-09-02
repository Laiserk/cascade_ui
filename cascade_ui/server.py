import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

SCRIPT_DIR = os.path.dirname(__file__)

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


if __name__ == "__main__":
    uvicorn.run(app)
