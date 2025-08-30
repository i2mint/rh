"""
Test the new app directory functionality. Promoted from misc/wip.
"""

import tempfile
import os
from pathlib import Path
from rh import MeshBuilder


def test_app_directory_naming():
    """Test that apps are created with proper naming in RH_APP_FOLDER."""
    mesh_spec = {"output": ["input"]}
    functions_spec = {"output": "return input;"}

    builder = MeshBuilder(mesh_spec=mesh_spec, functions_spec=functions_spec)

    # Test app name inference from title
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override environment variable for this test
        original_env = os.environ.get("RH_APP_FOLDER")
        os.environ["RH_APP_FOLDER"] = tmpdir

        try:
            # Reload util to pick up env change
            import importlib
            import rh.util

            importlib.reload(rh.util)

            # Test title inference
            app_path = builder.build_app(title="Temperature Converter")
            expected_path = Path(tmpdir) / "temperature_converter" / "index.html"
            assert app_path == expected_path
            assert app_path.exists()

            # Test explicit app name
            app_path2 = builder.build_app(title="My App", app_name="custom_name")
            expected_path2 = Path(tmpdir) / "custom_name" / "index.html"
            assert app_path2 == expected_path2
            assert app_path2.exists()

            # Test default app name
            builder2 = MeshBuilder(mesh_spec=mesh_spec, functions_spec=functions_spec)
            app_path3 = builder2.build_app()  # Default title "Mesh App"
            expected_path3 = Path(tmpdir) / "mesh_app" / "index.html"
            assert app_path3 == expected_path3
            assert app_path3.exists()

        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["RH_APP_FOLDER"] = original_env
            elif "RH_APP_FOLDER" in os.environ:
                del os.environ["RH_APP_FOLDER"]

            # Reload to reset to original state
            importlib.reload(rh.util)


def test_output_dir_override():
    """Test that explicit output_dir overrides app directory logic."""
    mesh_spec = {"output": ["input"]}
    functions_spec = {"output": "return input;"}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(mesh_spec=mesh_spec, functions_spec=functions_spec)
        builder.output_dir = tmpdir

        app_path = builder.build_app(title="Test App")
        expected_path = Path(tmpdir) / "index.html"
        assert app_path == expected_path
        assert app_path.exists()


if __name__ == "__main__":
    test_app_directory_naming()
    test_output_dir_override()
    print("\u2705 All app directory tests passed!")
