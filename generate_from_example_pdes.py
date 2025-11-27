import json
import os
from typing import Any, Dict, List

from generate_pde_jsons import convert_pde_to_json_file


EXAMPLE_PDES_PATH = "random_pde_list.json"


def build_description(entry: Dict[str, Any]) -> str:
    """
    Turn one entry from example_pdes.json into a textual description
    suitable for convert_pde_to_json_file.
    """
    name = entry.get("name", "unnamed_pde")
    variables = entry.get("variables", {})

    indep: List[str] = variables.get("independent", [])
    dep: List[str] = variables.get("dependent", [])
    params_from_variables: List[str] = variables.get("parameters", [])

    equation = entry.get("equation", "")

    # Optional extra information that may be provided in example_pdes.json
    domain = entry.get("domain")  # can be a dict or a descriptive string like "[0,1]^2"
    # Support both legacy 'initial_conditions' (list) and current 'initial_condition' (string)
    initial_conditions_raw = entry.get("initial_conditions")
    if initial_conditions_raw is None:
        initial_conditions_raw = entry.get("initial_condition")
    # Normalize to list of strings if present
    if isinstance(initial_conditions_raw, str):
        initial_conditions = [initial_conditions_raw]
    else:
        initial_conditions = initial_conditions_raw
    boundary_conditions = entry.get("boundary_conditions")  # list of strings or objects
    parameters_obj = entry.get("parameters")  # new structured parameters dict in example_pdes.json
    parameters_values = entry.get("parameters_values")  # legacy free-text like "D=0.01,r=1.0"

    parts: List[str] = []
    # Only give a high-level PDE name; let the model infer variables/parameters
    # from the equation, ICs, BCs, and any parameter-value hints.
    parts.append(f"PDE name: {name}.")

    # Domain: either use explicitly provided domain or assume a reasonable default.
    if isinstance(domain, dict):
        domain_strs: List[str] = []
        for var, interval in domain.items():
            if isinstance(interval, list) and len(interval) == 2:
                a, b = interval
                domain_strs.append(f"{var} ∈ [{a}, {b}]")
        if domain_strs:
            parts.append("Domain: " + "; ".join(domain_strs) + ".")
    elif isinstance(domain, str):
        # Descriptive domain like "[0,1]^2" – pass through as guidance.
        parts.append(
            "Domain description from data (convert this into a structured 'domain' JSON object): "
            + domain
        )
    else:
        # Heuristic default domain if none is given.
        default_pieces: List[str] = []
        for var in indep:
            if var.lower() in {"t", "time"}:
                default_pieces.append(f"{var} ∈ [0, 1]")
            else:
                default_pieces.append(f"{var} ∈ [0, 1]")
        if default_pieces:
            parts.append(
                "Assume the following default domain for the independent variables (encode this in the JSON 'domain' field): "
                + "; ".join(default_pieces)
                + "."
            )

    parts.append(
        "The PDE system, written in a compact symbolic notation using subscripts for derivatives, is:\n"
        f"{equation}"
    )

    # Optional ICs/BCs: we just forward them as text instructions to the model.
    if initial_conditions:
        parts.append("Initial conditions (to be encoded under 'initial_conditions' in JSON):")
        for ic in initial_conditions:
            parts.append(f"- {ic}")

    if boundary_conditions:
        parts.append("Boundary conditions (to be encoded under 'boundary_conditions' in JSON):")
        for bc in boundary_conditions:
            parts.append(f"- {bc}")

    # Optional parameter information / example settings.
    # Prefer the structured 'parameters' dict from example_pdes.json when present.
    if isinstance(parameters_obj, dict) and parameters_obj:
        parts.append(
            "Parameter definitions / values (encode these under the JSON 'parameters' field):"
        )
        for pname, pval in parameters_obj.items():
            parts.append(f"- {pname} = {pval}")
    elif parameters_values:
        parts.append(
            "Example or default parameter values (encode these under the appropriate 'parameters' or auxiliary fields in JSON):"
        )
        parts.append(f"- {parameters_values}")

    parts.append(
        "Convert this PDE (or PDE system) into the JSON operator-tree format following the Navier–Stokes example with "
        "keys 'metadata', 'variables', 'parameters', optional 'domain', 'pdes', 'initial_conditions', and "
        "'boundary_conditions'. Use expression trees for 'lhs', 'rhs', and any 'value_expr' fields."
    )

    return "\n".join(parts)


def main() -> None:
    if not os.path.isfile(EXAMPLE_PDES_PATH):
        raise FileNotFoundError(f"Could not find {EXAMPLE_PDES_PATH}")

    with open(EXAMPLE_PDES_PATH, "r", encoding="utf-8") as f:
        examples: List[Dict[str, Any]] = json.load(f)

    for entry in examples:
        name = entry.get("name", "unnamed_pde")
        desc = build_description(entry)
        print(f"Generating JSON for {name!r}...")
        output_path = convert_pde_to_json_file(name, desc)
        print(f"  Saved to {output_path}")


if __name__ == "__main__":
    main()


