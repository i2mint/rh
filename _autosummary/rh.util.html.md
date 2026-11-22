# rh.util

Utility functions for the RH framework.

### Functions

| [`get_app_directory`](#rh.util.get_app_directory)(app_name)              | Get a directory path for a named app within RH_APP_FOLDER.   |
|-------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| [`serve_directory`](#rh.util.serve_directory)(directory[, port, host]) | Serve a directory using Python's built-in HTTP server.       |

### Classes

| [`PluginRegistry`](#rh.util.PluginRegistry)()   | Registry for managing optional tool plugins.   |
|---------------------------------------------------------------------|------------------------------------------------|

### *class* rh.util.PluginRegistry

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Registry for managing optional tool plugins.

#### get_handler(tool_type)

Return highest-priority available handler.

* **Parameters:**
  **tool_type** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Type of tool to get handler for
* **Returns:**
  Handler class or None if no handler available

#### register(tool_type, handler_class, priority=0)

Manual registration for custom handlers.

* **Parameters:**
  * **tool_type** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Type of tool (e.g., ‘template’, ‘bundler’)
  * **handler_class** – Handler class to register
  * **priority** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Priority (higher number = higher priority)

### rh.util.get_app_directory(app_name)

Get a directory path for a named app within RH_APP_FOLDER.

* **Parameters:**
  **app_name** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the app
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  Full path to the app directory

### rh.util.serve_directory(directory, port=8080, host='localhost')

Serve a directory using Python’s built-in HTTP server.

* **Parameters:**
  * **directory** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Directory to serve
  * **port** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Port to serve on
  * **host** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Host to bind to
