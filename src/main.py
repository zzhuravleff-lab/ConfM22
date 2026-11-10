"""Визуализатор графа зависимостей пакетов (.NET/NuGet). Этап 3."""
import argparse
import sys

try:
    import yaml  # noqa: F401
except ImportError:
    print("Ошибка: нужен PyYAML. Установите: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from src import testrepo
from src.config import load_config, print_params, validate
from src.graph import build_graph
from src.nuget import direct_dependencies

_VERSION_MIN_CHARS = "0123456789"


def _min_version(spec):
    """'[8.0.0, )' -> '8.0.0'; '13.0.3' -> '13.0.3'. Best-effort."""
    if not spec:
        return ""
    spec = spec.strip()
    if spec[0] in "([":
        inside = spec[1:-1] if spec[-1] in ")]" else spec[1:]
        first = inside.split(",")[0].strip()
        return first
    return spec


def _fetch_from_test(graph, pkg):
    deps = graph.get(pkg, [])
    return [(d, "") for d in deps]


def _fetch_from_nuget(cfg, pkg, ver):
    return direct_dependencies(cfg["repo"], pkg, ver)


def _make_fetch(cfg, test_graph, root_ver):
    """Возвращает единую функцию fetch(pkg) -> [(id, version_spec)]."""
    if test_graph is not None:
        return lambda pkg: _fetch_from_test(test_graph, pkg)

    """ Для следующих уровней версию берём из возвращённого spec, """
    """ для корня — из конфига. """
    root_key = cfg["package"].lower()

    def fetch(pkg):
        if pkg.lower() == root_key:
            ver = root_ver
        else:
            """ при первом обращении ещё нет spec — увидим ниже через кеш """
            ver = _KNOWN_VERSIONS.get(pkg.lower(), "")
        return _fetch_from_nuget(cfg, pkg, ver)

    return fetch


""" кеш версий, заполняется по мере обхода (ниже, в fetch wrapper’е) """
_KNOWN_VERSIONS = {}


def _wrap_versions(cfg, test_graph):
    """Обёртка, которая запоминает версии и умеет резолвить их по пакету."""
    root = cfg["package"]
    root_ver = cfg["version"]

    if test_graph is not None:
        return lambda pkg: _fetch_from_test(test_graph, pkg)

    _KNOWN_VERSIONS[root.lower()] = root_ver

    def fetch(pkg):
        ver = _KNOWN_VERSIONS.get(pkg.lower(), "")
        deps = _fetch_from_nuget(cfg, pkg, ver)
        for child_id, spec in deps:
            key = child_id.lower()
            if key not in _KNOWN_VERSIONS:
                _KNOWN_VERSIONS[key] = _min_version(spec) or ver
        return deps

    return fetch


def _print_graph(root, nodes, edges):
    print(f"Граф зависимостей пакета {root}:")
    if len(nodes) == 1 and not edges:
        print("  (нет зависимостей в пределах заданных параметров)")
        return
    children = {}
    for parent, child in edges:
        children.setdefault(parent, []).append(child)

    def walk(key, depth, seen):
        indent = "  " * depth
        name = nodes[key]
        print(f"{indent}- {name}")
        for c in children.get(key, []):
            if c in seen:
                print(f"{indent}  - {nodes[c]} (цикл)")
                continue
            walk(c, depth + 1, seen | {c})

    walk(root.lower(), 0, {root.lower()})


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="src.main",
        description="Граф зависимостей пакетов .NET (NuGet), этап 3",
    )
    ap.add_argument("-c", "--config", default="config.yaml",
                    help="путь к YAML-конфигу (по умолчанию config.yaml)")
    args = ap.parse_args(argv)

    try:
        cfg = load_config(args.config)
    except ValueError as e:
        print(f"Ошибка конфигурации: {e}", file=sys.stderr)
        return 2

    errors = validate(cfg)
    if errors:
        print("Ошибки в параметрах:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 2

    print_params(cfg)
    print()

    test_graph = None
    if cfg["test_mode"]:
        try:
            test_graph = testrepo.read_edges(cfg["repo"])
        except ValueError as e:
            print(f"Ошибка тестового репозитория: {e}", file=sys.stderr)
            return 3

    fetch = _wrap_versions(cfg, test_graph)

    try:
        nodes, edges = build_graph(
            fetch=fetch,
            root=cfg["package"],
            max_depth=cfg["max_depth"],
            flt=cfg["filter"] or "",
        )
    except Exception as e:
        print(f"Ошибка получения зависимостей: {e}", file=sys.stderr)
        return 3

    _print_graph(cfg["package"], nodes, edges)
    return 0


if __name__ == "__main__":
    sys.exit(main())