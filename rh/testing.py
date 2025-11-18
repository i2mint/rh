"""Testing utilities for mesh logic."""

from typing import Dict, Any, Callable, List
import json


class MeshTester:
    """Utility class for testing mesh logic programmatically.

    This allows testing mesh calculations without building HTML apps.
    """

    def __init__(
        self,
        mesh_spec: Dict[str, List[str]],
        functions_spec: Dict[str, str],
        initial_values: Dict[str, Any],
    ):
        """Initialize mesh tester.

        Args:
            mesh_spec: Dictionary mapping function names to their dependencies
            functions_spec: Dictionary mapping function names to JS-like function bodies
            initial_values: Dictionary of initial variable values
        """
        self.mesh_spec = mesh_spec
        self.functions_spec = functions_spec
        self.initial_values = initial_values.copy()

        # Convert JavaScript functions to Python
        self._compiled_functions = {}
        self._compile_functions()

    def _compile_functions(self):
        """Compile JavaScript-like functions to Python callables."""
        for func_name, js_code in self.functions_spec.items():
            # Simple JS to Python conversion for basic expressions
            # Extract return statement
            if "return " in js_code:
                expr = js_code.split("return ")[1].split(";")[0].strip()
                # Create Python lambda
                deps = self.mesh_spec.get(func_name, [])
                try:
                    # Build parameter list
                    params = ", ".join(deps)
                    # Replace JS operators with Python equivalents
                    python_expr = expr.replace("Math.", "").replace("**", "**")
                    # Create lambda
                    func_str = f"lambda {params}: {python_expr}"
                    self._compiled_functions[func_name] = eval(
                        func_str,
                        {
                            "pow": pow,
                            "sqrt": lambda x: x**0.5,
                            "abs": abs,
                            "min": min,
                            "max": max,
                        },
                    )
                except Exception as e:
                    print(
                        f"Warning: Could not compile function '{func_name}': {e}"
                    )
                    # Fallback to identity
                    self._compiled_functions[func_name] = lambda *args: (
                        args[0] if args else 0
                    )

    def compute(self, values: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compute all derived values from given input values.

        Args:
            values: Input values (if None, uses initial_values)

        Returns:
            Dictionary with all computed values
        """
        if values is None:
            values = self.initial_values.copy()
        else:
            values = {**self.initial_values, **values}

        result = values.copy()

        # Iteratively compute all functions (handles dependencies)
        max_iterations = 50
        for _ in range(max_iterations):
            changed = False
            for func_name, deps in self.mesh_spec.items():
                if func_name in self._compiled_functions:
                    try:
                        # Get dependency values
                        dep_values = [result.get(dep, 0) for dep in deps]
                        # Compute
                        new_value = self._compiled_functions[func_name](*dep_values)
                        # Update if changed
                        if result.get(func_name) != new_value:
                            result[func_name] = new_value
                            changed = True
                    except Exception as e:
                        print(f"Error computing '{func_name}': {e}")

            if not changed:
                break

        return result

    def test_value(
        self, input_var: str, input_value: Any, expected_outputs: Dict[str, Any]
    ) -> bool:
        """Test that a given input produces expected outputs.

        Args:
            input_var: Name of the input variable
            input_value: Value to set for the input
            expected_outputs: Dictionary of expected output values

        Returns:
            True if all outputs match, False otherwise
        """
        result = self.compute({input_var: input_value})

        all_match = True
        for output_var, expected_value in expected_outputs.items():
            actual_value = result.get(output_var)
            if abs(actual_value - expected_value) > 0.0001:  # Tolerance for floats
                print(
                    f"❌ {output_var}: expected {expected_value}, got {actual_value}"
                )
                all_match = False
            else:
                print(f"✓ {output_var}: {actual_value}")

        return all_match

    def test_range(
        self,
        input_var: str,
        start: float,
        end: float,
        step: float,
        validator: Callable[[Dict[str, Any]], bool],
    ) -> List[Dict[str, Any]]:
        """Test a range of input values with a custom validator.

        Args:
            input_var: Name of the input variable
            start: Start of range
            end: End of range
            step: Step size
            validator: Function that takes computed values and returns True if valid

        Returns:
            List of test results
        """
        results = []
        current = start
        while current <= end:
            computed = self.compute({input_var: current})
            is_valid = validator(computed)
            results.append(
                {
                    "input": current,
                    "output": computed,
                    "valid": is_valid,
                }
            )
            current += step

        return results

    def generate_test_cases(
        self, num_cases: int = 10, seed: int = 42
    ) -> List[Dict[str, Any]]:
        """Generate random test cases for the mesh.

        Args:
            num_cases: Number of test cases to generate
            seed: Random seed for reproducibility

        Returns:
            List of test case dictionaries
        """
        import random

        random.seed(seed)

        test_cases = []
        # Get input variables (those not in mesh_spec)
        input_vars = set(self.initial_values.keys()) - set(self.mesh_spec.keys())

        for _ in range(num_cases):
            # Generate random inputs
            inputs = {}
            for var in input_vars:
                initial = self.initial_values.get(var, 0)
                # Generate value in range [initial/2, initial*2]
                if isinstance(initial, (int, float)) and initial != 0:
                    inputs[var] = random.uniform(initial * 0.5, initial * 2)
                else:
                    inputs[var] = random.uniform(-100, 100)

            # Compute outputs
            outputs = self.compute(inputs)

            test_cases.append({"inputs": inputs, "outputs": outputs})

        return test_cases

    def export_test_cases(
        self, test_cases: List[Dict[str, Any]], filepath: str
    ) -> None:
        """Export test cases to a JSON file.

        Args:
            test_cases: List of test case dictionaries
            filepath: Path to output file
        """
        with open(filepath, "w") as f:
            json.dump(test_cases, f, indent=2)
        print(f"✓ Exported {len(test_cases)} test cases to {filepath}")

    def import_test_cases(self, filepath: str) -> List[Dict[str, Any]]:
        """Import test cases from a JSON file.

        Args:
            filepath: Path to input file

        Returns:
            List of test case dictionaries
        """
        with open(filepath) as f:
            test_cases = json.load(f)
        print(f"✓ Imported {len(test_cases)} test cases from {filepath}")
        return test_cases

    def validate_test_cases(
        self, test_cases: List[Dict[str, Any]], tolerance: float = 0.0001
    ) -> bool:
        """Validate a list of test cases.

        Args:
            test_cases: List of test case dictionaries
            tolerance: Tolerance for floating point comparisons

        Returns:
            True if all test cases pass
        """
        all_pass = True
        for i, case in enumerate(test_cases):
            inputs = case["inputs"]
            expected_outputs = case["outputs"]

            actual_outputs = self.compute(inputs)

            case_pass = True
            for var, expected in expected_outputs.items():
                actual = actual_outputs.get(var)
                if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                    if abs(actual - expected) > tolerance:
                        print(
                            f"❌ Case {i+1}, {var}: expected {expected}, got {actual}"
                        )
                        case_pass = False
                elif actual != expected:
                    print(f"❌ Case {i+1}, {var}: expected {expected}, got {actual}")
                    case_pass = False

            if case_pass:
                print(f"✓ Test case {i+1} passed")
            else:
                all_pass = False

        return all_pass


def quick_test(
    mesh_spec: Dict[str, List[str]],
    functions_spec: Dict[str, str],
    initial_values: Dict[str, Any],
    test_inputs: Dict[str, Any],
) -> Dict[str, Any]:
    """Quick one-shot test of a mesh configuration.

    Args:
        mesh_spec: Mesh specification
        functions_spec: Function implementations
        initial_values: Initial values
        test_inputs: Input values to test

    Returns:
        Computed output values
    """
    tester = MeshTester(mesh_spec, functions_spec, initial_values)
    return tester.compute(test_inputs)
