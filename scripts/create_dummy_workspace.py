import os
import random
import shutil

from cascade.data import (
    ApplyModifier,
    Composer,
    Concatenator,
    Filter,
    Modifier,
    RangeSampler,
    Wrapper,
    dataset,
    modifier,
)
from cascade.metrics import Metric
from cascade.models import BasicModel
from cascade.repos import Repo
from cascade.workspaces import Workspace
from faker import Faker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def f(x):
    return x + 1


def is_even(x):
    return x % 2 == 0


class VeryLongCustomModifierNameToCheckLabelTruncation(Modifier):
    """
    Only exists to see what a node does with a name that
    does not fit into the box
    """


@dataset
def load_numbers(n):
    return list(range(n))


@dataset
def load_labels(n):
    return [i % 2 for i in range(n)]


@modifier
def add_offset(items, k):
    return [item + k for item in items]


@modifier
def join_features(left, right):
    return list(zip(left, right))


def build_pipeline_shapes(repo):
    """
    A data line where every version is a pipeline of a different shape.

    Meant for eyeballing the DAG on the dataset page - how it copes with
    long chains, wide fan-ins, deep nesting, unbalanced branches and
    plain volume. Every save has a different skeleton, so each shape
    lands in a major version of its own
    """

    line = repo.add_line("pipeline_shapes", line_type="data")

    def source(n, start=0):
        return Wrapper(list(range(start, start + n)))

    shapes = []

    # A single source and nothing else - the degenerate case
    shapes.append(("A single node with no inputs", source(4)))

    # A long chain - how deep the canvas can go before it needs scrolling
    chain = source(20)
    for _ in range(6):
        chain = ApplyModifier(chain, f)
    shapes.append(("A chain of seven steps", RangeSampler(chain, 0, 10)))

    # One join with many inputs - how wide the canvas can go
    shapes.append(
        ("A fan-in of six sources", Concatenator([source(3, i) for i in range(6)]))
    )

    # One source feeding two branches that join again. Cascade meta is a
    # tree, so the shared source is written into both branches and shows up
    # as two nodes instead of one - this is what an id per dataset would fix
    shared = source(10)
    shapes.append(
        (
            "A diamond, which renders as a tree until datasets have ids",
            Concatenator([ApplyModifier(shared, f), RangeSampler(shared, 0, 5)]),
        )
    )

    # Branches of very different depth joined at the top - checks whether
    # the short branch is aligned to the top or to the join
    deep = source(30)
    for _ in range(4):
        deep = ApplyModifier(deep, f)
    shapes.append(("Unbalanced branches, one deep and one shallow", Concatenator([deep, source(2)])))

    # A balanced binary tree of joins - eight sources merged pairwise
    level = [source(2, i * 2) for i in range(8)]
    while len(level) > 1:
        level = [Concatenator(level[i : i + 2]) for i in range(0, len(level), 2)]
    shapes.append(("A binary tree of joins over eight sources", level[0]))

    # Close to a real pipeline - sources joined, sampled, then
    # composed with the labels of the same length
    train = ApplyModifier(
        RangeSampler(Concatenator([source(10), source(10, 100)]), 0, 15), f
    )
    labels = ApplyModifier(source(15), f)
    shapes.append(("Features and labels composed, close to a real pipeline", Composer([train, labels])))

    # Every node here is a FunctionModifier, so the labels come
    # from the name of the wrapped function instead of the class
    shapes.append(
        (
            "A functional pipeline built with the dataset and modifier decorators",
            join_features(add_offset(load_numbers(20), 5), load_labels(20)),
        )
    )

    # A custom modifier with a name too long for the node box
    shapes.append(
        (
            "A custom class with a name that does not fit into a node",
            VeryLongCustomModifierNameToCheckLabelTruncation(
                Filter(source(10), is_even)
            ),
        )
    )

    # Plain volume - five branches of four sources each, over thirty nodes
    groups = [
        RangeSampler(Concatenator([source(2, j * 2) for j in range(4)]), 0, 8)
        for _ in range(5)
    ]
    shapes.append(("Over thirty nodes at once, a stress test for the layout", Composer(groups)))

    for description, ds in shapes:
        ds.describe(description)
        ds.tag("pipeline-shape")
        line.save(ds, only_meta=True)


fake = Faker()

if __name__ == "__main__":
    ws_path = os.path.join(BASE_DIR, "dummy_workspace")
    try:
        os.makedirs(ws_path)
    except FileExistsError as e:
        raise FileExistsError("The workspace already exists at this path!") from e
    ws = Workspace(ws_path)

    metric_names = [fake.word() for _ in range(5)]

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
                                name=random.choice(metric_names),
                                value=random.random(),
                                dataset="dataset",
                                split=random.choice(["train", "val", "test", None]),
                                direction=random.choice(["up", "down", None]),
                                interval=random.choice(
                                    [
                                        (
                                            random.randint(0, 100),
                                            random.randint(0, 100),
                                        ),
                                        None,
                                    ]
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

    repo = Repo(os.path.join(ws_path, "test"))
    for i in range(10):
        line = repo.add_line(line_type="model")

        train_loss = random.random()
        test_loss = random.random()

        for i in range(random.randint(90, 100)):
            model = BasicModel()
            model.describe(fake.text())

            model.add_metric(
                Metric(
                    name="loss",
                    value=train_loss,
                    dataset="dataset",
                    split="train",
                    direction="down",
                    extra=None,
                )
            )

            model.add_metric(
                Metric(
                    name="loss",
                    value=test_loss,
                    dataset="dataset",
                    split="test",
                    direction="down",
                    extra=None,
                )
            )

            train_loss = train_loss * 0.9
            test_loss = test_loss * 0.98 + 0.001

            line.save(model)

    line = repo.add_line("long_line", line_type="model")

    train_loss = random.random()
    test_loss = random.random()

    for i in range(1000):
        model = BasicModel()
        model.describe(fake.text())

        model.add_metric(
            Metric(
                name="loss",
                value=random.random(),
                dataset="dataset",
                split="train",
                direction="down",
                extra=None,
            )
        )

        model.add_metric(
            Metric(
                name="loss",
                value=random.random(),
                dataset="dataset",
                split="test",
                direction="down",
                extra=None,
            )
        )

        line.save(model)

    build_pipeline_shapes(repo)

    shutil.rmtree("tmp")
