# Reactive Html Framework (RH) - Complete Specification

## Overview

We are building a framework that transforms user-defined relationships between variables into interactive, computable systems. The framework handles bidirectional dependencies and cycles gracefully, enabling users to express their mental models of how variables relate without worrying about computational ordering or infinite loops.

## Core Architecture

### 1. Mesh Specification Layer
We define computational networks (which we call "meshes") using various input formats:

**Input Sources:**
- **JSON specifications** with explicit function definitions
- **Python/JavaScript functions** with introspected dependencies
- **Excel formulas** parsed from spreadsheet cells
- **Natural language descriptions** processed by AI agents to extract relationships
- **Mathematical notation** parsed from LaTeX or symbolic expressions
- **Configuration files** (YAML, TOML) with domain-specific syntax

All input sources compile to a unified mesh representation where:
- **Variables** represent data points or computed values
- **Functions** express relationships between variables
- Function argument names serve as source variable IDs
- Function names serve as target variable IDs
- Cycles are permitted (e.g., `Y = f(X)` and `X = g(Y)` can coexist)

### 2. Intermediate Representation (IR)
We compile mesh specifications into a static, optimized representation containing:
- Variable-to-function dependency mappings
- Topological ordering for acyclic portions
- Cycle detection and resolution strategies
- Computation scheduling indices

This IR eliminates the need for runtime dependency analysis and enables efficient execution across different rendering environments.

### 3. Execution Modules
We implement multiple execution environments from the same IR:

**Computational Executors:**
- **Python callable objects** for programmatic calculation
- **JavaScript compute engines** for web-based processing
- **Excel workbooks** with generated formulas and macros

**Interactive Renderers:**
- **HTML/JS reactive pages** with real-time updates via sliders and inputs
- **Desktop applications** with native UI controls
- **Jupyter notebook widgets** for exploratory analysis
- **Web-based visualization dashboards**

**Export Formats:**
- **Static reports** (PDF, HTML)
- **API endpoints** for external system integration
- **Database schemas** with computed columns

## Key Innovation

Our system resolves bidirectional dependencies through constraint satisfaction rather than sequential computation, allowing the expression of natural relationships (like `temperature_celsius = (temperature_fahrenheit - 32) * 5/9` alongside `temperature_fahrenheit = temperature_celsius * 9/5 + 32`) without computational conflicts.

## Target Use Case

We prioritize creating interactive web applications where users can manipulate variable values and observe real-time propagation of changes throughout their defined system of relationships, while maintaining flexibility in how meshes are specified and executed.

---

## Technical Implementation

### Core Data Structure and Algorithm

#### Mesh Specification Format
```python
mesh = {
    "temp_fahrenheit": ["temp_celsius"],           # F = f(C)
    "temp_celsius": ["temp_fahrenheit"],           # C = g(F)  
    "temp_kelvin": ["temp_celsius"],               # K = h(C)
    "pressure_adjusted": ["pressure", "temp_kelvin"]  # P_adj = j(P, K)
}
```

Where:
- **Keys** (function names) = variable names that will store results
- **Values** (argument lists) = variable names that serve as inputs

#### Reverse Mapping Construction
We construct the inverse mapping from **argument names → function names**:
```python
reverse_mesh = {
    "temp_celsius": ["temp_fahrenheit", "temp_kelvin"],
    "temp_fahrenheit": ["temp_celsius"],
    "temp_kelvin": ["pressure_adjusted"],
    "pressure": ["pressure_adjusted"]
}
```

#### RJSF Form Generation
For each unique argument name across all functions, we generate:
- **Input element** (numerical input by default, inferred from type/default value)
- **Display element** for computed results
- **Reactive binding** to trigger computation on value change

#### JavaScript Propagation Algorithm
```javascript
class MeshPropagator {
    constructor(mesh, functions) {
        this.mesh = mesh;           // {"temp_f": ["temp_c"], "temp_k": ["temp_c"]}
        this.functions = functions; // {"temp_f": (temp_c) => temp_c * 9/5 + 32}
        this.reverseMesh = this.buildReverse(mesh);
    }
    
    // General callback factory
    createCallback(changedVariable) {
        return (value, formData) => {
            return this.propagate(changedVariable, value, formData);
        };
    }
    
    propagate(changedVariable, newValue, formData) {
        const newFormData = {...formData, [changedVariable]: newValue};
        const computed = new Set();
        const queue = [...(this.reverseMesh[changedVariable] || [])];
        
        while (queue.length > 0) {
            const funcName = queue.shift();
            
            if (computed.has(funcName)) {
                throw new Error(`Cyclic computation detected: ${funcName}`);
            }
            
            computed.add(funcName);
            const args = this.mesh[funcName];
            const argValues = args.map(arg => newFormData[arg]);
            const result = this.functions[funcName](...argValues);
            
            if (newFormData[funcName] !== result) {
                newFormData[funcName] = result;
                
                // Add dependent functions to queue
                if (this.reverseMesh[funcName]) {
                    queue.push(...this.reverseMesh[funcName].filter(f => !computed.has(f)));
                }
            }
        }
        
        return newFormData;
    }
}
```

## Package Architecture

### File Structure
```
rh/
├── rh/
│   ├── __init__.py           # Main API: MeshBuilder class
│   ├── spec/
│   │   ├── __init__.py
│   │   ├── parsers.py        # Parse different mesh formats (JSON, Python funcs, etc.)
│   │   └── validators.py     # Validate mesh specifications
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── rjsf.py          # Generate RJSF schema + UI schema
│   │   ├── html.py          # Generate complete HTML page
│   │   └── assets.py        # Bundle JS/CSS assets
│   ├── functions/
│   │   ├── __init__.py
│   │   ├── js_resolver.py   # Resolve and bundle JS functions
│   │   └── registry.py      # Built-in function library
│   ├── templates/
│   │   ├── base.html        # Base HTML template
│   │   └── mesh_app.js      # Template for the mesh propagator
│   └── util.py              # HTTP servers, file operations, etc.
├── misc/
│   ├── examples/            # Example projects and demos
│   └── CHANGELOG.md         # Record major changes made by the AI assistant
└── tests/
```

