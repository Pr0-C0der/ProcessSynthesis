import json
import os
from typing import Any, Dict, List


INPUT_DIR = "example_pde_jsons"


def expr_to_str(node: Dict[str, Any]) -> str:
    """
    Convert an expression-tree node (op/deriv/dep/param/const/fn/var) into a readable string.
    This is a simple pretty-printer; you can refine formatting later.
    """
    node_type = node.get("type")

    if node_type == "deriv":
        dep = node["dep"]
        wrt = node["wrt"]
        order = node.get("order", 1)
        if order == 1:
            return f"∂{dep}/∂{wrt}"
        else:
            return f"∂^{order}{dep}/∂{wrt}^{order}"

    if node_type == "dep":
        return node["name"]

    if node_type == "param":
        return node["name"]

    if node_type == "const":
        return str(node["value"])

    if node_type == "var":
        return node["name"]

    if node_type == "fn":
        name = node["name"]
        args = ", ".join(expr_to_str(a) for a in node.get("args", []))
        return f"{name}({args})"

    if node_type == "op":
        op = node["op"]
        args: List[Dict[str, Any]] = node.get("args", [])
        # Binary infix operators
        if op in {"+", "-", "*", "/", "^"} and len(args) == 2:
            left = expr_to_str(args[0])
            right = expr_to_str(args[1])
            if op == "*":
                return f"({left} {right})"
            if op == "^":
                return f"({left}^{right})"
            return f"({left} {op} {right})"
        # Generic op: join arguments
        inner = ", ".join(expr_to_str(a) for a in args)
        return f"{op}({inner})"

    return "<?>"


def classify_equation(eq_id: str) -> str:
    """
    Classify an equation_id into 'pde', 'boundary', or 'initial'.
    Uses naming conventions seen in the generated JSONs.
    """
    lower = eq_id.lower()
    if "boundary" in lower:
        return "boundary"
    if "initial" in lower:
        return "initial"
    if "bc" in lower:
        return "boundary"
    if "ic" in lower:
        return "initial"
    return "pde"


def print_pde_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data.get("metadata", {})
    name = metadata.get("name", os.path.basename(path))
    description = metadata.get("description")
    
    print(f"\n=== {name} ===")
    if description:
        print(f"Description: {description}")

    # Print variables
    variables = data.get("variables", {})
    if variables:
        indep = variables.get("independent", [])
        dep = variables.get("dependent", [])
        if indep:
            print(f"Independent variables: {', '.join(indep)}")
        if dep:
            print(f"Dependent variables: {', '.join(dep)}")

    # Print parameters with their values
    parameters = data.get("parameters", {})
    if parameters:
        param_strs = []
        for param_name, param_value in parameters.items():
            if param_value is None:
                param_strs.append(f"{param_name} (unspecified)")
            else:
                param_strs.append(f"{param_name} = {param_value}")
        if param_strs:
            print(f"Parameters: {', '.join(param_strs)}")

    # Optional: print domain information if present.
    domain = data.get("domain")
    if domain:
        print("Domain:")
        for var, interval in domain.items():
            if isinstance(interval, list) and len(interval) == 2:
                a, b = interval
                a_str = expr_to_str(a) if isinstance(a, dict) else str(a)
                b_str = expr_to_str(b) if isinstance(b, dict) else str(b)
                print(f"  {var} ∈ [{a_str}, {b_str}]")
        print()

    pdes = data.get("pdes", [])
    main_pdes = []
    boundaries = []
    initials = []

    for eq in pdes:
        eq_id = eq.get("equation_id", "unknown")
        lhs = expr_to_str(eq.get("lhs", {}))
        rhs = expr_to_str(eq.get("rhs", {}))
        eq_str = f"{lhs} = {rhs}"

        category = classify_equation(eq_id)
        if category == "pde":
            main_pdes.append((eq_id, eq_str))
        elif category == "boundary":
            boundaries.append((eq_id, eq_str))
        else:
            initials.append((eq_id, eq_str))

    print("\nPDE(s):")
    for eq_id, eq_str in main_pdes:
        print(f"  [{eq_id}]  {eq_str}")

    print("\nBoundary condition(s) (from 'pdes'):")
    for eq_id, eq_str in boundaries:
        print(f"  [{eq_id}]  {eq_str}")

    print("\nInitial condition(s) (from 'pdes'):")
    for eq_id, eq_str in initials:
        print(f"  [{eq_id}]  {eq_str}")

    # Also handle top-level initial_conditions / boundary_conditions, if present.
    top_ics = data.get("initial_conditions", [])
    top_bcs = data.get("boundary_conditions", [])

    if top_ics:
        print("\nInitial condition(s) (from 'initial_conditions'):")
        for ic in top_ics:
            dep = ic.get("dep", "?")
            ic_type = ic.get("type", "ic")
            loc = ic.get("location", {})
            val_expr = expr_to_str(ic.get("value_expr", {}))
            notes = ic.get("notes", "")
            
            # Format location nicely
            if isinstance(loc, dict):
                loc_parts = [f"{k}={v}" for k, v in loc.items()]
                loc_str = ", ".join(loc_parts) if loc_parts else "?"
            else:
                loc_str = str(loc)
            
            ic_line = f"  [{ic_type}] {dep} at {loc_str}: {val_expr}"
            if notes:
                ic_line += f" ({notes})"
            print(ic_line)

    if top_bcs:
        print("\nBoundary condition(s) (from 'boundary_conditions'):")
        for bc in top_bcs:
            dep = bc.get("dep", "?")
            bc_type = bc.get("type", "?")
            spec = bc.get("spec", {})
            val_expr = expr_to_str(bc.get("value_expr", {}))
            notes = bc.get("notes", "")
            
            # Format spec nicely
            if isinstance(spec, str):
                spec_str = spec
            elif isinstance(spec, dict):
                spec_parts = [f"{k}={v}" for k, v in spec.items()]
                spec_str = ", ".join(spec_parts) if spec_parts else "?"
            else:
                spec_str = str(spec)
            
            bc_line = f"  [{bc_type}] {dep} at {spec_str}: {val_expr}"
            if notes:
                bc_line += f" ({notes})"
            print(bc_line)


def main() -> None:
    """
    Parse all JSON files in example_pde_jsons and print the PDE, initial
    conditions, and boundary conditions in a readable form.
    """
    if not os.path.isdir(INPUT_DIR):
        raise RuntimeError(f"Directory '{INPUT_DIR}' does not exist.")

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    if not files:
        print(f"No JSON files found in '{INPUT_DIR}'.")
        return

    for filename in sorted(files):
        full_path = os.path.join(INPUT_DIR, filename)
        print_pde_file(full_path)


if __name__ == "__main__":
    main()


