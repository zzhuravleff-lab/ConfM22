import io
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import nuget

NUSPEC = b"""<?xml version="1.0"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>Test.Pkg</id>
    <version>1.0.0</version>
    <dependencies>
      <group targetFramework="netstandard2.0">
        <dependency id="Newtonsoft.Json" version="13.0.0"/>
        <dependency id="System.Text.Json" version="8.0.0"/>
      </group>
      <group targetFramework="net472">
        <dependency id="Newtonsoft.Json" version="12.0.0"/>
      </group>
    </dependencies>
  </metadata>
</package>
"""


def make_nupkg(nuspec):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("Test.Pkg.nuspec", nuspec)
    return buf.getvalue()


def test_parse_nuspec_dedups():
    deps = nuget._parse_nuspec(NUSPEC)
    assert deps == [
        ("Newtonsoft.Json", "13.0.0"),
        ("System.Text.Json", "8.0.0"),
    ]


def test_extract_nuspec():
    xml = nuget._extract_nuspec_from_nupkg(make_nupkg(NUSPEC), "Test.Pkg")
    assert b"Newtonsoft.Json" in xml


def test_direct_dependencies_offline():
    index = {
        "resources": [
            {"@type": "PackageBaseAddress/3.0.0",
             "@id": "https://example.test/flat/"},
        ]
    }
    nupkg = make_nupkg(NUSPEC)

    def fake_get(url):
        if url.endswith("index.json"):
            import json
            return json.dumps(index).encode()
        return nupkg

    with patch.object(nuget, "_http_get", side_effect=fake_get):
        deps = nuget.direct_dependencies(
            "https://example.test/index.json", "Test.Pkg", "1.0.0"
        )
    assert [d[0] for d in deps] == ["Newtonsoft.Json", "System.Text.Json"]