### Main API Design
```python
# rh/__init__.py
from .rh import MeshBuilder
from .spec.parsers import from_functions, from_json, from_yaml

class MeshBuilder:
    def __init__(self, mesh_spec, functions_spec, *, 
                 initial_values=None,
                 field_overrides=None,
                 ui_config=None,
                 output_dir="./mesh_app"):
        """
        mesh_spec: dict or path to JSON/YAML
        functions_spec: dict mapping function names to JS code/paths/URLs
        initial_values: dict of initial values for type inference
        field_overrides: dict of field-specific UI customizations
        """
        self.mesh = self._parse_mesh(mesh_spec)
        self.functions = self._resolve_functions(functions_spec)
        self.initial_values = initial_values or {}
        self.field_overrides = field_overrides or {}
        self.output_dir = Path(output_dir)
    
    def generate_config(self):
        """Generate explicit configuration from inputs + conventions"""
        # This is the key method - everything downstream uses only this config
        
    def build_app(self, *, title="Mesh App", serve=False, port=8080):
        """Generate complete HTML app with all assets bundled"""
        # Returns path to generated HTML file
        
    def build_components_from_config(self, config):
        """Generate RJSF schema, functions bundle, and config separately"""
        # Returns dict with 'rjsf_schema', 'rjsf_ui_schema', 'js_functions_bundle', 'propagation_config'
        
    def serve(self, port=8080):
        """Serve the app locally for development"""
```

### Function Resolution Strategies

#### 1. Inline Functions
```python
functions_spec = {
    "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
    "temp_kelvin": "return temp_celsius + 273.15;"
}
```

#### 2. File Paths
```python
functions_spec = {
    "temp_fahrenheit": "./functions/temperature.js#fahrenheit",  # function in file
    "temp_kelvin": "./functions/temperature.js#kelvin",
    "complex_calc": "./calculations/physics.js"  # whole file
}
```

#### 3. NPM Packages/URLs
```python
functions_spec = {
    "math_operation": "https://unpkg.com/mathjs@11.0.0/lib/cjs/index.js#evaluate",
    "lodash_func": "lodash#get"  # from CDN
}
```

#### 4. Built-in Registry
```python
# rh comes with common functions
from rh.functions.registry import math_functions

functions_spec = {
    **math_functions,  # Pre-built math functions
    "custom_func": "return x * 2;"
}
```

### JavaScript Function Resolver
```python
# rh/functions/js_resolver.py
class JSResolver:
    def resolve_functions(self, functions_spec: dict) -> str:
        """Bundle all functions into a single JS object"""
        resolved = {}
        
        for func_name, spec in functions_spec.items():
            if isinstance(spec, str):
                if spec.startswith('http'):
                    resolved[func_name] = self._fetch_from_url(spec)
                elif spec.startswith('./') or spec.endswith('.js'):
                    resolved[func_name] = self._load_from_file(spec)
                elif '#' in spec:
                    resolved[func_name] = self._extract_function(spec)
                else:
                    resolved[func_name] = f"function({self._infer_args(func_name)}) {{ {spec} }}"
        
        return self._bundle_functions(resolved)
    
    def _bundle_functions(self, functions: dict) -> str:
        """Generate JS object with all functions"""
        js_functions = []
        for name, code in functions.items():
            js_functions.append(f'"{name}": {code}')
        
        return f"const meshFunctions = {{{','.join(js_functions)}}};"
```

## Convention Over Configuration

### Core Conventions

#### 1. Type Inference from Values
```python
# Smart defaults based on initial values
{
    "temperature": 20.5,        # → number input (float detected)
    "count": 42,               # → number input (int detected) 
    "name": "default",         # → text input
    "enabled": True,           # → checkbox
    "category": ["A", "B"],    # → select dropdown
}
```

#### 2. Function Naming Conventions
```python
# Variable names suggest UI behavior
{
    "slider_temperature": 20,     # → range slider (prefix detection)
    "readonly_result": ["x"],     # → read-only display
    "hidden_internal": ["x"],     # → hidden field
}
```

#### 3. Mesh Structure Patterns
```python
# Input variables (no dependencies) → form inputs
# Computed variables (have dependencies) → read-only displays
# Intermediate variables → hidden by default
```

### Configuration Override System
```python
class MeshBuilder:
    def __init__(self, 
                 mesh_spec, 
                 functions_spec,
                 *,
                 # UI Configuration
                 ui_config: dict = None,
                 type_mappings: dict = None,
                 field_overrides: dict = None,
                 # Behavior Configuration  
                 validation_rules: dict = None,
                 initial_values: dict = None):
        
        self.conventions = DefaultConventions()
        if ui_config:
            self.conventions.update(ui_config)
```

### Smart Defaults

#### Type → UI Element Mapping
```python
DEFAULT_TYPE_MAPPINGS = {
    (int, float): {
        "ui:widget": "updown",
        "ui:options": {"step": 0.1}
    },
    bool: {"ui:widget": "checkbox"},
    str: {"ui:widget": "text"},
    list: {"ui:widget": "select"},
}

# Convention-based overrides
PREFIX_MAPPINGS = {
    "slider_": {"ui:widget": "range", "minimum": 0, "maximum": 100},
    "readonly_": {"ui:readonly": True},
    "hidden_": {"ui:widget": "hidden"},
    "color_": {"ui:widget": "color"},
    "date_": {"ui:widget": "date"},
}
```

#### Layout Conventions
```python
# Auto-group related variables
{
    "temp_celsius": ...,
    "temp_fahrenheit": ...,     # → Temperature group
    "temp_kelvin": ...,
    
    "pressure_psi": ...,        # → Pressure group  
    "pressure_bar": ...,
}

# Auto-detect input vs output sections
inputs = variables_with_no_dependencies()
outputs = variables_with_dependencies()
```

