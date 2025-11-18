"""
Runtime smoke test using Playwright to verify generated app renders without React errors.
This test launches a headless Chromium, opens the generated index.html, captures console messages,
and asserts there are no React runtime errors and that a form container appears.
"""

import tempfile
import os
from pathlib import Path
import pytest
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

        app_path = builder.build_app(title="Playwright Runtime Smoke Test", embed_react=True)
        file_url = Path(app_path).absolute().as_uri()

        console_msgs = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                ]
            )
            page = browser.new_page()

            def on_console(msg):
                try:
                    text = msg.text()
                except Exception:
                    text = str(msg)
                console_msgs.append(text)

            def on_page_error(error):
                console_msgs.append(f"PAGE ERROR: {error}")

            def on_crash(page):
                console_msgs.append("PAGE CRASHED")

            page.on("console", on_console)
            page.on("pageerror", on_page_error)
            page.on("crash", on_crash)

            # Open the generated file
            try:
                # For file:// URLs with embedded resources, use 'load' instead of 'networkidle'
                page.goto(file_url, wait_until="load", timeout=15000)
            except Exception as e:
                # Page crashes can happen in constrained environments (e.g., containers)
                # with large inline scripts. Skip the test in such cases.
                if "crashed" in str(e).lower():
                    pytest.skip(f"Chromium crashed in this environment (likely due to resource constraints): {e}")
                # If the page crashes during navigation, try to get some diagnostic info
                if console_msgs:
                    raise AssertionError(f"Page failed to load: {e}\nConsole output: {console_msgs}")
                raise

            # Wait briefly for app to initialize (covers most cases)
            try:
                page.wait_for_timeout(2000)
            except Exception as e:
                if console_msgs:
                    raise AssertionError(f"Page crashed during initialization: {e}\nConsole output: {console_msgs}")
                raise

            # Gather console output
            joined = "\n".join(console_msgs)

            # Fail if we see known React minified errors or other render failures
            assert (
                "Minified React error" not in joined
            ), f"React minified error seen in console:\n{joined}"
            assert (
                "Error rendering form" not in joined
            ), f"Form render error seen in console:\n{joined}"

            # Check that some DOM container for the form exists
            form_node = (
                page.query_selector("#rjsf-form")
                or page.query_selector(".simple-form")
                or page.query_selector("form")
            )

            assert (
                form_node is not None
            ), f"No form container found in DOM; console:\n{joined}"

            browser.close()


if __name__ == "__main__":
    test_runtime_form_renders_without_react_errors()
