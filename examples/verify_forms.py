#!/usr/bin/env python3
"""
Simple verification script moved from misc/wip to examples.
"""

from rh import MeshBuilder


def main():
    print("🔍 Verifying RH Framework Form Generation...")

    mesh_spec = {"temp_fahrenheit": ["temp_celsius"], "temp_kelvin": ["temp_celsius"]}

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    initial_values = {"temp_celsius": 20.0}

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    app_path = builder.build_app(
        title="Temperature Converter Test", app_name="verify_test", embed_rjsf=True
    )

    print(f"✅ App generated: {app_path}")
    print(f"🔗 Open file://{app_path} in your browser to inspect the running app.")


if __name__ == "__main__":
    main()
