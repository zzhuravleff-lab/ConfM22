"""Загрузка и валидация YAML-конфигурации."""
from pathlib import Path

import yaml

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

    test_mode_valid = isinstance(cfg["test_mode"], bool)
    if not test_mode_valid:
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

    if test_mode_valid and cfg["test_mode"]:
        if not isinstance(repo, str) or not Path(repo).is_file():
            errors.append(f"repo: в тестовом режиме файл не найден: {repo}")

    return errors


def print_params(cfg):
    print("Параметры конфигурации:")
    for k, v in cfg.items():
        print(f"  {k} = {v}")