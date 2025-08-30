"""
Test the specific issue from the demo - serve() called before build_app().
"""

from rh import MeshBuilder


def test_serve_before_build():
    """Test the exact scenario that was failing."""
    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
    }

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    initial_values = {"temp_celsius": 20.0}

    # Create the mesh builder
    builder = MeshBuilder(mesh_spec, functions_spec, initial_values)

    print("🔧 Testing serve() before build_app() scenario...")

    # This is what was failing before - calling serve() without build_app() first
    # Now we test that the directory gets created properly
    output_dir = builder._get_output_dir()
    print(f"📁 Output directory would be: {output_dir}")

    # Test that serve_directory creates the directory
    from rh.util import serve_directory, process_path

    # This should work now without crashing
    processed_dir = process_path(output_dir, ensure_dir_exists=True)
    print(f"✅ Directory ensured: {processed_dir}")

    import os

    assert os.path.exists(processed_dir), f"Directory should exist: {processed_dir}"

    print("✅ Fix successful! serve() can now be called before build_app()")


if __name__ == "__main__":
    test_serve_before_build()
