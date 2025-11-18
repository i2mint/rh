"""Validation utilities for mesh specifications and configurations."""

from typing import Dict, Any, List, Set, Tuple


class MeshValidator:
    """Validates mesh specifications for correctness and provides helpful error messages."""

    @staticmethod
    def validate_mesh_spec(
        mesh_spec: Dict[str, Any],
        functions_spec: Dict[str, Any],
        initial_values: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """Validate a complete mesh specification.

        Args:
            mesh_spec: Dictionary mapping function names to their dependencies
            functions_spec: Dictionary mapping function names to their implementations
            initial_values: Dictionary of initial variable values

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate mesh_spec structure
        if not isinstance(mesh_spec, dict):
            errors.append(f"mesh_spec must be a dictionary, got {type(mesh_spec)}")
            return False, errors

        if not isinstance(functions_spec, dict):
            errors.append(
                f"functions_spec must be a dictionary, got {type(functions_spec)}"
            )
            return False, errors

        # Check all functions in mesh have implementations
        for func_name, deps in mesh_spec.items():
            if func_name not in functions_spec:
                errors.append(
                    f"Function '{func_name}' in mesh_spec has no implementation in functions_spec"
                )

            # Validate dependencies list
            if not isinstance(deps, list):
                errors.append(
                    f"Dependencies for '{func_name}' must be a list, got {type(deps)}"
                )

        # Check for undefined dependencies
        all_vars = set(initial_values.keys()) | set(mesh_spec.keys())
        for func_name, deps in mesh_spec.items():
            for dep in deps:
                if dep not in all_vars:
                    errors.append(
                        f"Function '{func_name}' depends on undefined variable '{dep}'"
                    )

        # Check for orphaned functions (in functions_spec but not in mesh_spec or initial_values)
        defined_vars = set(mesh_spec.keys()) | set(initial_values.keys())
        for func_name in functions_spec.keys():
            if func_name not in defined_vars:
                errors.append(
                    f"Warning: Function '{func_name}' defined but never used in mesh or initial values"
                )

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def detect_circular_dependencies(mesh_spec: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies in the mesh.

        Args:
            mesh_spec: Dictionary mapping function names to dependencies

        Returns:
            List of circular dependency chains
        """
        cycles = []

        def dfs(node: str, visited: Set[str], path: List[str]):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if cycle not in cycles:
                    cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            if node in mesh_spec:
                for dep in mesh_spec[node]:
                    if dep in mesh_spec:  # Only follow if it's a computed variable
                        dfs(dep, visited, path.copy())

        for func_name in mesh_spec.keys():
            dfs(func_name, set(), [])

        return cycles

    @staticmethod
    def validate_function_syntax(
        functions_spec: Dict[str, str]
    ) -> Tuple[bool, List[str]]:
        """Basic validation of JavaScript function syntax.

        Args:
            functions_spec: Dictionary mapping function names to JavaScript code

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        for func_name, func_code in functions_spec.items():
            if not isinstance(func_code, str):
                errors.append(
                    f"Function '{func_name}' must be a string, got {type(func_code)}"
                )
                continue

            # Basic checks
            if not func_code.strip():
                errors.append(f"Function '{func_name}' is empty")

            # Check for return statement (recommended but not required)
            if "return" not in func_code:
                errors.append(
                    f"Warning: Function '{func_name}' has no return statement"
                )

            # Check for balanced braces/brackets/parentheses
            if func_code.count("{") != func_code.count("}"):
                errors.append(f"Function '{func_name}' has unbalanced curly braces")
            if func_code.count("(") != func_code.count(")"):
                errors.append(f"Function '{func_name}' has unbalanced parentheses")
            if func_code.count("[") != func_code.count("]"):
                errors.append(f"Function '{func_name}' has unbalanced square brackets")

        is_valid = all("Warning:" in err for err in errors)
        return is_valid, errors

    @staticmethod
    def suggest_fixes(errors: List[str]) -> List[str]:
        """Suggest fixes for common errors.

        Args:
            errors: List of error messages

        Returns:
            List of suggested fixes
        """
        suggestions = []

        for error in errors:
            if "undefined variable" in error:
                suggestions.append(
                    "Add the variable to initial_values or define it as a computed variable in mesh_spec"
                )
            elif "no implementation" in error:
                suggestions.append(
                    "Add the function implementation to functions_spec"
                )
            elif "never used" in error:
                suggestions.append(
                    "Remove unused function or add it to mesh_spec if it should be computed"
                )
            elif "no return statement" in error:
                suggestions.append("Add a return statement to the function")
            elif "unbalanced" in error:
                suggestions.append("Check for missing or extra brackets/braces/parentheses")

        return suggestions


def validate_mesh(
    mesh_spec: Dict[str, Any],
    functions_spec: Dict[str, Any],
    initial_values: Dict[str, Any],
    raise_on_error: bool = False,
) -> bool:
    """Convenience function to validate a mesh specification.

    Args:
        mesh_spec: Dictionary mapping function names to their dependencies
        functions_spec: Dictionary mapping function names to their implementations
        initial_values: Dictionary of initial variable values
        raise_on_error: If True, raise ValueError on validation errors

    Returns:
        True if valid, False otherwise

    Raises:
        ValueError: If validation fails and raise_on_error=True
    """
    validator = MeshValidator()

    # Validate mesh structure
    is_valid, errors = validator.validate_mesh_spec(
        mesh_spec, functions_spec, initial_values
    )

    if not is_valid or errors:
        # Check for circular dependencies
        cycles = validator.detect_circular_dependencies(mesh_spec)
        if cycles:
            errors.append(f"Circular dependencies detected: {cycles}")

        # Validate function syntax
        _, func_errors = validator.validate_function_syntax(functions_spec)
        errors.extend(func_errors)

    if errors:
        error_msg = "\n".join(errors)
        suggestions = validator.suggest_fixes(errors)
        if suggestions:
            error_msg += "\n\nSuggested fixes:\n" + "\n".join(
                f"  - {s}" for s in suggestions
            )

        if raise_on_error:
            raise ValueError(f"Mesh validation failed:\n{error_msg}")
        else:
            print(f"Mesh validation warnings/errors:\n{error_msg}")
            return False

    return True