### Configuration Escape Hatches
```python
# Fine-grained field control
field_overrides = {
    "temperature": {
        "title": "Temperature (°C)",
        "ui:widget": "range",
        "minimum": -100,
        "maximum": 500,
        "ui:help": "Ambient temperature"
    }
}

# Custom type mappings
type_mappings = {
    "percentage": {  # Custom semantic type
        "ui:widget": "range",
        "minimum": 0,
        "maximum": 100,
        "ui:options": {"step": 1}
    }
}
```

### Progressive Configuration Complexity
1. **Zero Config**: Just mesh + functions → working form
2. **Naming Conventions**: Use prefixes for common UI patterns  
3. **Type Hints**: Specify semantic types for better widgets
4. **Field Overrides**: Customize specific fields
5. **Full Control**: Custom UI schema generation

## Lightweight Tool Strategy

### Core Tools with Stdlib-First Approach

#### 1. JS Bundler
- **Primary**: `string` concatenation + `textwrap.dedent` (stdlib only)
- **Plugin**: Auto-register `esbuild-python` if available for minification
- **Alternative**: Simple regex-based module resolution for basic cases

#### 2. Template Engine
- **Primary**: `string.Template` (stdlib) for basic substitution
- **Plugin**: Auto-register `jinja2` if available for complex templating
- **Fallback**: f-strings with helper functions

#### 3. HTTP Server
- **Primary**: `http.server.HTTPServer` + `socketserver` (stdlib)
- **Plugin**: Auto-register `flask`/`fastapi` if available for advanced routing

#### 4. Dependency Resolver
- **Primary**: `urllib.request` for fetching CDN resources (stdlib)
- **Plugin**: Auto-register `requests` if available for better HTTP handling
- **File resolution**: `pathlib` + `importlib.util` (stdlib)

#### 5. Validation Engine
- **Primary**: Custom validators using `typing` introspection (stdlib)
- **Plugin**: Auto-register `jsonschema` if available for JSON Schema validation

### Plugin Architecture Design
```python
# rh/util.py
class PluginRegistry:
    def __init__(self):
        self._handlers = {}
        self._auto_register()
    
    def register(self, tool_type: str, handler_class, priority: int = 0):
        """Manual registration for custom handlers"""
        
    def _auto_register(self):
        """Detect and register third-party tools automatically"""
        if self._has_package('jinja2'):
            self.register('template', Jinja2Handler, priority=10)
        if self._has_package('esbuild'):
            self.register('bundler', ESBuildHandler, priority=10)
        # ... etc
    
    def get_handler(self, tool_type: str):
        """Return highest-priority available handler"""

# rh/base.py
@dataclass
class MeshBuilder:
    plugins: PluginRegistry = field(default_factory=PluginRegistry)
    
    def set_bundler(self, handler):
        self.plugins.register('bundler', handler, priority=20)
```

### Dependencies by Feature Level
- **Core (stdlib only)**: Basic mesh building, simple templates, dev server
- **Enhanced (+ lightweight deps)**: 
  - `jinja2` for advanced templates
- **Advanced (+ heavier deps)**:
  - `esbuild-python` for JS optimization
  - `jsonschema` for validation

---

## Python Coding Standards (From User Preferences)

### General Principles
- **Favor functional over object-oriented implementations** where appropriate. When using OOP, adhere to **SOLID principles**.
- Implement **Facades**, **Single Source of Truth (SSOT)**, and **Dependency Injection**.
- **Minimize hardcoded values** and magic numbers. Express configurable values as keyword-only arguments or external configurations, promoting an **open-closed design**.
- **Function/Method Argument Order:** For functions and methods, make arguments beyond the 3rd or 4th position **keyword-only**. Consider doing so even from the 2nd or 3rd position if it significantly improves readability or future extensibility.
- Use **dataclasses** whenever possible for simple data structures.

### Modularity and Helper Functions
- **Be modular:** Favor creating small, focused helper functions to support larger functionalities.
- **Inner Functions:** If a helper function is **only** used by a single target function, define it as an **inner function** (nested within the target function).
- **Module-Level Helper Functions:** If a helper function is, or could be, used by other functions within the **same module**, its name **must** start with a **single underscore** (e.g., `_helper_function`). This indicates it's an internal utility.
- **Reusable Functions:** If a function is broadly useful and can be reused in various contexts across different modules or packages, its name **should not** start with an underscore.

### Documentation and Testing
- **Docstrings:** Always include a **minimal docstring** for all functions, classes, and modules.
- **Doctests:** Whenever possible, include a **very simple doctest** within the docstring. Omit doctests only if it is an inner function or if the doctest requires significant setup that complicates the docstring.

### Architectural Patterns: Using Built-in Facades

#### Favor `Iterable` and `Iterator`
Unless a specific collection type (like `list`, `set`, `tuple`, etc.) is strictly required (e.g., for specific indexing or mutation), prefer returning an **`Iterable`** or yielding values (creating a generator). This promotes lazy evaluation and reduces memory consumption, while still allowing the consumer to iterate or cast to a concrete collection type if needed.

**Instead of:**
```python
def squares(n: int) -> list[int]:
    result = []
    for i in range(n):
        result.append(i * i)
    return result
```

**Prefer a generator:**
```python
def squares(n: int) -> 'Iterable[int]': # Added type hint for clarity
    for i in range(n):
        yield i * i
```

#### `Mapping` and `MutableMapping` for Storage Interactions
Most interactions with storage sources (local files, blob storage, databases, etc.) can be abstracted into **key-value operations**. In such cases, use **`Mapping`** for read-only interfaces and **`MutableMapping`** for read-write interfaces. These can be implemented through inheritance or (often preferable) composition.

---

## Complete Test-Driven Development Suite

### Unit Test: Core Mesh Builder Functionality

