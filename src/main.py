"""Визуализатор графа зависимостей пакетов (.NET/NuGet). Этап 1."""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Ошибка: нужен PyYAML. Установите: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

MIN_DEPTH = 1
OUTPUT_EXT = ".png"
DEFAULTS = {
    "package": None,
    "repo": None,
    "test_mode": False,
    "version": None,
    "output": None,
    "max_depth": None,
    "filter": None,
}


def load_config(path):
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"Файл конфигурации не найден: {path}")
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ValueError(f"Ошибка разбора YAML: {e}")
    if not isinstance(data, dict):
        raise ValueError("Конфигурация должна быть YAML-словарём")
    unknown = set(data) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"Неизвестные ключи конфигурации: {sorted(unknown)}")
    return {**DEFAULTS, **data}


def validate(cfg):
    """Проверяет все настраиваемые параметры, возвращает список ошибок."""
    errors = []

    pkg = cfg["package"]
    if not isinstance(pkg, str) or not pkg.strip():
        errors.append("package: должно быть непустой строкой")

    repo = cfg["repo"]
    if not isinstance(repo, str) or not repo.strip():
        errors.append("repo: должно быть непустой строкой (URL или путь)")

    if not isinstance(cfg["test_mode"], bool):
        errors.append("test_mode: должно быть true или false")

    ver = cfg["version"]
    if not isinstance(ver, str) or not ver.strip():
        errors.append("version: должно быть непустой строкой (например, 1.0.0)")

    out = cfg["output"]
    if not isinstance(out, str) or not out.strip():
        errors.append("output: должно быть непустой строкой (имя файла)")
    elif Path(out).suffix.lower() != OUTPUT_EXT:
        errors.append(f"output: имя файла должно иметь расширение {OUTPUT_EXT}")

    depth = cfg["max_depth"]
    if not isinstance(depth, int) or isinstance(depth, bool) or depth < MIN_DEPTH:
        errors.append(f"max_depth: должно быть целым числом >= {MIN_DEPTH}")

    flt = cfg["filter"]
    if flt is not None and not isinstance(flt, str):
        errors.append("filter: должно быть строкой или null")

    if cfg["test_mode"] and not Path(str(repo)).is_file():
        errors.append(f"repo: в тестовом режиме файл не найден: {repo}")

    return errors


def print_params(cfg):
    print("Параметры конфигурации:")
    for k, v in cfg.items():
        print(f"  {k} = {v}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="src.main",
        description="Визуализатор графа зависимостей пакетов (.NET/NuGet), этап 1",
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
    return 0


if __name__ == "__main__":
    sys.exit(main())