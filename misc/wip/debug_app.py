"""
Debug script to investigate the white page issue.
"""

from rh import MeshBuilder
import tempfile
from pathlib import Path


def debug_temperature_converter():
    """Debug the temperature converter to see what's being generated."""
    print("🐛 Debugging Temperature Converter...")

    # Same configuration as user's example
    mesh_spec = {
        "temp_fahrenheit": ["temp_celsius"],
        "temp_kelvin": ["temp_celsius"],
    }

    functions_spec = {
        "temp_fahrenheit": "return temp_celsius * 9/5 + 32;",
        "temp_kelvin": "return temp_celsius + 273.15;",
    }

    initial_values = {"temp_celsius": 20.0}

    # Create and build the app
    builder = MeshBuilder(mesh_spec, functions_spec, initial_values)

    # Generate config first to inspect
    config = builder.generate_config()
    print("\n📊 Generated Configuration:")
    print(f"  Schema properties: {list(config['schema']['properties'].keys())}")
    print(f"  UI Schema: {config['uiSchema']}")
    print(f"  Initial values: {config['initial_values']}")
    print(f"  Functions: {len(config['functions'])} chars")

    # Build the app
    with tempfile.TemporaryDirectory() as tmpdir:
        builder.output_dir = tmpdir
        app_path = builder.build_app(title="Temperature Converter")

        print(f"\n📱 App created at: {app_path}")

        # Read and analyze the HTML
        html_content = app_path.read_text()
        print(f"📄 HTML size: {len(html_content)} characters")

        # Check for common issues
        issues = []

        # Check if essential JavaScript is present
        if "React.createElement" not in html_content:
            issues.append("❌ React.createElement not found")
        else:
            print("✅ React.createElement found")

        if "JSONSchemaForm" not in html_content:
            issues.append("❌ JSONSchemaForm not found")
        else:
            print("✅ JSONSchemaForm found")

        if "meshFunctions" not in html_content:
            issues.append("❌ meshFunctions not found")
        else:
            print("✅ meshFunctions found")

        if "renderForm" not in html_content:
            issues.append("❌ renderForm function not found")
        else:
            print("✅ renderForm function found")

        # Check for form configuration
        if "formConfig" not in html_content:
            issues.append("❌ formConfig not found")
        else:
            print("✅ formConfig found")

        # Check for the rjsf-form div
        if 'id="rjsf-form"' not in html_content:
            issues.append("❌ rjsf-form div not found")
        else:
            print("✅ rjsf-form div found")

        if issues:
            print("\n🚨 Issues found:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✅ All checks passed - HTML structure looks correct")

        # Show critical sections of the HTML
        print("\n🔍 Key HTML Sections:")

        # Extract head section
        head_start = html_content.find("<head>")
        head_end = html_content.find("</head>") + 7
        if head_start != -1:
            head_section = html_content[head_start:head_end]
            print("\n  📋 HEAD Section (CDN links):")
            lines = head_section.split('\n')
            for line in lines:
                if 'src=' in line or 'href=' in line:
                    print(f"    {line.strip()}")

        # Extract script sections
        print("\n  📋 JavaScript Sections:")
        script_count = html_content.count('<script>')
        print(f"    Found {script_count} script tags")

        # Show the first few lines of the form initialization
        if "renderForm" in html_content:
            render_start = html_content.find("function renderForm")
            if render_start != -1:
                render_section = html_content[render_start : render_start + 300]
                print(f"\n  📋 renderForm function start:")
                print(f"    {render_section}...")

        # Create a simple test HTML to verify the issue
        test_html = create_minimal_test_html()
        test_path = Path(tmpdir) / "test.html"
        test_path.write_text(test_html)

        print(f"\n🧪 Created minimal test file: {test_path}")
        print("   This should show a simple form to verify React/RJSF loading")

        return app_path, test_path


def create_minimal_test_html():
    """Create a minimal HTML to test if React/RJSF loads correctly."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RH Debug Test</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1>RH Debug Test</h1>
        <div id="react-test">Loading React...</div>
        <div id="rjsf-test">Loading RJSF...</div>
        <div id="form-test">Loading Form...</div>
    </div>

    <!-- React Dependencies -->
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@rjsf/core@5/dist/rjsf-core.umd.js"></script>
    <script src="https://unpkg.com/@rjsf/utils@5/dist/rjsf-utils.umd.js"></script>
    <script src="https://unpkg.com/@rjsf/validator-ajv8@5/dist/rjsf-validator-ajv8.umd.js"></script>
    <script src="https://unpkg.com/@rjsf/bootstrap-4@5/dist/rjsf-bootstrap-4.umd.js"></script>

    <script>
        // Test React loading
        document.getElementById('react-test').innerHTML = 
            typeof React !== 'undefined' ? '✅ React loaded' : '❌ React failed to load';
        
        // Test RJSF loading
        document.getElementById('rjsf-test').innerHTML = 
            typeof JSONSchemaForm !== 'undefined' ? '✅ RJSF loaded' : '❌ RJSF failed to load';
        
        // Test simple form
        if (typeof React !== 'undefined' && typeof JSONSchemaForm !== 'undefined') {
            const Form = JSONSchemaForm.default;
            
            const schema = {
                type: "object",
                properties: {
                    temperature: {type: "number", title: "Temperature"}
                }
            };
            
            const element = React.createElement(Form, {
                schema: schema,
                formData: {temperature: 20},
                onSubmit: (data) => console.log("Form data:", data)
            });
            
            ReactDOM.render(element, document.getElementById('form-test'));
        } else {
            document.getElementById('form-test').innerHTML = '❌ Cannot create form - dependencies missing';
        }
    </script>
</body>
</html>"""


if __name__ == "__main__":
    app_path, test_path = debug_temperature_converter()
    print(f"\n🌐 To debug:")
    print(f"   1. Open: file://{app_path}")
    print(f"   2. Open: file://{test_path}")
    print(f"   3. Check browser console for JavaScript errors (F12)")
    print(f"   4. Try both files to isolate the issue")
