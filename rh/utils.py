"""Utility functions for mesh visualization, debugging, and helpers."""

from typing import Dict, List, Any, Set
import json


def visualize_mesh(mesh_spec: Dict[str, List[str]], initial_values: Dict[str, Any] = None) -> str:
    """Generate a simple text-based visualization of the mesh structure.

    Args:
        mesh_spec: Dictionary mapping function names to their dependencies
        initial_values: Dictionary of initial variable values

    Returns:
        String representation of the mesh structure
    """
    lines = []
    lines.append("=" * 60)
    lines.append("MESH STRUCTURE")
    lines.append("=" * 60)

    # Identify input variables (in initial_values but not computed)
    initial_values = initial_values or {}
    input_vars = set(initial_values.keys()) - set(mesh_spec.keys())
    computed_vars = set(mesh_spec.keys())

    # Show input variables
    if input_vars:
        lines.append("\n📥 INPUT VARIABLES:")
        for var in sorted(input_vars):
            value = initial_values.get(var, "?")
            lines.append(f"  • {var} = {value}")

    # Show computed variables and their dependencies
    if computed_vars:
        lines.append("\n⚙️  COMPUTED VARIABLES:")
        for var in sorted(computed_vars):
            deps = mesh_spec[var]
            deps_str = ", ".join(deps) if deps else "(no deps)"
            lines.append(f"  • {var} ← [{deps_str}]")

    # Build reverse dependencies for better understanding
    reverse_deps: Dict[str, List[str]] = {}
    for func, deps in mesh_spec.items():
        for dep in deps:
            if dep not in reverse_deps:
                reverse_deps[dep] = []
            reverse_deps[dep].append(func)

    # Show reverse dependencies (what depends on each variable)
    lines.append("\n🔄 PROPAGATION CHAINS:")
    all_vars = sorted(input_vars | computed_vars)
    for var in all_vars:
        dependents = reverse_deps.get(var, [])
        if dependents:
            deps_str = ", ".join(sorted(dependents))
            lines.append(f"  • {var} → affects: {deps_str}")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


