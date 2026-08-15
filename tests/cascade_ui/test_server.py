"""
Copyright 2023-2025 Oleg Sevostyanov, Ilia Moiseev

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
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

sys.path.append(BASE_DIR)
from cascade_ui.models import CompareRequest, ItemSearchRequest
from cascade_ui.server import LinePathSpec, ModelPathSpec, RepoPathSpec, Server


def test_repos(workspace):
    path = workspace.get_root()

    s = Server(path)
    repo = s.repo(RepoPathSpec(repo="repo"))
    assert repo.name == "repo"


def test_lines(workspace):
    path = workspace.get_root()

    s = Server(path)
    line = s.line(LinePathSpec(repo="repo", line="00000"))
    assert line.len == 1
    assert line.name == "00000"


def test_model(workspace):
    path = workspace.get_root()

    s = Server(path)
    model = s.model(ModelPathSpec(repo="repo", line="00000", num=0))
    assert len(model.artifacts) == 0


def paths_of(suggestions):
    return [item.path for item in suggestions.items]


def test_item_index_skips_data_lines(compare_workspace):
    s = Server(compare_workspace.get_root())

    index = s._get_item_index()

    assert paths_of(s.item_search_suggestions(ItemSearchRequest(query=""))) == [
        item.path for item in index
    ]
    assert sorted(item.path for item in index) == [
        "first/00000/00000",
        "first/00000/00001",
        "second/00000/00000",
    ]
    assert all(item.slug for item in index)
    assert [item.num for item in index if item.repo == "first"] == [0, 1]


def test_suggestions_head_anchored(compare_workspace):
    s = Server(compare_workspace.get_root())

    assert sorted(
        paths_of(s.item_search_suggestions(ItemSearchRequest(query="fir")))
    ) == [
        "first/00000/00000",
        "first/00000/00001",
    ]
    assert paths_of(
        s.item_search_suggestions(ItemSearchRequest(query="first/00000/00001"))
    ) == ["first/00000/00001"]


def test_suggestions_tail_anchored(compare_workspace):
    s = Server(compare_workspace.get_root())

    assert paths_of(
        s.item_search_suggestions(ItemSearchRequest(query="00000/00001"))
    ) == ["first/00000/00001"]
    # A bare number matches model names, but not the line with the same name
    assert sorted(
        paths_of(s.item_search_suggestions(ItemSearchRequest(query="00000")))
    ) == [
        "first/00000/00000",
        "second/00000/00000",
    ]


def test_suggestions_do_not_match_mid_segment(compare_workspace):
    s = Server(compare_workspace.get_root())

    assert s.item_search_suggestions(ItemSearchRequest(query="irst/00000")).total == 0
    assert s.item_search_suggestions(ItemSearchRequest(query="0000/00001")).total == 0


def test_suggestions_match_slug_substring(compare_workspace):
    s = Server(compare_workspace.get_root())

    slug = s._get_item_index()[0].slug
    middle = slug.split("_")[1]

    suggestions = s.item_search_suggestions(ItemSearchRequest(query=middle))

    assert slug in [item.slug for item in suggestions.items]


def test_suggestions_limit_keeps_total(compare_workspace):
    s = Server(compare_workspace.get_root())

    suggestions = s.item_search_suggestions(ItemSearchRequest(query="", limit=2))

    assert len(suggestions.items) == 2
    assert suggestions.total == 3


def test_compare_resolves_slug_path_and_num(compare_workspace):
    s = Server(compare_workspace.get_root())
    slug = s._resolve_item("first/00000/00001").slug

    response = s.compare_item_table(
        CompareRequest(items=[slug, "second/00000/00000", "first/00000/0"])
    )

    assert [column.path for column in response.columns] == [
        "first/00000/00001",
        "second/00000/00000",
        "first/00000/00000",
    ]
    # The identifier is echoed back as requested so the UI can round-trip the URL
    assert response.columns[0].id == slug
    assert response.columns[2].id == "first/00000/0"
    assert response.not_found == []


def test_slugless_model_stays_usable(compare_workspace):
    """
    A model whose SLUG file failed to be written is still a model. It must not
    take down the index for the whole workspace
    """

    root = compare_workspace.get_root()
    os.remove(os.path.join(root, "first", "00000", "00001", "SLUG"))

    s = Server(root)

    suggestions = s.item_search_suggestions(ItemSearchRequest(query=""))
    assert "first/00000/00001" in paths_of(suggestions)
    assert suggestions.total == 3

    slugless = [item for item in suggestions.items if item.path == "first/00000/00001"][0]
    assert slugless.slug is None
    assert slugless.num == 1

    # It has no slug to be addressed by, so the path has to keep working
    response = s.compare_item_table(CompareRequest(items=["first/00000/00001"]))
    assert response.not_found == []
    assert response.columns[0].slug is None
    assert response.columns[0].num == 1


def test_items_that_are_not_models_are_skipped(compare_workspace):
    root = compare_workspace.get_root()
    os.makedirs(os.path.join(root, "first", "00000", "not_a_model"))

    s = Server(root)

    assert "first/00000/not_a_model" not in paths_of(
        s.item_search_suggestions(ItemSearchRequest(query=""))
    )


def test_compare_resolves_slug_case_insensitively(compare_workspace):
    """
    Slugs come from a lowercase wordlist, so a hand typed URL should still work
    """

    s = Server(compare_workspace.get_root())
    slug = s._resolve_item("first/00000/00000").slug

    response = s.compare_item_table(CompareRequest(items=[slug.upper()]))

    assert response.not_found == []
    assert response.columns[0].path == "first/00000/00000"


def test_compare_keeps_paths_case_sensitive(compare_workspace):
    """
    Unlike slugs, paths are directory names where the case is meaningful
    """

    s = Server(compare_workspace.get_root())

    response = s.compare_item_table(CompareRequest(items=["FIRST/00000/00000"]))

    assert response.columns == []
    assert response.not_found == ["FIRST/00000/00000"]


def test_compare_reports_available_fields_per_column(compare_workspace):
    """
    The client rebuilds the row picker from the columns it holds, so each one
    has to carry its own fields and not just the union
    """

    s = Server(compare_workspace.get_root())

    response = s.compare_item_table(
        CompareRequest(items=["first/00000/00000", "second/00000/00000"])
    )

    first, second = response.columns
    assert "params.lr" in first.available_fields
    assert "params.lr" not in second.available_fields
    assert "params.momentum" in second.available_fields

    union = set(first.available_fields) | set(second.available_fields)
    assert union == set(response.item_fields)


def test_compare_reports_not_found(compare_workspace):
    s = Server(compare_workspace.get_root())

    response = s.compare_item_table(
        CompareRequest(items=["no_such_slug", "first/00000/00000"])
    )

    assert response.not_found == ["no_such_slug"]
    assert len(response.columns) == 1


def test_compare_data_line_items_are_not_comparable(compare_workspace):
    s = Server(compare_workspace.get_root())

    response = s.compare_item_table(CompareRequest(items=["second/00001/00000"]))

    assert response.columns == []
    assert response.not_found == ["second/00001/00000"]


def test_compare_base_fields_and_field_union(compare_workspace):
    s = Server(compare_workspace.get_root())

    response = s.compare_item_table(
        CompareRequest(
            items=["first/00000/00000", "second/00000/00000"],
            item_fields=["params.lr", "params.batch_size"],
        )
    )

    for column in response.columns:
        assert set(column.meta).issuperset(
            {"name", "slug", "tags", "created_at", "saved_at"}
        )

    assert response.columns[0].meta["name"] == "00000"
    assert response.columns[0].meta["params.lr"] == 0.1
    assert response.columns[0].meta["params.batch_size"] == 32
    # Requested for every column, missing ones come back as None
    assert response.columns[1].meta["params.lr"] is None

    # The union spans both models even though neither has all of the params
    assert {"params.lr", "params.batch_size", "params.momentum"}.issubset(
        response.item_fields
    )
