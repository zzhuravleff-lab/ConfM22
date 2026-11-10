import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.main import validate, DEFAULTS


def base():
    return {**DEFAULTS,
            "package": "pkg", "repo": "https://x", "test_mode": False,
            "version": "1.0.0", "output": "g.png", "max_depth": 3, "filter": ""}


def test_ok():
    assert validate(base()) == []


def test_bad():
    c = base()
    c.update(package="", repo=1, test_mode="x", version="", output="g.svg",
             max_depth=0, filter=[1])
    errs = validate(c)
    assert len(errs) == 7