```python
# tests/test_basic_rh.py
import pytest
from rh import MeshBuilder

def test_basic_mesh_with_grouping_and_overrides():
    """Test core functionality: types, grouping, layout, and config overrides"""
    
    # Simple mesh with clear input/output distinction
    mesh_spec = {
        # Temperature conversion group
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
        
        # Physics calculation group  
        "kinetic_energy": ["mass", "velocity"],
        "momentum": ["mass", "velocity"],
        
        # UI demonstration
        "slider_opacity": [],  # Convention: slider prefix
        "readonly_total": ["kinetic_energy", "momentum"],  # Convention: readonly prefix
    }
    
    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
        "kinetic_energy": "return 0.5 * mass * velocity * velocity;",
        "momentum": "return mass * velocity;",
        "readonly_total": "return kinetic_energy + momentum;",
    }
    
    # Test configuration overrides
    field_overrides = {
        "mass": {
            "title": "Mass (kg)",
            "minimum": 0,
            "ui:help": "Object mass in kilograms"
        },
        "temp_celsius": {
            "ui:widget": "range",
            "minimum": -273,
            "maximum": 1000
        }
    }
    
    # Initial values for type inference
    initial_values = {
        "temp_celsius": 20.0,    # float → number input
        "mass": 10,              # int → number input  
        "velocity": 5.5,         # float → number input
        "slider_opacity": 50,    # int with slider_ prefix → range widget
    }
    
    # Build the mesh
    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
        field_overrides=field_overrides
    )
    
    # Generate explicit configuration
    config = builder.generate_config()
    
    # Test explicit configuration structure
    assert "schema" in config
    assert "uiSchema" in config  
    assert "functions" in config
    assert "propagation_rules" in config
    
    # Test type inference
    assert config["schema"]["properties"]["temp_celsius"]["type"] == "number"
    assert config["schema"]["properties"]["mass"]["type"] == "integer"
    
    # Test convention-based UI widgets
    assert config["uiSchema"]["slider_opacity"]["ui:widget"] == "range"
    assert config["uiSchema"]["readonly_total"]["ui:readonly"] == True
    
    # Test field overrides applied
    assert config["schema"]["properties"]["mass"]["title"] == "Mass (kg)"
    assert config["schema"]["properties"]["mass"]["minimum"] == 0
    assert config["uiSchema"]["temp_celsius"]["ui:widget"] == "range"
    
    # Test auto-grouping by prefix
    expected_groups = {
        "temperature": ["temp_celsius", "temp_fahrenheit", "temp_kelvin"],
        "physics": ["mass", "velocity", "kinetic_energy", "momentum"],  
        "ui_controls": ["slider_opacity", "readonly_total"]
    }
    
    for group_name, expected_fields in expected_groups.items():
        group_schema = config["schema"]["properties"][group_name]
        assert group_schema["type"] == "object"
        for field in expected_fields:
            assert field in group_schema["properties"]
    
    # Test propagation rules generation
    propagation = config["propagation_rules"]
    assert "temp_celsius" in propagation  # Input variable that triggers others
    assert "temp_fahrenheit" in propagation["temp_celsius"]  # Should trigger this
    assert "temp_kelvin" in propagation["temp_celsius"]      # And this
    
    # Test functions bundle
    assert "temp_fahrenheit" in config["functions"]
    assert "kinetic_energy" in config["functions"]
    
    # Test the explicit config can generate working components  
    components = builder.build_components_from_config(config)
    assert "rjsf_schema" in components
    assert "rjsf_ui_schema" in components
    assert "js_functions_bundle" in components
    assert "propagation_config" in components
```

### Integration Test: Playwright Browser Automation

