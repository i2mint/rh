#!/usr/bin/env python
"""Command-line interface for RH (Reactive HTML Framework)."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .core import MeshBuilder
from .validation import validate_mesh


def load_config_from_file(filepath: str) -> dict:
    """Load mesh configuration from a JSON file.

    Args:
        filepath: Path to JSON configuration file

    Returns:
        Dictionary with mesh_spec, functions_spec, and initial_values
    """
    with open(filepath) as f:
        config = json.load(f)

    required_keys = ["mesh_spec", "functions_spec"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Config file must contain '{key}' key")

    return config


def create_app(args):
    """Create an RH app from command-line arguments."""
    if args.config:
        # Load from config file
        config = load_config_from_file(args.config)
        mesh_spec = config["mesh_spec"]
        functions_spec = config["functions_spec"]
        initial_values = config.get("initial_values", {})
        field_overrides = config.get("field_overrides", {})
        ui_config = config.get("ui_config", {})
        meta = config.get("meta")
    else:
        print("Error: --config is required")
        sys.exit(1)

    # Validate if requested
    if not args.no_validate:
        is_valid = validate_mesh(mesh_spec, functions_spec, initial_values)
        if not is_valid and args.strict:
            print("Validation failed and --strict is enabled. Exiting.")
            sys.exit(1)

    # Build the app
    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
        field_overrides=field_overrides,
        ui_config=ui_config,
        output_dir=args.output,
    )

    app_path = builder.build_app(
        title=args.title or "RH App",
        serve=args.serve,
        port=args.port,
        embed_react=args.embed_react,
        embed_rjsf=args.embed_rjsf,
        meta=meta,
    )

    if not args.serve:
        print(f"✓ App created successfully at: {app_path}")
        if args.embed_react:
            print("  (Offline mode: React embedded)")


def validate_config(args):
    """Validate a mesh configuration file."""
    config = load_config_from_file(args.config)

    mesh_spec = config["mesh_spec"]
    functions_spec = config["functions_spec"]
    initial_values = config.get("initial_values", {})

    print("Validating mesh configuration...")

    is_valid = validate_mesh(
        mesh_spec, functions_spec, initial_values, raise_on_error=False
    )

    if is_valid:
        print("✓ Configuration is valid!")
        sys.exit(0)
    else:
        print("✗ Configuration has errors (see above)")
        sys.exit(1)


def create_template(args):
    """Create a template configuration file."""
    template = {
        "mesh_spec": {
            "fahrenheit": ["celsius"],
            "kelvin": ["celsius"],
        },
        "functions_spec": {
            "fahrenheit": "return celsius * 9/5 + 32;",
            "kelvin": "return celsius + 273.15;",
        },
        "initial_values": {"celsius": 20.0},
        "field_overrides": {},
        "ui_config": {},
        "meta": {
            "description": "A temperature converter example",
            "features": [
                "Convert Celsius to Fahrenheit",
                "Convert Celsius to Kelvin",
                "Real-time updates",
            ],
        },
    }

    output_path = Path(args.output or "rh_config.json")

    if output_path.exists() and not args.force:
        print(f"Error: {output_path} already exists. Use --force to overwrite.")
        sys.exit(1)

    with open(output_path, "w") as f:
        json.dump(template, f, indent=2)

    print(f"✓ Template created at: {output_path}")
    print(f"\nEdit the file and then run:")
    print(f"  rh create --config {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RH - Reactive HTML Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a template config file
  rh template -o my_app.json

  # Create an app from config
  rh create --config my_app.json --title "My App" --output ./my_app

  # Create and serve
  rh create --config my_app.json --serve --port 8080

  # Create offline app (embed all resources)
  rh create --config my_app.json --embed-react --output ./offline_app

  # Validate a config file
  rh validate --config my_app.json
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create an RH app")
    create_parser.add_argument(
        "--config", "-c", required=True, help="Path to JSON configuration file"
    )
    create_parser.add_argument(
        "--title", "-t", help="App title (default: from config or 'RH App')"
    )
    create_parser.add_argument(
        "--output", "-o", help="Output directory (default: from config or ./rh_app)"
    )
    create_parser.add_argument(
        "--serve", "-s", action="store_true", help="Serve the app after creation"
    )
    create_parser.add_argument(
        "--port", "-p", type=int, default=8080, help="Port for development server"
    )
    create_parser.add_argument(
        "--embed-react", action="store_true", help="Embed React for offline use"
    )
    create_parser.add_argument(
        "--embed-rjsf", action="store_true", help="Embed RJSF for offline use"
    )
    create_parser.add_argument(
        "--no-validate", action="store_true", help="Skip validation"
    )
    create_parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if validation fails",
    )
    create_parser.set_defaults(func=create_app)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a configuration file"
    )
    validate_parser.add_argument(
        "--config", "-c", required=True, help="Path to JSON configuration file"
    )
    validate_parser.set_defaults(func=validate_config)

    # Template command
    template_parser = subparsers.add_parser(
        "template", help="Create a template configuration file"
    )
    template_parser.add_argument(
        "--output", "-o", help="Output file path (default: rh_config.json)"
    )
    template_parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing file"
    )
    template_parser.set_defaults(func=create_template)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
