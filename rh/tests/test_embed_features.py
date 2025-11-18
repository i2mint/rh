"""Tests for embed_react and embed_rjsf features."""

import tempfile
from pathlib import Path
from rh import MeshBuilder


def test_embed_react_removes_cdn_links():
    """Test that embed_react=True removes CDN links and embeds React inline."""
    mesh_spec = {"y": ["x"]}
    functions_spec = {"y": "return x * 2;"}
    initial_values = {"x": 5}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        # Build with embed_react=True
        app_path = builder.build_app(title="Embed Test", embed_react=True)
        with open(app_path) as f:
            content = f.read()

        # Should NOT contain CDN links
        assert "unpkg.com/react@17" not in content
        assert "unpkg.com/react-dom@17" not in content
        assert "cdnjs.cloudflare.com/ajax/libs/bootstrap" not in content

        # Should contain embedded React (check for React license comment)
        assert "/** @license React" in content

        # Should be significantly larger than non-embedded version
        assert len(content) > 100000  # React + ReactDOM is ~130KB


def test_embed_react_false_uses_cdn():
    """Test that embed_react=False uses CDN links."""
    mesh_spec = {"y": ["x"]}
    functions_spec = {"y": "return x * 2;"}
    initial_values = {"x": 5}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        # Build with embed_react=False (default)
        app_path = builder.build_app(title="CDN Test", embed_react=False)
        with open(app_path) as f:
            content = f.read()

        # Should contain CDN links
        assert "unpkg.com/react@17" in content
        assert "unpkg.com/react-dom@17" in content
        assert "cdnjs.cloudflare.com/ajax/libs/bootstrap" in content

        # Should NOT contain embedded React
        assert "/** @license React" not in content

        # Should be smaller
        assert len(content) < 50000


def test_embed_react_skips_rjsf_cdn():
    """Test that embed_react=True skips RJSF CDN and uses fallback."""
    mesh_spec = {"y": ["x"]}
    functions_spec = {"y": "return x * 2;"}
    initial_values = {"x": 5}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app(title="Fallback Test", embed_react=True)
        with open(app_path) as f:
            content = f.read()

        # Should NOT load RJSF from CDN
        assert "react-jsonschema-form" not in content or "RJSF skipped for offline mode" in content

        # Should have SimpleFormComponent fallback
        assert "window.SimpleFormComponent" in content


def test_inline_css_when_embed_react():
    """Test that embed_react=True includes inline CSS instead of Bootstrap CDN."""
    mesh_spec = {"y": ["x"]}
    functions_spec = {"y": "return x * 2;"}
    initial_values = {"x": 5}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app(title="CSS Test", embed_react=True)
        with open(app_path) as f:
            content = f.read()

        # Should have inline CSS styles
        assert ".form-control" in content
        assert ".btn-primary" in content
        assert ".mesh-form-container" in content

        # Should NOT have Bootstrap CDN link
        assert "cdnjs.cloudflare.com/ajax/libs/bootstrap" not in content


def test_both_embed_flags_together():
    """Test using both embed_react and embed_rjsf together."""
    mesh_spec = {"y": ["x"]}
    functions_spec = {"y": "return x * 2;"}
    initial_values = {"x": 5}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        # Build with both flags (if rjsf-umd.js exists, it would be embedded)
        app_path = builder.build_app(
            title="Both Flags Test", embed_react=True, embed_rjsf=True
        )
        with open(app_path) as f:
            content = f.read()

        # Should have embedded React
        assert "/** @license React" in content

        # Should NOT have React CDN links
        assert "unpkg.com/react@17" not in content


def test_generated_html_is_valid_with_embed():
    """Test that generated HTML with embed_react is valid and complete."""
    mesh_spec = {"output": ["input"]}
    functions_spec = {"output": "return input.toUpperCase();"}
    initial_values = {"input": "hello"}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app(title="Valid HTML Test", embed_react=True)
        with open(app_path) as f:
            content = f.read()

        # Check HTML structure
        assert content.startswith("<!DOCTYPE html>")
        assert "<html" in content
        assert "</html>" in content
        assert "<head>" in content
        assert "</head>" in content
        assert "<body>" in content
        assert "</body>" in content

        # Check essential components
        assert "<title>Valid HTML Test</title>" in content
        assert 'id="rjsf-form"' in content
        assert "meshFunctions" in content
        assert "meshConfig" in content

        # Check that all placeholders were replaced
        assert "__TITLE__" not in content
        assert "__CSS_TAG__" not in content
        assert "__REACT_TAGS__" not in content
        assert "__VENDOR_SCRIPT_TAG__" not in content
        assert "__MESH_FUNCTIONS__" not in content
        assert "__MESH_PROPAGATOR__" not in content
        assert "__APP_INITIALIZATION__" not in content
