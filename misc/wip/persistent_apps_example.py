"""
Example showing how to use RH_APP_FOLDER for persistent app storage.
"""

from rh import MeshBuilder
from rh.util import RH_APP_FOLDER, get_app_directory
import os


def create_persistent_apps():
    """Demonstrate creating apps that persist in RH_APP_FOLDER."""

    print("🗂️  RH App Directory Management")
    print("=" * 50)
    print(f"📁 RH_APP_FOLDER: {RH_APP_FOLDER}")
    print()

    # Create a simple calculator app
    mesh_spec = {
        "result": ["a", "b", "operation"],
        "square_a": ["a"],
        "square_b": ["b"],
    }

    functions_spec = {
        "result": """
            if (operation === 'add') return a + b;
            if (operation === 'multiply') return a * b;
            if (operation === 'subtract') return a - b;
            if (operation === 'divide') return b !== 0 ? a / b : 0;
            return 0;
        """,
        "square_a": "return a * a;",
        "square_b": "return b * b;",
    }

    initial_values = {"a": 10, "b": 5, "operation": "add"}

    field_overrides = {
        "operation": {
            "type": "string",
            "enum": ["add", "multiply", "subtract", "divide"],
            "ui:widget": "select",
        }
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
        field_overrides=field_overrides,
    )

    # Build app with automatic directory naming
    print("🔢 Creating Calculator App...")
    app_path = builder.build_app(title="Simple Calculator")
    print(f"✅ Calculator created at: {app_path}")
    print(f"🌐 Open in browser: file://{app_path}")
    print()

    # Build another app with explicit app name
    print("🌡️  Creating Temperature Converter...")
    temp_mesh = {"temp_fahrenheit": ["temp_celsius"], "temp_kelvin": ["temp_celsius"]}
    temp_functions = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }
    temp_builder = MeshBuilder(
        mesh_spec=temp_mesh,
        functions_spec=temp_functions,
        initial_values={"temp_celsius": 20.0},
    )

    temp_app_path = temp_builder.build_app(
        title="Temperature Converter", app_name="my_temp_converter"
    )
    print(f"✅ Temperature converter created at: {temp_app_path}")
    print(f"🌐 Open in browser: file://{temp_app_path}")
    print()

    # Show what's in the apps folder
    print("📂 Apps in RH_APP_FOLDER:")
    if os.path.exists(RH_APP_FOLDER):
        for item in os.listdir(RH_APP_FOLDER):
            item_path = os.path.join(RH_APP_FOLDER, item)
            if os.path.isdir(item_path):
                print(f"   📁 {item}/")
                if os.path.exists(os.path.join(item_path, "index.html")):
                    print(f"      └── 📄 index.html")

    print()
    print("💡 Tips:")
    print("   - Apps are saved permanently in RH_APP_FOLDER")
    print("   - Set RH_APP_FOLDER environment variable to customize location")
    print("   - App names are inferred from titles or can be set explicitly")
    print("   - Use builder.output_dir for custom locations")


if __name__ == "__main__":
    create_persistent_apps()