```python
# tests/test_app_integration.py
import pytest
from playwright.sync_api import sync_playwright, expect
from rh import MeshBuilder
import tempfile
from pathlib import Path
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

@pytest.fixture
def mesh_app_server():
    """Generate test app and serve it locally"""
    mesh_spec = {
        # Temperature conversion group
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
        
        # Physics calculation group  
        "kinetic_energy": ["mass", "velocity"],
        "momentum": ["mass", "velocity"],
        
        # UI demonstration
        "slider_opacity": [],  # Convention: slider prefix
        "readonly_total": ["kinetic_energy", "momentum"],  # Convention: readonly prefix
    }
    
    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
        "kinetic_energy": "return 0.5 * mass * velocity * velocity;",
        "momentum": "return mass * velocity;",
        "readonly_total": "return kinetic_energy + momentum;",
    }
    
    initial_values = {
        "temp_celsius": 0.0,
        "mass": 10,
        "velocity": 5.0,
        "slider_opacity": 50,
    }
    
    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values
    )
    
    # Generate app files
    with tempfile.TemporaryDirectory() as tmpdir:
        app_path = builder.build_app(output_dir=tmpdir, title="Test Mesh App")
        
        # Start local server
        os.chdir(tmpdir)
        port = _find_free_port()
        server = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        time.sleep(0.5)
        
        yield f"http://localhost:{port}"
        
        server.shutdown()

def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def test_basic_form_rendering(mesh_app_server):
    """Test that form renders with correct initial values and structure"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(mesh_app_server)
        
        # Wait for form to load
        expect(page.locator('form')).to_be_visible()
        
        # Test initial values
        expect(page.locator('input[name="temp_celsius"]')).to_have_value("0")
        expect(page.locator('input[name="mass"]')).to_have_value("10")
        expect(page.locator('input[name="velocity"]')).to_have_value("5")
        expect(page.locator('input[name="slider_opacity"]')).to_have_value("50")
        
        # Test computed initial values
        expect(page.locator('input[name="temp_fahrenheit"]')).to_have_value("32")
        expect(page.locator('input[name="temp_kelvin"]')).to_have_value("273.15")
        expect(page.locator('input[name="kinetic_energy"]')).to_have_value("125")  # 0.5 * 10 * 5^2
        expect(page.locator('input[name="momentum"]')).to_have_value("50")  # 10 * 5
        
        browser.close()

def test_temperature_conversion_propagation(mesh_app_server):
    """Test that changing celsius propagates to fahrenheit and kelvin"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(mesh_app_server)
        
        # Wait for form to load
        expect(page.locator('form')).to_be_visible()
        
        # Change celsius to 100
        celsius_input = page.locator('input[name="temp_celsius"]')
        celsius_input.fill("100")
        celsius_input.blur()  # Trigger onChange event
        
        # Verify propagation happened
        expect(page.locator('input[name="temp_fahrenheit"]')).to_have_value("212", timeout=2000)
        expect(page.locator('input[name="temp_kelvin"]')).to_have_value("373.15", timeout=2000)
        
        # Test another value
        celsius_input.fill("-40")
        celsius_input.blur()
        
        expect(page.locator('input[name="temp_fahrenheit"]')).to_have_value("-40", timeout=2000)
        expect(page.locator('input[name="temp_kelvin"]')).to_have_value("233.15", timeout=2000)
        
        browser.close()

def test_physics_calculations_propagation(mesh_app_server):
    """Test that changing mass/velocity updates kinetic energy and momentum"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(mesh_app_server)
        
        expect(page.locator('form')).to_be_visible()
        
        # Change mass
        mass_input = page.locator('input[name="mass"]')
        mass_input.fill("20")
        mass_input.blur()
        
        # Verify kinetic energy and momentum updated
        expect(page.locator('input[name="kinetic_energy"]')).to_have_value("250", timeout=2000)  # 0.5 * 20 * 5^2
        expect(page.locator('input[name="momentum"]')).to_have_value("100", timeout=2000)  # 20 * 5
        
        # Change velocity
        velocity_input = page.locator('input[name="velocity"]')
        velocity_input.fill("10")
        velocity_input.blur()
        
        # Verify calculations updated again
        expect(page.locator('input[name="kinetic_energy"]')).to_have_value("1000", timeout=2000)  # 0.5 * 20 * 10^2
        expect(page.locator('input[name="momentum"]')).to_have_value("200", timeout=2000)  # 20 * 10
        
        browser.close()

def test_ui_widget_conventions(mesh_app_server):
    """Test that UI conventions are applied correctly"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(mesh_app_server)
        
        expect(page.locator('form')).to_be_visible()
        
        # Test slider convention
        slider_input = page.locator('input[name="slider_opacity"]')
        expect(slider_input).to_have_attribute("type", "range")
        
        # Test readonly convention
        readonly_input = page.locator('input[name="readonly_total"]')
        expect(readonly_input).to_have_attribute("readonly")
        
        # Test slider interaction
        slider_input.fill("75")
        expect(slider_input).to_have_value("75")
        
        browser.close()

def test_chained_propagation(mesh_app_server):
    """Test propagation through multiple levels of dependencies"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(mesh_app_server)
        
        expect(page.locator('form')).to_be_visible()
        
        # Change velocity, should update both kinetic_energy and momentum,
        # which should then update readonly_total
        velocity_input = page.locator('input[name="velocity"]')
        velocity_input.fill("6")
        velocity_input.blur()
        
        # Wait for first level propagation
        expect(page.locator('input[name="kinetic_energy"]')).to_have_value("180", timeout=2000)  # 0.5 * 10 * 6^2
        expect(page.locator('input[name="momentum"]')).to_have_value("60", timeout=2000)  # 10 * 6
        
        # Wait for second level propagation
        expect(page.locator('input[name="readonly_total"]')).to_have_value("240", timeout=2000)  # 180 + 60
        
        browser.close()

def test_form_validation_errors(mesh_app_server):
    """Test that invalid inputs show appropriate behavior"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(mesh_app_server)
        
        expect(page.locator('form')).to_be_visible()
        
        # Try entering invalid input
        mass_input = page.locator('input[name="mass"]')
        mass_input.fill("not-a-number")
        mass_input.blur()
        
        # Should either:
        # 1. Reject the input (value stays previous)
        # 2. Show validation error
        # 3. Clear dependent calculations
        
        # Wait a moment for any error handling
        page.wait_for_timeout(1000)
        
        # Verify system didn't crash (form still interactive)
        celsius_input = page.locator('input[name="temp_celsius"]')
        celsius_input.fill("50")
        celsius_input.blur()
        expect(page.locator('input[name="temp_fahrenheit"]')).to_have_value("122", timeout=2000)
        
        browser.close()

# Test with different mesh configurations
@pytest.mark.parametrize("headless", [True, False])
def test_visual_regression(mesh_app_server, headless):
    """Optional: Test visual appearance (can be run with headless=False for debugging)"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(mesh_app_server)
        
        expect(page.locator('form')).to_be_visible()
        
        # Take screenshot for visual regression testing
        if headless:
            page.screenshot(path="test-results/mesh-form.png")
        else:
            # For debugging - pause to inspect
            page.pause()
        
        browser.close()
```

---

## Usage Examples

### Simple Temperature Converter
```python
from rh import MeshBuilder

# Define relationships
mesh = {
    "fahrenheit": ["celsius"],
    "kelvin": ["celsius"],
    "rankine": ["fahrenheit"]
}

# Define functions
functions = {
    "fahrenheit": "return celsius * 9/5 + 32;",
    "kelvin": "return celsius + 273.15;",
    "rankine": "return fahrenheit + 459.67;"
}

# Build and deploy
builder = MeshBuilder(mesh, functions)
app_path = builder.build_app(title="Temperature Converter")
builder.serve(port=8080)  # Development server
```

### Complex Physics Calculator
```python
functions = {
    "calculate_bmi": "./health/bmi.js#calculateBMI",
    "format_result": "lodash#round",  # From CDN
    "complex_math": "https://unpkg.com/mathjs/lib/index.js#evaluate",
    "custom_logic": """
        const intermediate = weight / (height * height);
        return Math.round(intermediate * 100) / 100;
    """
}

builder = MeshBuilder("./config/health_mesh.json", functions)
components = builder.build_components()  # For custom integration
```

## HTML Template Structure

