import os
import random
import shutil

from cascade.data import ApplyModifier, RangeSampler, Wrapper
from cascade.metrics import Metric
from cascade.models import BasicModel
from cascade.repos import Repo
from cascade.workspaces import Workspace
from faker import Faker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def f(x):
    return x + 1


fake = Faker()

if __name__ == "__main__":
    ws_path = os.path.join(BASE_DIR, "dummy_workspace")
    try:
        os.makedirs(ws_path)
    except FileExistsError as e:
        raise FileExistsError("The workspace already exists at this path!") from e
    ws = Workspace(ws_path)

    os.makedirs("tmp", exist_ok=True)
    for i in range(random.randint(1, 10)):
        repo = Repo(os.path.join(ws_path, f"repo_of_{fake.word('noun')}_{i}"))
        for i in range(random.randint(1, 5)):
            line_type = random.choice(["model", "data"])
            line = repo.add_line(line_type=line_type)

            if line_type == "model":
                for i in range(random.randint(0, 10)):
                    model = BasicModel()
                    model.describe(fake.text())

                    for _ in range(random.randint(0, 10)):
                        model.add_metric(
                            Metric(
                                name=fake.word(),
                                value=random.random(),
                                dataset=fake.word(),
                                split=random.choice(["train", "val", "test", None]),
                                direction=random.choice(["up", "down", None]),
                                interval=random.choice(
                                    [(random.randint(0, 100), random.randint(0, 100)), None]
                                ),
                                extra=None,
                            )
                        )

                    for _ in range(random.randint(0, 5)):
                        name = fake.word()
                        path = f"tmp/{name}.txt"
                        with open(path, "w") as file:
                            file.write(name)
                        model.add_file(path)

                    params = {}
                    for _ in range(random.randint(0, 30)):
                        params[fake.word("noun")] = fake.random_number()

                    for _ in range(random.randint(0, 30)):
                        model.comment(fake.sentence())

                    for _ in range(random.randint(0, 20)):
                        tag = fake.word().lower()[: min(len(fake.word()), 10)]
                        model.tag(tag)

                    line.save(model)
            elif line_type == "data":
                for i in range(random.randint(1, 5)):
                    line = repo.add_line(line_type="data")
                    ds = Wrapper([0, 1, 2, 3])
                    ds = ApplyModifier(ds, f)
                    ds = RangeSampler(ds, 0, len(ds), 2)

                    ds.describe(fake.text())

                    for _ in range(random.randint(0, 30)):
                        ds.comment(fake.sentence())

                    for _ in range(random.randint(0, 20)):
                        tag = fake.word().lower()[: min(len(fake.word()), 10)]
                        ds.tag(tag)

                    line.save(ds)
            else:
                raise Exception()

    shutil.rmtree("tmp")
