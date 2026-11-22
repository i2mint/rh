# rh.core

Core RH (Reactive Html Framework) module.

This module implements the main MeshBuilder class for creating reactive
computational meshes with interactive web interfaces.

### Classes

| [`MeshBuilder`](#rh.core.MeshBuilder)(mesh_spec, functions_spec[, ...])   | Main class for building reactive mesh applications.   |
|--------------------------------------------------------------------------------------------------|-------------------------------------------------------|

### *class* rh.core.MeshBuilder(mesh_spec, functions_spec, initial_values=dict(), field_overrides=dict(), ui_config=dict(), output_dir=None)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Main class for building reactive mesh applications.

A mesh defines relationships between variables through functions,
enabling bidirectional dependencies and real-time updates in web interfaces.

#### build_app(, title='Mesh App', serve=False, port=8080, app_name=None, embed_rjsf=False, meta=None)

Generate complete HTML app with all assets bundled.

* **Parameters:**
  * **title** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Title for the HTML page
  * **serve** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Whether to start a development server
  * **port** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Port for development server
  * **app_name** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – Name for the app (used for directory if output_dir not set)
* **Return type:**
  [`Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path)
* **Returns:**
  Path to the generated HTML file

#### build_components_from_config(config)

Generate RJSF components from explicit config.

* **Parameters:**
  **config** ([`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Configuration dictionary from generate_config()
* **Return type:**
  [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]
* **Returns:**
  Dict with component specifications for external use

#### generate_config()

Generate explicit configuration from inputs and conventions.

This is the key method - everything downstream uses only this config.

* **Return type:**
  [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]

#### serve(directory=None, port=8080)

Serve the app locally for development.

* **Parameters:**
  * **directory** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – Directory to serve (if not provided, uses output_dir logic)
  * **port** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Port to serve on
