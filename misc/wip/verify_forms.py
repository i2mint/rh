#!/usr/bin/env python3
"""
Simple test to verify the RH framework generates working forms.
"""

from rh import MeshBuilder


def main():
    print("🧪 Testing RH Framework Form Generation...")

    # Create a simple temperature converter
    mesh_spec = {"temp_fahrenheit": ["temp_celsius"], "temp_kelvin": ["temp_celsius"]}

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    initial_values = {"temp_celsius": 20.0}

    ui_conventions = {
        "temp_fahrenheit": {"ui:readonly": True},
        "temp_kelvin": {"ui:readonly": True},
    }

    # Build the app
    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
        field_overrides=ui_conventions,
    )

    app_path = builder.build_app(
        title="Temperature Converter Test", app_name="temp_test"
    )

    print(f"✅ App generated: {app_path}")
    print(f"📄 File size: {app_path.stat().st_size} bytes")

    # Check HTML content
    html_content = app_path.read_text()

    checks = {
        "Has React": "react" in html_content.lower(),
        "Has Form Component": (
            "SimpleFormComponent" in html_content or "JSONSchemaForm" in html_content
        ),
        "Has Mesh Functions": "meshFunctions" in html_content,
        "Has Temperature Functions": "temp_celsius * 9/5 + 32" in html_content,
        "Has Bootstrap": "bootstrap" in html_content,
        "Has Error Handling": "alert alert-danger" in html_content,
    }

    print("\n🔍 Content Checks:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    all_passed = all(checks.values())
    print(f"\n{'🎉 All checks passed!' if all_passed else '⚠️ Some checks failed'}")

    print(f"\n💡 Open {app_path} in a web browser to test the interactive form!")

    return app_path


if __name__ == "__main__":
    main()
