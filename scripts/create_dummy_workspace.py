import os

from cascade.models import BasicModel, ModelRepo, Workspace

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    ws_path = os.path.join(BASE_DIR, "dummy_workspace")
    try:
        os.makedirs(ws_path)
    except FileExistsError as e:
        raise FileExistsError("The workspace already exists at this path!") from e
    ws = Workspace(ws_path)

    repo = ModelRepo(os.path.join(ws_path, "repo_1"))
    for i in range(5):
        line = repo.add_line()
        model = BasicModel()
        # Don't have this in 0.12.0 yet
        # model.describe("Hello")
        # model.comment("This is a comment")
        # model.tag(["tag1"])

    repo = ModelRepo(os.path.join(ws_path, "repo_2"))
    for i in range(5):
        line = repo.add_line()
        line.save(BasicModel(), only_meta=True)
