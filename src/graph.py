"""Обход графа зависимостей: BFS с рекурсией, с учётом глубины/фильтра/циклов."""


def _normalize(name):
    return name.lower()


def _matches_filter(pkg, flt):
    """True, если пакет надо исключить из анализа."""
    return bool(flt) and flt.lower() in pkg.lower()


def build_graph(fetch, root, max_depth, flt):
    """Возвращает (nodes, edges).

    nodes — dict lowercase_id -> original_id (что печатать).
    edges — список (parent_lower, child_lower).
    fetch(pkg) — функция, возвращающая [(id, version_spec), ...].
    Корень включаем всегда. max_depth — предел глубины: 0..max_depth.
    """
    root_key = _normalize(root)
    nodes = {root_key: root}
    edges = []
    visited = {root_key}

    def bfs_recursive(frontier, depth):
        """ depth — сколько рёбер уже пройдено до текущего уровня."""
        """ Раскрываем frontier, только если ещё есть куда идти. """
        if depth >= max_depth or not frontier:
            return
        next_frontier = []
        for key, orig in frontier:
            for child_id, _spec in fetch(orig):
                child_key = _normalize(child_id)
                if _matches_filter(child_id, flt) and child_key != root_key:
                    continue
                if child_key in visited:
                    continue
                visited.add(child_key)
                nodes[child_key] = child_id
                edges.append((key, child_key))
                next_frontier.append((child_key, child_id))
        """ РЕКУРСИЯ: следующий уровень """
        bfs_recursive(next_frontier, depth + 1)

    bfs_recursive([(root_key, root)], depth=0)
    return nodes, edges