### Base HTML Template (`templates/base.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <style>
        .mesh-form-container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
        }
        .readonly-field {
            background-color: #f8f9fa;
        }
        .field-group {
            border: 1px solid #dee2e6;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="mesh-form-container">
            <h1>$title</h1>
            <div id="rjsf-form"></div>
        </div>
    </div>

    <!-- RJSF Dependencies -->
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@rjsf/core@5/dist/rjsf-core.umd.js"></script>
    <script src="https://unpkg.com/@rjsf/utils@5/dist/rjsf-utils.umd.js"></script>
    <script src="https://unpkg.com/@rjsf/validator-ajv8@5/dist/rjsf-validator-ajv8.umd.js"></script>
    <script src="https://unpkg.com/@rjsf/bootstrap-4@5/dist/rjsf-bootstrap-4.umd.js"></script>

    <!-- Mesh Functions -->
    <script>
        $mesh_functions
    </script>

    <!-- Mesh Propagator -->
    <script>
        $mesh_propagator
    </script>

    <!-- App Initialization -->
    <script>
        $app_initialization
    </script>
</body>
</html>
```

### Mesh Propagator Template (`templates/mesh_app.js`)
```javascript
class MeshPropagator {
    constructor(mesh, functions, reverseMesh) {
        this.mesh = mesh;
        this.functions = functions;
        this.reverseMesh = reverseMesh;
    }
    
    createCallback(changedVariable) {
        return (value, formData) => {
            return this.propagate(changedVariable, value, formData);
        };
    }
    
    propagate(changedVariable, newValue, formData) {
        const newFormData = {...formData, [changedVariable]: newValue};
        const computed = new Set();
        const queue = [...(this.reverseMesh[changedVariable] || [])];
        
        while (queue.length > 0) {
            const funcName = queue.shift();
            
            if (computed.has(funcName)) {
                console.error(`Cyclic computation detected: ${funcName}`);
                throw new Error(`Cyclic computation detected: ${funcName}`);
            }
            
            computed.add(funcName);
            const args = this.mesh[funcName];
            
            try {
                const argValues = args.map(arg => newFormData[arg]);
                const result = this.functions[funcName](...argValues);
                
                if (newFormData[funcName] !== result) {
                    newFormData[funcName] = result;
                    
                    // Add dependent functions to queue
                    if (this.reverseMesh[funcName]) {
                        queue.push(...this.reverseMesh[funcName].filter(f => !computed.has(f)));
                    }
                }
            } catch (error) {
                console.error(`Error computing ${funcName}:`, error);
                // Continue with other computations
            }
        }
        
        return newFormData;
    }
    
    buildReverse(mesh) {
        const reverse = {};
        for (const [funcName, argNames] of Object.entries(mesh)) {
            for (const argName of argNames) {
                if (!reverse[argName]) {
                    reverse[argName] = [];
                }
                reverse[argName].push(funcName);
            }
        }
        return reverse;
    }
}

// Initialize mesh propagator with configuration
const meshConfig = $mesh_config;
const meshPropagator = new MeshPropagator(
    meshConfig.mesh,
    meshFunctions,
    meshConfig.reverseMesh
);
```

## Core Implementation Classes

### MeshBuilder Core Class
```python
# rh/rh.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional
import json
import tempfile
from .spec.parsers import parse_mesh_spec
from .functions.js_resolver import JSResolver
from .generators.rjsf import RJSFGenerator
from .generators.html import HTMLGenerator
from .util import PluginRegistry

@dataclass
class MeshBuilder:
    """Main class for building reactive mesh applications"""
    
    mesh_spec: Dict[str, Any]
    functions_spec: Dict[str, Any]
    initial_values: Dict[str, Any] = field(default_factory=dict)
    field_overrides: Dict[str, Any] = field(default_factory=dict)
    ui_config: Dict[str, Any] = field(default_factory=dict)
    output_dir: str = "./mesh_app"
    plugins: PluginRegistry = field(default_factory=PluginRegistry)
    
    def __post_init__(self):
        """Initialize parsers and generators"""
        self.mesh = self._parse_mesh(self.mesh_spec)
        self.js_resolver = JSResolver(self.plugins)
        self.rjsf_generator = RJSFGenerator(self.plugins)
        self.html_generator = HTMLGenerator(self.plugins)
    
    def _parse_mesh(self, mesh_spec):
        """Parse mesh specification from various formats"""
        if isinstance(mesh_spec, str):
            # File path
            return parse_mesh_spec(mesh_spec)
        elif isinstance(mesh_spec, dict):
            # Direct dict
            return mesh_spec
        else:
            raise ValueError(f"Unsupported mesh_spec type: {type(mesh_spec)}")
    
    def generate_config(self) -> Dict[str, Any]:
        """Generate explicit configuration from inputs + conventions
        
        This is the key method - everything downstream uses only this config
        """
        config = {
            "schema": self._generate_json_schema(),
            "uiSchema": self._generate_ui_schema(),
            "functions": self._resolve_functions(),
            "propagation_rules": self._build_propagation_rules(),
            "initial_values": self.initial_values,
            "mesh": self.mesh
        }
        
        return config
    
    def _generate_json_schema(self) -> Dict[str, Any]:
        """Generate JSON Schema from mesh and initial values"""
        all_variables = self._get_all_variables()
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for var_name in all_variables:
            var_schema = self._infer_variable_schema(var_name)
            schema["properties"][var_name] = var_schema
            
            # Apply field overrides
            if var_name in self.field_overrides:
                schema["properties"][var_name].update(self.field_overrides[var_name])
        
        return schema
    
    def _generate_ui_schema(self) -> Dict[str, Any]:
        """Generate RJSF UI Schema with conventions and overrides"""
        ui_schema = {}
        all_variables = self._get_all_variables()
        
        for var_name in all_variables:
            ui_config = self._apply_ui_conventions(var_name)
            
            # Add propagation callback if this variable triggers others
            reverse_mesh = self._build_reverse_mesh()
            if var_name in reverse_mesh:
                ui_config["ui:onChange"] = f"meshPropagator.createCallback('{var_name}')"
            
            # Apply field overrides
            if var_name in self.field_overrides:
                ui_config.update({k: v for k, v in self.field_overrides[var_name].items() 
                                if k.startswith('ui:')})
            
            if ui_config:
                ui_schema[var_name] = ui_config
        
        return ui_schema
    
    def _infer_variable_schema(self, var_name: str) -> Dict[str, Any]:
        """Infer JSON Schema for a variable based on initial values"""
        if var_name in self.initial_values:
            value = self.initial_values[var_name]
            if isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, int):
                return {"type": "integer"}
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, str):
                return {"type": "string"}
            elif isinstance(value, list):
                return {"type": "array"}
        
        # Default to number for computed variables
        return {"type": "number"}
    
    def _apply_ui_conventions(self, var_name: str) -> Dict[str, Any]:
        """Apply naming conventions to determine UI widgets"""
        ui_config = {}
        
        # Prefix-based conventions
        if var_name.startswith("slider_"):
            ui_config.update({
                "ui:widget": "range",
                "minimum": 0,
                "maximum": 100
            })
        elif var_name.startswith("readonly_"):
            ui_config["ui:readonly"] = True
        elif var_name.startswith("hidden_"):
            ui_config["ui:widget"] = "hidden"
        elif var_name.startswith("color_"):
            ui_config["ui:widget"] = "color"
        elif var_name.startswith("date_"):
            ui_config["ui:widget"] = "date"
        
        # Check if this is a computed variable (has dependencies)
        if var_name in self.mesh:
            # This is a computed variable - make it readonly by default
            if "ui:readonly" not in ui_config and not var_name.startswith("slider_"):
                ui_config["ui:readonly"] = True
        
        return ui_config
    
    def _get_all_variables(self) -> set:
        """Get all variables (inputs and outputs) in the mesh"""
        variables = set(self.mesh.keys())  # Output variables
        for args in self.mesh.values():
            variables.update(args)  # Input variables
        return variables
    
    def _build_reverse_mesh(self) -> Dict[str, list]:
        """Build reverse mapping from arguments to functions"""
        reverse = {}
        for func_name, arg_names in self.mesh.items():
            for arg_name in arg_names:
                if arg_name not in reverse:
                    reverse[arg_name] = []
                reverse[arg_name].append(func_name)
        return reverse
    
    def _build_propagation_rules(self) -> Dict[str, Any]:
        """Build propagation rules for the mesh"""
        return {
            "reverseMesh": self._build_reverse_mesh(),
            "mesh": self.mesh
        }
    
    def _resolve_functions(self) -> str:
        """Resolve and bundle JavaScript functions"""
        return self.js_resolver.resolve_functions(self.functions_spec)
    
    def build_app(self, *, title: str = "Mesh App", serve: bool = False, port: int = 8080) -> Path:
        """Generate complete HTML app with all assets bundled"""
        config = self.generate_config()
        
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        html_content = self.html_generator.generate_app(config, title)
        
        app_file = output_path / "index.html"
        app_file.write_text(html_content)
        
        if serve:
            self.serve(port=port)
        
        return app_file
    
    def build_components_from_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RJSF components from explicit config"""
        return {
            "rjsf_schema": config["schema"],
            "rjsf_ui_schema": config["uiSchema"],
            "js_functions_bundle": config["functions"],
            "propagation_config": config["propagation_rules"]
        }
    
    def serve(self, port: int = 8080):
        """Serve the app locally for development"""
        from .util import serve_directory
        serve_directory(self.output_dir, port=port)
```

### JavaScript Function Resolver
```python
# rh/functions/js_resolver.py
from typing import Dict, Any
import urllib.request
import urllib.parse
from pathlib import Path
import re

class JSResolver:
    """Resolves and bundles JavaScript functions from various sources"""
    
    def __init__(self, plugins=None):
        self.plugins = plugins
    
    def resolve_functions(self, functions_spec: Dict[str, Any]) -> str:
        """Bundle all functions into a single JS object"""
        resolved = {}
        
        for func_name, spec in functions_spec.items():
            resolved[func_name] = self._resolve_single_function(func_name, spec)
        
        return self._bundle_functions(resolved)
    
    def _resolve_single_function(self, func_name: str, spec: Any) -> str:
        """Resolve a single function from its specification"""
        if isinstance(spec, str):
            if spec.startswith('http'):
                return self._fetch_from_url(spec)
            elif spec.startswith('./') or spec.endswith('.js'):
                return self._load_from_file(spec)
            elif '#' in spec:
                return self._extract_named_function(spec)
            else:
                # Inline function body
                args = self._infer_args(func_name)
                return f"function({', '.join(args)}) {{ {spec} }}"
        else:
            raise ValueError(f"Unsupported function spec type for {func_name}: {type(spec)}")
    
    def _fetch_from_url(self, url: str) -> str:
        """Fetch function from URL"""
        if '#' in url:
            url, func_name = url.split('#', 1)
            # Fetch and extract specific function
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
            return self._extract_function_from_content(content, func_name)
        else:
            # Fetch entire file
            with urllib.request.urlopen(url) as response:
                return response.read().decode('utf-8')
    
    def _load_from_file(self, file_spec: str) -> str:
        """Load function from local file"""
        if '#' in file_spec:
            file_path, func_name = file_spec.split('#', 1)
            content = Path(file_path).read_text()
            return self._extract_function_from_content(content, func_name)
        else:
            return Path(file_spec).read_text()
    
    def _extract_named_function(self, spec: str) -> str:
        """Extract named function from module spec like 'lodash#get'"""
        if spec.startswith('lodash#'):
            func_name = spec.split('#', 1)[1]
            return f"function(...args) {{ return _.{func_name}(...args); }}"
        # Add more built-in extractions as needed
        return spec
    
    def _extract_function_from_content(self, content: str, func_name: str) -> str:
        """Extract a specific function from JavaScript content"""
        # Simple regex-based extraction (can be enhanced)
        pattern = rf'function\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{[^}}]*\}}'
        match = re.search(pattern, content)
        if match:
            return match.group(0)
        
        # Try arrow function
        pattern = rf'const\s+{re.escape(func_name)}\s*=\s*\([^)]*\)\s*=>\s*[^;]*;'
        match = re.search(pattern, content)
        if match:
            return match.group(0)
        
        raise ValueError(f"Function {func_name} not found in content")
    
    def _infer_args(self, func_name: str) -> list:
        """Infer function arguments from mesh specification"""
        # This would need access to the mesh to determine arguments
        # For now, return empty list - will be enhanced in implementation
        return []
    
    def _bundle_functions(self, functions: Dict[str, str]) -> str:
        """Generate JS object with all functions"""
        js_functions = []
        for name, code in functions.items():
            # Ensure code is a function expression
            if not code.strip().startswith('function') and '=>' not in code:
                code = f"function() {{ {code} }}"
            js_functions.append(f'"{name}": {code}')
        
        return f"const meshFunctions = {{{','.join(js_functions)}}};"
```

### RJSF Generator
```python
# rh/generators/rjsf.py
from typing import Dict, Any

class RJSFGenerator:
    """Generates React JSON Schema Form specifications"""
    
    def __init__(self, plugins=None):
        self.plugins = plugins
    
    def generate_rjsf_spec(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete RJSF specification from config"""
        return {
            "schema": config["schema"],
            "uiSchema": self._enhance_ui_schema(config["uiSchema"], config),
            "formData": config["initial_values"]
        }
    
    def _enhance_ui_schema(self, ui_schema: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance UI schema with mesh-specific functionality"""
        enhanced = ui_schema.copy()
        
        # Add onChange callbacks for propagation
        reverse_mesh = config["propagation_rules"]["reverseMesh"]
        for var_name in reverse_mesh:
            if var_name not in enhanced:
                enhanced[var_name] = {}
            # The callback will be injected as JavaScript in the template
            enhanced[var_name]["ui:onChange"] = f"MESH_CALLBACK_{var_name}"
        
        return enhanced
```

### HTML Generator
```python
# rh/generators/html.py
from typing import Dict, Any
from pathlib import Path
import json
from string import Template

class HTMLGenerator:
    """Generates complete HTML applications"""
    
    def __init__(self, plugins=None):
        self.plugins = plugins
        self.template_dir = Path(__file__).parent.parent / "templates"
    
    def generate_app(self, config: Dict[str, Any], title: str = "Mesh App") -> str:
        """Generate complete HTML application"""
        # Load templates
        base_template = Template((self.template_dir / "base.html").read_text())
        mesh_js_template = Template((self.template_dir / "mesh_app.js").read_text())
        
        # Generate JavaScript components
        mesh_config_js = f"const meshConfig = {json.dumps(config['propagation_rules'])}"
        mesh_propagator_js = mesh_js_template.substitute(mesh_config=mesh_config_js)
        
        # Generate app initialization
        app_init_js = self._generate_app_initialization(config)
        
        # Substitute into base template
        return base_template.substitute(
            title=title,
            mesh_functions=config["functions"],
            mesh_propagator=mesh_propagator_js,
            app_initialization=app_init_js
        )
    
    def _generate_app_initialization(self, config: Dict[str, Any]) -> str:
        """Generate the main app initialization JavaScript"""
        rjsf_config = {
            "schema": config["schema"],
            "uiSchema": config["uiSchema"],
            "formData": config["initial_values"]
        }
        
        return f"""
        // Initialize RJSF form
        const Form = JSONSchemaForm.default;
        const validator = validator;
        
        const formConfig = {json.dumps(rjsf_config)};
        
        // Create onChange handler that uses mesh propagator
        const onChange = ({{formData}}, id) => {{
            if (id && meshPropagator.reverseMesh[id]) {{
                const newFormData = meshPropagator.propagate(id, formData[id], formData);
                // Update form with new data
                renderForm(newFormData);
            }}
        }};
        
        function renderForm(formData = formConfig.formData) {{
            const element = React.createElement(Form, {{
                schema: formConfig.schema,
                uiSchema: formConfig.uiSchema,
                formData: formData,
                onChange: onChange,
                validator: validator,
                onSubmit: ({{formData}}) => console.log("Data submitted: ", formData)
            }});
            
            ReactDOM.render(element, document.getElementById('rjsf-form'));
        }}
        
        // Initial render
        renderForm();
        """
```

---

## Development Roadmap

### Phase 1: Core Foundation
1. **Basic MeshBuilder class** with configuration generation
2. **Simple template system** using stdlib only
3. **Basic function resolution** for inline JS functions
4. **Core test suite** passing

### Phase 2: Enhanced Features
1. **Plugin system** with auto-detection
2. **Convention system** with prefixes and type inference
3. **External function resolution** (files, URLs)
4. **Enhanced UI widgets** and grouping

### Phase 3: Advanced Functionality
1. **Complex propagation** with cycle detection
2. **Visual form builder** interface
3. **Export to multiple formats**
4. **Performance optimization**

### Phase 4: Ecosystem
1. **Function library marketplace**
2. **Integration with Jupyter notebooks**
3. **Desktop application wrapper**
4. **Cloud deployment options**

---

## Installation and Setup

```bash
# Development installation
git clone <repository>
cd rh
pip install -e .[dev]

# Install playwright for browser testing
playwright install

# Run tests
pytest tests/
```

### Requirements Files

**requirements.txt** (minimal):
```
# Core dependencies (none - uses stdlib)
```

**requirements-dev.txt**:
```
pytest>=7.0.0
playwright>=1.20.0
jinja2>=3.0.0  # Optional enhancement
esbuild>=0.14.0  # Optional JS bundling
```

**pyproject.toml**:
```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mesh-builder"
version = "0.1.0"
description = "Reactive Computation Framework for Interactive Web Applications"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "playwright>=1.20.0",
    "jinja2>=3.0.0",
    "esbuild>=0.14.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

---

This complete specification provides everything needed to implement the Reactive Computation Framework (Mesh Builder). It includes architectural principles, detailed implementation guidance, comprehensive test suites, usage examples, and a clear development roadmap. The framework enables users to transform variable relationships into interactive web applications with minimal configuration while supporting advanced customization through conventions and explicit overrides.