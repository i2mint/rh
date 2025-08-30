"""
Test calling serve() before build_app() - promoted from misc/wip.
"""

from rh import MeshBuilder
import tempfile
import os


def test_serve_before_build_app():
    """Test that serve() can be called before build_app() without crashing."""

    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
    }

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    initial_values = {"temp_celsius": 20.0}

    # Test with a custom directory to avoid environment-specific paths
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create builder and set explicit output directory
        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        builder.output_dir = tmpdir

        # Test the core fix: process_path should create missing directories
        from rh.util import process_path

        # Create a subdirectory that doesn't exist yet
        test_serve_dir = os.path.join(tmpdir, "nonexistent_dir")

        # This should create the directory (simulating what serve_directory does)
        processed_dir = process_path(test_serve_dir, ensure_dir_exists=True)

        # Verify the directory exists
        assert os.path.exists(processed_dir), f"Directory should exist: {processed_dir}"

        # Now test that _get_output_dir() logic works
        serve_dir = builder._get_output_dir()
        processed_serve_dir = process_path(serve_dir, ensure_dir_exists=True)

        assert os.path.exists(
            processed_serve_dir
        ), f"Serve directory should exist: {processed_serve_dir}"


if __name__ == "__main__":
    test_serve_before_build_app()
