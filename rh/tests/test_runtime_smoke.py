"""
Runtime smoke test using Playwright to verify generated app renders without React errors.
This test launches a headless Chromium, opens the generated index.html, captures console messages,
and asserts there are no React runtime errors and that a form container appears.
"""

import tempfile
import os
from pathlib import Path
from rh import MeshBuilder
from playwright.sync_api import sync_playwright


def test_runtime_form_renders_without_react_errors():
    mesh_spec = {"fahrenheit": ["celsius"], "kelvin": ["celsius"]}

    functions_spec = {
        "fahrenheit": "return celsius * 9/5 + 32;",
        "kelvin": "return celsius + 273.15;",
    }

    initial_values = {"celsius": 25.0}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app(title="Playwright Runtime Smoke Test")
        file_url = Path(app_path).absolute().as_uri()

        console_msgs = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            def on_console(msg):
                try:
                    text = msg.text()
                except Exception:
                    text = str(msg)
                console_msgs.append(text)

            page.on("console", on_console)

            # Open the generated file
            page.goto(file_url)

            # Wait briefly for app to initialize (covers most cases)
            page.wait_for_timeout(1500)

            # Gather console output
            joined = "\n".join(console_msgs)

            # Fail if we see known React minified errors or other render failures
            assert "Minified React error" not in joined, f"React minified error seen in console:\n{joined}"
            assert "Error rendering form" not in joined, f"Form render error seen in console:\n{joined}"

            # Check that some DOM container for the form exists
            form_node = (
                page.query_selector("#rjsf-form")
                or page.query_selector(".simple-form")
                or page.query_selector("form")
            )

            assert form_node is not None, f"No form container found in DOM; console:\n{joined}"

            browser.close()


if __name__ == "__main__":
    test_runtime_form_renders_without_react_errors()
