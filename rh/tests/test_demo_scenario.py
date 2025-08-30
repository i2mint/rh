"""
Test the exact demo scenario to ensure the fix works. Promoted from misc/wip.
"""

from rh import MeshBuilder
import tempfile
import os
from rh.util import process_path


def test_demo_scenario():
    """Test the exact scenario from the demo that was failing."""
    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
    }

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    initial_values = {"temp_celsius": 20.0}

    # Create the mesh builder (same as demo)
    builder = MeshBuilder(mesh_spec, functions_spec, initial_values)

    # Use temp directory for testing (as suggested in the original requirements)
    with tempfile.TemporaryDirectory() as tmpdir:
        builder.output_dir = tmpdir

        # Build the app
        app_path = builder.build_app(title="Temperature Converter")

        # Get the directory that serve() would try to use
        serve_dir = tmpdir  # This is what builder.serve() would try to serve

        # This should not fail now
        processed_dir = process_path(serve_dir, ensure_dir_exists=True)

        # Verify directory exists and has the app
        assert os.path.exists(processed_dir)
        assert os.path.exists(app_path)


if __name__ == "__main__":
    test_demo_scenario()
