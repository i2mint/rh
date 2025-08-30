"""
Manual test script to verify the actual output of the RH framework.

This script generates a sample app and displays the actual HTML to verify
it contains the expected interactive functionality.
"""

from rh import MeshBuilder
import tempfile
from pathlib import Path


def main():
    print("🧪 Manual Test: Verifying Generated HTML")
    print("=" * 50)

    # Create a simple test case
    mesh_spec = {
        "fahrenheit": ["celsius"],
        "kelvin": ["celsius"],
        "area": ["radius"],
        "slider_size": [],
        "readonly_summary": ["area", "slider_size"],
    }

    functions_spec = {
        "fahrenheit": "return celsius * 9/5 + 32;",
        "kelvin": "return celsius + 273.15;",
        "area": "return Math.PI * radius * radius;",
        "readonly_summary": "return `Area: ${area.toFixed(2)}, Size: ${slider_size}`;",
    }

    initial_values = {"celsius": 20.0, "radius": 5.0, "slider_size": 50}

    field_overrides = {
        "celsius": {
            "title": "Temperature (°C)",
            "ui:help": "Enter temperature in Celsius",
        },
        "radius": {"title": "Circle Radius", "minimum": 0, "maximum": 100},
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            field_overrides=field_overrides,
            output_dir=tmpdir,
        )

        print("📊 Generated Configuration:")
        config = builder.generate_config()

        print(f"  Variables: {list(config['schema']['properties'].keys())}")
        print(f"  Functions: {list(functions_spec.keys())}")

        print("\n🔄 Propagation Rules:")
        reverse_mesh = config["propagation_rules"]["reverseMesh"]
        for var, deps in reverse_mesh.items():
            print(f"  {var} → {deps}")

        print("\n🎨 UI Schema:")
        ui_schema = config["uiSchema"]
        for var, schema in ui_schema.items():
            if schema:
                print(f"  {var}: {schema}")

        print("\n📱 Building App...")
        app_path = builder.build_app(title="Manual Test App")

        print(f"✅ App created: {app_path}")
        print(f"📄 File size: {app_path.stat().st_size} bytes")

        # Display key sections of the HTML
        html_content = app_path.read_text()

        print("\n🔍 HTML Structure Check:")
        checks = [
            ("DOCTYPE", "<!DOCTYPE html>" in html_content),
            ("Title", "Manual Test App" in html_content),
            ("React", "react" in html_content.lower()),
            ("RJSF", "@rjsf/core" in html_content),
            ("Mesh Functions", "meshFunctions" in html_content),
            ("Propagator", "MeshPropagator" in html_content),
            ("Form Config", "formConfig" in html_content),
            ("Celsius Function", "celsius * 9/5 + 32" in html_content),
            ("Area Function", "Math.PI * radius * radius" in html_content),
        ]

        for check_name, passes in checks:
            status = "✅" if passes else "❌"
            print(f"  {status} {check_name}")

        print("\n📋 Sample HTML Sections:")

        # Extract and show the mesh configuration
        import re
        import json

        config_match = re.search(
            r'const meshConfig = ({.*?});', html_content, re.DOTALL
        )
        if config_match:
            config_obj = json.loads(config_match.group(1))
            print("\n  🔧 Mesh Configuration:")
            print(f"    Mesh: {config_obj['mesh']}")
            print(f"    Reverse: {config_obj['reverseMesh']}")

        form_config_match = re.search(
            r'const formConfig = ({.*?});', html_content, re.DOTALL
        )
        if form_config_match:
            form_obj = json.loads(form_config_match.group(1))
            print("\n  📝 Form Configuration:")
            print(
                f"    Schema properties: {list(form_obj['schema']['properties'].keys())}"
            )
            print(f"    UI Schema keys: {list(form_obj['uiSchema'].keys())}")
            print(f"    Initial data: {form_obj['formData']}")

        print(f"\n🌐 To test manually, open: file://{app_path}")
        print("   The app should show:")
        print("   - Temperature inputs with Celsius, Fahrenheit, Kelvin")
        print("   - Radius input with area calculation")
        print("   - Size slider (0-100)")
        print("   - Read-only summary field")
        print("   - Real-time updates when values change")


if __name__ == "__main__":
    main()
