"""
Simple example showing how to create and serve a reactive web app.

This creates a basic temperature converter that you can view in your browser.
"""

from rh import MeshBuilder


def main():
    """Create and serve a temperature converter app."""
    print("Creating Temperature Converter...")

    # Define the relationships between variables
    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
    }

    # Define how to compute each relationship
    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    # Set initial values
    initial_values = {"temp_celsius": 20.0}

    # Create the builder
    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    # Build the app
    app_path = builder.build_app(title="My Temperature Converter")
    print(f"✅ App created at: {app_path}")

    # Serve it locally (this will open your browser automatically)
    print("🌐 Starting development server...")
    print("Press Ctrl+C to stop the server")
    builder.serve(port=8080)


if __name__ == "__main__":
    main()
