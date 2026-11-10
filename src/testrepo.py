"""Чтение тестового репозитория: файл с рёбрами 'A B' (A зависит от B)."""
from pathlib import Path


def read_edges(path):
    """Читает файл рёбер и возвращает dict: node -> [deps]."""
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"Тестовый репозиторий не найден: {path}")
    graph = {}
    for lineno, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(
                f"{path}:{lineno}: ожидается 'A B', получено: {raw!r}"
            )
        src, dst = parts
        for tag in (src, dst):
            if not (len(tag) == 1 and tag.isupper() and tag.isalpha()):
                raise ValueError(
                    f"{path}:{lineno}: '{tag}' не одиночная заглавная буква"
                )
        graph.setdefault(src, []).append(dst)
        graph.setdefault(dst, [])
    return graph