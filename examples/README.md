# RH Examples

This directory contains example configurations demonstrating various features of the RH framework.

## Available Examples

### 1. Temperature Converter (`temperature_converter.json`)
A simple temperature converter between Celsius, Fahrenheit, and Kelvin.

**Try it:**
```bash
rh create --config examples/temperature_converter.json --serve
```

### 2. Physics Calculator (`physics_calculator.json`)
Calculate various physics quantities (velocity, acceleration, force, kinetic energy) from basic inputs.

**Try it:**
```bash
rh create --config examples/physics_calculator.json --title "Physics Calculator" --serve
```

### 3. Loan Calculator (`loan_calculator.json`)
Calculate loan payments with interactive sliders for amount, interest rate, and term.

**Try it:**
```bash
rh create --config examples/loan_calculator.json --title "Loan Calculator" --serve
```

## Creating Your Own Examples

You can create a template configuration file with:

```bash
rh template -o my_app.json
```

Then edit the file and create your app:

```bash
rh create --config my_app.json --serve
```

## Configuration Structure

Each JSON file contains:
- `mesh_spec`: Defines which variables depend on which other variables
- `functions_spec`: JavaScript functions to compute derived values
- `initial_values`: Starting values for input variables
- `field_overrides`: Custom field configurations (titles, ranges, etc.)
- `ui_config`: Additional UI customizations
- `meta`: Metadata like description and features list

## Offline Mode

To create apps that work offline (no CDN dependencies):

```bash
rh create --config examples/temperature_converter.json --embed-react --output ./offline_app
```

This embeds all JavaScript libraries directly into the HTML file.
