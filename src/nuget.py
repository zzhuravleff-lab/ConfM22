"""Извлечение прямых зависимостей пакета из репозитория NuGet (V3)."""
import io
import json
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

USER_AGENT = "config-management-course/1.0"
TIMEOUT = 15


def _http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def _service_index(index_url):
    """Скачивает V3 index.json и возвращает URL PackageBaseAddress."""
    data = json.loads(_http_get(index_url).decode("utf-8"))
    for res in data.get("resources", []):
        if res.get("@type") == "PackageBaseAddress/3.0.0":
            return res["@id"].rstrip("/")
    raise ValueError("В индексе NuGet не найден PackageBaseAddress/3.0.0")


def _package_url(base_url, package_id, version):
    pid = package_id.lower()
    ver = version.lower()
    return f"{base_url}/{pid}/{ver}/{pid}.{ver}.nupkg"


def _parse_nuspec(xml_bytes):
    """Возвращает список (id, version) прямых зависимостей из .nuspec."""
    root = ET.fromstring(xml_bytes)
    deps = []
    # Пространства имён в nuspec бывают и с префиксом, и без — обходим локально.
    for dep in root.iter():
        if dep.tag.split("}")[-1] != "dependency":
            continue
        dep_id = dep.get("id")
        dep_ver = dep.get("version", "")
        if dep_id:
            deps.append((dep_id, dep_ver))
    # Убираем дубликаты, сохраняя порядок.
    seen = set()
    out = []
    for d in deps:
        if d[0] not in seen:
            seen.add(d[0])
            out.append(d)
    return out


def _extract_nuspec_from_nupkg(nupkg_bytes, package_id):
    """Достаёт XML .nuspec из ZIP-архива .nupkg."""
    with zipfile.ZipFile(io.BytesIO(nupkg_bytes)) as zf:
        candidates = [
            n for n in zf.namelist()
            if n.lower().endswith(".nuspec") and "/" not in n
        ]
        if not candidates:
            raise ValueError("В .nupkg не найден .nuspec")
        """ NuGet кладёт .nuspec с именем пакета; на всякий случай берём совпадение. """
        want = package_id.lower() + ".nuspec"
        target = next(
            (c for c in candidates if c.lower() == want),
            candidates[0],
        )
        return zf.read(target)


def direct_dependencies(index_url, package_id, version):
    """Возвращает список (id, version_spec) прямых зависимостей пакета."""
    base = _service_index(index_url)
    nupkg_url = _package_url(base, package_id, version)
    nupkg = _http_get(nupkg_url)
    xml = _extract_nuspec_from_nupkg(nupkg, package_id)
    return _parse_nuspec(xml)