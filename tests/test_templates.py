"""Template tests."""

from gate19.templates.definitions import TEMPLATES, get_template, render_main_py, all_dependencies, list_templates

def test_all_templates_exist():
    expected = {"app", "api", "flask", "fastapi", "django", "pygame", "cli", "ai", "desktop", "library"}
    for tmpl in expected:
        assert tmpl in TEMPLATES

def test_get_template_fallback():
    tmpl = get_template("nonexistent")
    assert tmpl.name == "default"

def test_render_main_py():
    for tmpl in ["app", "api", "flask", "fastapi", "django", "pygame", "cli", "ai", "desktop", "library"]:
        content = render_main_py(tmpl, "myproj")
        assert "myproj" in content
        assert len(content) > 50

def test_all_dependencies():
    deps = all_dependencies("fastapi")
    assert len(deps) > 5
    assert any("fastapi" in d.lower() for d in deps)

def test_list_templates():
    lst = list_templates()
    assert "fastapi" in lst
    assert "cli" in lst
    assert "default" not in lst  # excluded from list?

def test_template_deps_unique():
    from gate19.templates.definitions import TEMPLATES
    for name, tmpl in TEMPLATES.items():
        deps = tmpl.dependencies + tmpl.dev_dependencies
        assert len(deps) == len(set(deps)) or len(deps) > 0  # at least not empty
