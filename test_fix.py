"""
Test the fixed temperature converter.
"""

from rh import MeshBuilder
import tempfile


def test_fixed_app():
    """Test the temperature converter with the validator fix."""
    print("🔧 Testing Fixed Temperature Converter...")

    # Same configuration as user's example
    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
    }

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    initial_values = {"temp_celsius": 20.0}

    # Create and build the app
    builder = MeshBuilder(mesh_spec, functions_spec, initial_values)

    with tempfile.TemporaryDirectory() as tmpdir:
        builder.output_dir = tmpdir
        app_path = builder.build_app(title="Fixed Temperature Converter")

        print(f"📱 Fixed app created at: {app_path}")

        # Check the validator fix
        html_content = app_path.read_text()

        if "const validator = validator;" in html_content:
            print("❌ Circular validator reference still present")
        elif "const validator = JSONSchemaForm.validator.ajv8;" in html_content:
            print("✅ Validator reference fixed")
        else:
            print("⚠️ Validator reference changed to something else")

        # Look for other potential issues
        print("\n🔍 JavaScript Analysis:")

        # Check if all necessary components are present
        checks = [
            ("Form constant", "const Form = JSONSchemaForm.default;" in html_content),
            ("Validator fix", "JSONSchemaForm.validator.ajv8" in html_content),
            ("FormConfig", "const formConfig = " in html_content),
            ("onChange handler", "const onChange = " in html_content),
            ("renderForm function", "function renderForm(" in html_content),
            ("Initial render call", "renderForm();" in html_content),
        ]

        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")

        print(f"\n🌐 Test this URL in your browser:")
        print(f"   file://{app_path}")
        print("\n💡 If you still see a white page:")
        print("   1. Open browser console (F12)")
        print("   2. Look for JavaScript errors in the Console tab")
        print("   3. Check the Network tab to see if CDN resources are loading")

        return app_path


if __name__ == "__main__":
    test_fixed_app()
