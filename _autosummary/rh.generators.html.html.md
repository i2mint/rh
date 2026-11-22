# rh.generators.html

HTML Generator for creating complete web applications from mesh configurations.

### Classes

| [`HTMLGenerator`](#rh.generators.html.HTMLGenerator)()   | Generates complete HTML applications from mesh configurations.   |
|--------------------------------------------------------------------|------------------------------------------------------------------|

### *class* rh.generators.html.HTMLGenerator

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Generates complete HTML applications from mesh configurations.

The generator builds a self-contained index.html that includes React, a
lightweight fallback form component, optional embedded vendor UMD for
RJSF (when embed_rjsf=True), and the mesh propagation runtime.

#### generate_app(config, title='Mesh App', embed_rjsf=False)

Return a full HTML document as a string for the provided mesh config.

- config: dict with keys schema, uiSchema, initial_values, mesh (dict of function deps), functions (optional)
- embed_rjsf: if True, embed the deterministic vendor UMD found in templates/vendor/rjsf-umd.js

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