def export_config(
    mesh_spec: Dict[str, Any],
    functions_spec: Dict[str, Any],
    initial_values: Dict[str, Any],
    filepath: str,
    **kwargs
) -> None:
    """Export mesh configuration to a JSON file.

    Args:
        mesh_spec: Dictionary mapping function names to their dependencies
        functions_spec: Dictionary mapping function names to their implementations
        initial_values: Dictionary of initial variable values
        filepath: Path to output JSON file
        **kwargs: Additional configuration options (field_overrides, ui_config, meta, etc.)
    """
    config = {
        "mesh_spec": mesh_spec,
        "functions_spec": functions_spec,
        "initial_values": initial_values,
    }

    config.update(kwargs)

    with open(filepath, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✓ Configuration exported to: {filepath}")


def import_config(filepath: str) -> Dict[str, Any]:
    """Import mesh configuration from a JSON file.

    Args:
        filepath: Path to input JSON file

    Returns:
        Dictionary with configuration
    """
    with open(filepath) as f:
        config = json.load(f)

    required_keys = ["mesh_spec", "functions_spec"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Config file must contain '{key}' key")

    return config


def analyze_mesh_complexity(mesh_spec: Dict[str, List[str]]) -> Dict[str, Any]:
    """Analyze mesh complexity metrics.

    Args:
        mesh_spec: Dictionary mapping function names to their dependencies

    Returns:
        Dictionary with complexity metrics
    """
    metrics = {
        "total_functions": len(mesh_spec),
        "total_dependencies": sum(len(deps) for deps in mesh_spec.values()),
        "max_dependencies": max((len(deps) for deps in mesh_spec.values()), default=0),
        "average_dependencies": 0.0,
        "variables_with_no_deps": 0,
        "deepest_chain": 0,
    }

    if metrics["total_functions"] > 0:
        metrics["average_dependencies"] = (
            metrics["total_dependencies"] / metrics["total_functions"]
        )

    # Count functions with no dependencies
    metrics["variables_with_no_deps"] = sum(
        1 for deps in mesh_spec.values() if len(deps) == 0
    )

    # Calculate deepest dependency chain
    def get_depth(var: str, visited: Set[str] = None) -> int:
        if visited is None:
            visited = set()
        if var in visited or var not in mesh_spec:
            return 0
        visited.add(var)
        if not mesh_spec[var]:
            return 1
        return 1 + max((get_depth(dep, visited.copy()) for dep in mesh_spec[var]), default=0)

    metrics["deepest_chain"] = max((get_depth(var) for var in mesh_spec), default=0)

    return metrics


def generate_mesh_graph_dot(mesh_spec: Dict[str, List[str]], initial_values: Dict[str, Any] = None) -> str:
    """Generate a Graphviz DOT representation of the mesh.

    Args:
        mesh_spec: Dictionary mapping function names to their dependencies
        initial_values: Dictionary of initial variable values

    Returns:
        DOT format string that can be used with Graphviz
    """
    initial_values = initial_values or {}
    lines = ["digraph Mesh {"]
    lines.append("  rankdir=LR;")
    lines.append("  node [shape=box, style=filled];")

    # Identify input vs computed variables
    input_vars = set(initial_values.keys()) - set(mesh_spec.keys())
    computed_vars = set(mesh_spec.keys())

    # Style input variables differently
    for var in input_vars:
        lines.append(f'  "{var}" [fillcolor=lightblue, label="{var}\\n(input)"];')

    # Style computed variables
    for var in computed_vars:
        lines.append(f'  "{var}" [fillcolor=lightgreen, label="{var}\\n(computed)"];')

    # Add edges
    for func, deps in mesh_spec.items():
        for dep in deps:
            lines.append(f'  "{dep}" -> "{func}";')

    lines.append("}")

    return "\n".join(lines)


def debug_mesh(mesh_spec: Dict[str, Any], functions_spec: Dict[str, Any], initial_values: Dict[str, Any]) -> None:
    """Print debug information about a mesh configuration.

    Args:
        mesh_spec: Dictionary mapping function names to their dependencies
        functions_spec: Dictionary mapping function names to their implementations
        initial_values: Dictionary of initial variable values
    """
    print("\n" + "=" * 70)
    print("MESH DEBUG INFORMATION")
    print("=" * 70)

    print("\n📊 COMPLEXITY METRICS:")
    metrics = analyze_mesh_complexity(mesh_spec)
    for key, value in metrics.items():
        formatted_key = key.replace("_", " ").title()
        print(f"  • {formatted_key}: {value}")

    print(visualize_mesh(mesh_spec, initial_values))

    print("\n💻 FUNCTION IMPLEMENTATIONS:")
    for func_name in sorted(functions_spec.keys()):
        code = functions_spec[func_name]
        preview = code[:60] + "..." if len(code) > 60 else code
        print(f"  • {func_name}: {preview}")

    print("\n" + "=" * 70)


def get_execution_order(mesh_spec: Dict[str, List[str]]) -> List[List[str]]:
    """Determine the execution order for mesh functions using topological sort.

    Args:
        mesh_spec: Dictionary mapping function names to their dependencies

    Returns:
        List of levels, where each level contains variables that can be computed in parallel
    """
    # Calculate in-degree for each variable
    in_degree = {var: 0 for var in mesh_spec}
    for deps in mesh_spec.values():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] += 1

    # Find variables with no incoming edges
    levels = []
    current_level = [var for var, degree in in_degree.items() if degree == 0]

    while current_level:
        levels.append(sorted(current_level))
        next_level = []

        for var in current_level:
            # For each variable that depends on the current var
            for func, deps in mesh_spec.items():
                if var in deps:
                    in_degree[func] -= 1
                    if in_degree[func] == 0:
                        next_level.append(func)

        current_level = next_level

    return levels
