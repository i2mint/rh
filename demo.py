"""
Demo script showing the RH (Reactive Html Framework) in action.

This script creates a temperature converter application demonstrating
the core capabilities of the framework.
"""

from rh import MeshBuilder
import tempfile
from pathlib import Path


def demo_temperature_converter():
    """Create a temperature converter app demonstrating basic functionality."""
    print("🌡️  Creating Temperature Converter App...")

    # Define the mesh - relationships between variables
    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
        "temp_rankine": ["temp_fahrenheit"],
    }

    # Define the functions - how to compute each relationship
    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
        "temp_rankine": "return temp_fahrenheit + 459.67;",
    }

    # Initial values for type inference and default display
    initial_values = {"temp_celsius": 20.0}

    # Create the mesh builder
    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    # Generate and inspect the configuration
    config = builder.generate_config()
    print(f"✅ Generated config with {len(config['schema']['properties'])} variables")
    print(f"   Variables: {list(config['schema']['properties'].keys())}")

    # Build the app
    with tempfile.TemporaryDirectory() as tmpdir:
        builder.output_dir = tmpdir  # Set output directory
        app_path = builder.build_app(title="Temperature Converter")

        print(f"📱 App created at: {app_path}")
        print(f"📄 HTML size: {app_path.stat().st_size} bytes")

        # Show a snippet of the generated HTML
        html_content = app_path.read_text()
        print("🔍 HTML Preview:")
        lines = html_content.split('\n')
        for i, line in enumerate(lines[:10]):
            print(f"   {i+1:2d}: {line}")
        print("   ...")

        return app_path


def demo_physics_calculator():
    """Create a physics calculator with more complex relationships."""
    print("\n⚡ Creating Physics Calculator App...")

    mesh_spec = {
        "kinetic_energy": ["mass", "velocity"],
        "momentum": ["mass", "velocity"],
        "force": ["mass", "acceleration"],
        "energy_force_ratio": ["kinetic_energy", "force"],
        "slider_efficiency": [],  # Using convention for slider
        "readonly_total_energy": [
            "kinetic_energy",
            "slider_efficiency",
        ],  # Convention for readonly
    }

    functions_spec = {
        "kinetic_energy": "return 0.5 * mass * velocity * velocity;",
        "momentum": "return mass * velocity;",
        "force": "return mass * acceleration;",
        "energy_force_ratio": "return force > 0 ? kinetic_energy / force : 0;",
        "readonly_total_energy": "return kinetic_energy * (slider_efficiency / 100);",
    }

    initial_values = {
        "mass": 10.0,  # kg
        "velocity": 5.0,  # m/s
        "acceleration": 9.81,  # m/s² (gravity)
        "slider_efficiency": 80,  # %
    }

    # Custom field overrides for better UX
    field_overrides = {
        "mass": {
            "title": "Mass (kg)",
            "minimum": 0.1,
            "maximum": 1000,
            "ui:help": "Mass of the object in kilograms",
        },
        "velocity": {
            "title": "Velocity (m/s)",
            "minimum": 0,
            "maximum": 100,
            "ui:help": "Velocity in meters per second",
        },
        "acceleration": {
            "title": "Acceleration (m/s²)",
            "minimum": 0,
            "maximum": 50,
            "ui:help": "Acceleration in meters per second squared",
        },
        "slider_efficiency": {"title": "Efficiency (%)", "minimum": 0, "maximum": 100},
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
        field_overrides=field_overrides,
    )

    config = builder.generate_config()
    print(f"✅ Generated config with {len(config['schema']['properties'])} variables")

    # Show propagation rules
    reverse_mesh = config["propagation_rules"]["reverseMesh"]
    print("🔄 Propagation Rules:")
    for input_var, triggered_funcs in reverse_mesh.items():
        print(f"   {input_var} → {triggered_funcs}")

    # Show UI conventions applied
    ui_schema = config["uiSchema"]
    print("🎨 UI Conventions:")
    for var, ui_config in ui_schema.items():
        if ui_config:
            print(f"   {var}: {ui_config}")

    with tempfile.TemporaryDirectory() as tmpdir:
        builder.output_dir = tmpdir  # Set output directory
        app_path = builder.build_app(title="Physics Calculator")
        print(f"📱 Physics app created at: {app_path}")

        return app_path


def demo_bidirectional_conversion():
    """Demonstrate bidirectional relationships (cycles)."""
    print("\n🔄 Creating Bidirectional Currency Converter...")

    # This mesh has cycles - USD can convert to EUR and vice versa
    mesh_spec = {
        "amount_eur": ["amount_usd"],
        "amount_usd": ["amount_eur"],  # Bidirectional
        "amount_gbp": ["amount_eur"],
        "total_portfolio": ["amount_usd", "amount_eur", "amount_gbp"],
    }

    functions_spec = {
        "amount_eur": "return amount_usd * 0.85;",  # USD to EUR
        "amount_usd": "return amount_eur / 0.85;",  # EUR to USD (reverse)
        "amount_gbp": "return amount_eur * 0.88;",  # EUR to GBP
        "total_portfolio": "return amount_usd + (amount_eur / 0.85) + (amount_gbp / 0.88 / 0.85);",
    }

    initial_values = {"amount_usd": 1000.0}

    field_overrides = {
        "amount_usd": {"title": "USD Amount", "ui:help": "Amount in US Dollars"},
        "amount_eur": {"title": "EUR Amount", "ui:help": "Amount in Euros"},
        "amount_gbp": {"title": "GBP Amount", "ui:help": "Amount in British Pounds"},
        "total_portfolio": {
            "title": "Total Portfolio (USD equivalent)",
            "ui:readonly": True,
        },
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
        field_overrides=field_overrides,
    )

    config = builder.generate_config()

    # Demonstrate the cycle detection
    reverse_mesh = config["propagation_rules"]["reverseMesh"]
    print("🔄 Bidirectional Dependencies:")
    print(f"   USD triggers: {reverse_mesh.get('amount_usd', [])}")
    print(f"   EUR triggers: {reverse_mesh.get('amount_eur', [])}")

    with tempfile.TemporaryDirectory() as tmpdir:
        builder.output_dir = tmpdir  # Set output directory
        app_path = builder.build_app(title="Currency Converter")
        print(f"💱 Currency converter created at: {app_path}")

        return app_path


def main():
    """Run all demos."""
    print("🚀 RH Framework Demo - Reactive Html Builder")
    print("=" * 50)

    try:
        # Run all demos
        temp_app = demo_temperature_converter()
        physics_app = demo_physics_calculator()
        currency_app = demo_bidirectional_conversion()

        print("\n🎉 All demos completed successfully!")
        print("\nGenerated apps:")
        print(f"   🌡️  Temperature: {temp_app}")
        print(f"   ⚡ Physics: {physics_app}")
        print(f"   💱 Currency: {currency_app}")

        print("\n💡 Next steps:")
        print("   - Open any HTML file in a browser to see the interactive app")
        print("   - Modify input values to see real-time propagation")
        print("   - Use builder.serve() to start a development server")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
