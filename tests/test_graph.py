import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.graph import build_graph
from src.testrepo import read_edges


def make_fetch(graph):
    return lambda pkg: [(c, "") for c in graph.get(pkg, [])]


def test_linear_depth():
    g = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
    nodes, edges = build_graph(make_fetch(g), "A", max_depth=2, flt="")
    assert set(nodes) == {"a", "b", "c"}
    assert ("a", "b") in edges and ("b", "c") in edges
    assert ("c", "d") not in edges


def test_cycle_terminates():
    g = {"A": ["B"], "B": ["C"], "C": ["A"]}
    nodes, edges = build_graph(make_fetch(g), "A", max_depth=10, flt="")
    assert set(nodes) == {"a", "b", "c"}
    assert ("c", "a") not in edges  """ обратное ребро в корень не добавляем """


def test_filter():
    g = {"A": ["B", "C"], "B": ["D"], "C": ["E"]}
    nodes, edges = build_graph(make_fetch(g), "A", max_depth=5, flt="B")
    assert set(nodes) == {"a", "c", "e"}


def test_diamond_visited_once():
    g = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    nodes, edges = build_graph(make_fetch(g), "A", max_depth=5, flt="")
    assert [e for e in edges if e[1] == "d"].__len__() == 1


def test_testrepo_read(tmp_path=None):
    """можно не использовать tmp_path, а положить файл-фикстуру рядом"""
    g = read_edges("tests/fixtures/linear.txt")
    assert g == {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}