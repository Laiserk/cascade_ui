import os

from cascade.data import ApplyModifier, RangeSampler, Wrapper
from cascade.models import BasicModel
from cascade.repos import Repo
from cascade.workspaces import Workspace

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def f(x):
    return x + 1


if __name__ == "__main__":
    ws_path = os.path.join(BASE_DIR, "dummy_workspace")
    try:
        os.makedirs(ws_path)
    except FileExistsError as e:
        raise FileExistsError("The workspace already exists at this path!") from e
    ws = Workspace(ws_path)

    repo = Repo(os.path.join(ws_path, "repo_1"))
    for i in range(5):
        line = repo.add_line(line_type="model")
        model = BasicModel()
        model.describe("Hello")
        model.comment("This is a comment")
        model.tag(["tag1"])
        line.save(BasicModel(), only_meta=True)

    repo = Repo(os.path.join(ws_path, "repo_2"))
    for i in range(5):
        line = repo.add_line(line_type="data")
        ds = Wrapper([0, 1, 2, 3])
        ds = ApplyModifier(ds, f)
        ds = RangeSampler(ds, 0, len(ds), 2)
        line.save(ds)
