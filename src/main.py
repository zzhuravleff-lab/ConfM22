"""Визуализатор графа зависимостей пакетов (.NET/NuGet). Этап 2."""
import argparse
import sys

try:
    import yaml  # noqa: F401  # проверка, что зависимость установлена
except ImportError:
    print("Ошибка: нужен PyYAML. Установите: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from src.config import load_config, print_params, validate
from src.nuget import direct_dependencies


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="src.main",
        description="Граф зависимостей пакетов .NET (NuGet), этап 2",
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

    try:
        deps = direct_dependencies(cfg["repo"], cfg["package"], cfg["version"])
    except Exception as e:
        print(f"Ошибка получения зависимостей: {e}", file=sys.stderr)
        return 3

    print(f"Прямые зависимости пакета {cfg['package']} "
          f"{cfg['version']}:")
    if not deps:
        print("  (нет)")
    for dep_id, dep_ver in deps:
        suffix = f" {dep_ver}" if dep_ver else ""
        print(f"  - {dep_id}{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())