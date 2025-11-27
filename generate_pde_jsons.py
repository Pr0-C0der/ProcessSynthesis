import os
import json
from typing import Dict

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment or .env file.")

client = OpenAI(api_key=api_key)

OUTPUT_DIR = "random_pde_jsons"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# This is the example PDE JSON structure you provided, with PDEs + ICs/BCs.
EXAMPLE_SCHEMA: Dict = {
    "metadata": {
        "name": "2D Incompressible Navier–Stokes (u,v,p) - full system with ICs/BCs",
        "description": "System of three PDEs: u-momentum, v-momentum, and incompressible continuity in (x,y,t), with initial and boundary conditions.",
    },
    "variables": {
        "independent": ["x", "y", "t"],
        "dependent": ["u", "v", "p"],
    },
    "parameters": {
        "nu": None,
    },
    "domain": {
        "x": [0.0, 1.0],
        "y": [0.0, 1.0],
        "t": [0.0, 1.0],
    },
    "pdes": [
        {
            "equation_id": "u_momentum",
            "type": "equals",
            "lhs": {
                "type": "op",
                "op": "+",
                "args": [
                    {"type": "deriv", "dep": "u", "wrt": "t", "order": 1},
                    {
                        "type": "op",
                        "op": "+",
                        "args": [
                            {
                                "type": "op",
                                "op": "*",
                                "args": [
                                    {"type": "dep", "name": "u"},
                                    {"type": "deriv", "dep": "u", "wrt": "x", "order": 1},
                                ],
                            },
                            {
                                "type": "op",
                                "op": "*",
                                "args": [
                                    {"type": "dep", "name": "v"},
                                    {"type": "deriv", "dep": "u", "wrt": "y", "order": 1},
                                ],
                            },
                        ],
                    },
                ],
            },
            "rhs": {
                "type": "op",
                "op": "+",
                "args": [
                    {
                        "type": "op",
                        "op": "*",
                        "args": [
                            {"type": "const", "value": -1},
                            {"type": "deriv", "dep": "p", "wrt": "x", "order": 1},
                        ],
                    },
                    {
                        "type": "op",
                        "op": "*",
                        "args": [
                            {"type": "param", "name": "nu"},
                            {
                                "type": "op",
                                "op": "+",
                                "args": [
                                    {"type": "deriv", "dep": "u", "wrt": "x", "order": 2},
                                    {"type": "deriv", "dep": "u", "wrt": "y", "order": 2},
                                ],
                            },
                        ],
                    },
                ],
            },
        },
        {
            "equation_id": "v_momentum",
            "type": "equals",
            "lhs": {
                "type": "op",
                "op": "+",
                "args": [
                    {"type": "deriv", "dep": "v", "wrt": "t", "order": 1},
                    {
                        "type": "op",
                        "op": "+",
                        "args": [
                            {
                                "type": "op",
                                "op": "*",
                                "args": [
                                    {"type": "dep", "name": "u"},
                                    {"type": "deriv", "dep": "v", "wrt": "x", "order": 1},
                                ],
                            },
                            {
                                "type": "op",
                                "op": "*",
                                "args": [
                                    {"type": "dep", "name": "v"},
                                    {"type": "deriv", "dep": "v", "wrt": "y", "order": 1},
                                ],
                            },
                        ],
                    },
                ],
            },
            "rhs": {
                "type": "op",
                "op": "+",
                "args": [
                    {
                        "type": "op",
                        "op": "*",
                        "args": [
                            {"type": "const", "value": -1},
                            {"type": "deriv", "dep": "p", "wrt": "y", "order": 1},
                        ],
                    },
                    {
                        "type": "op",
                        "op": "*",
                        "args": [
                            {"type": "param", "name": "nu"},
                            {
                                "type": "op",
                                "op": "+",
                                "args": [
                                    {"type": "deriv", "dep": "v", "wrt": "x", "order": 2},
                                    {"type": "deriv", "dep": "v", "wrt": "y", "order": 2},
                                ],
                            },
                        ],
                    },
                ],
            },
        },
        {
            "equation_id": "continuity",
            "type": "equals",
            "lhs": {
                "type": "op",
                "op": "+",
                "args": [
                    {"type": "deriv", "dep": "u", "wrt": "x", "order": 1},
                    {"type": "deriv", "dep": "v", "wrt": "y", "order": 1},
                ],
            },
            "rhs": {"type": "const", "value": 0},
        },
    ],
    "initial_conditions": [
        {
            "type": "ic",
            "dep": "u",
            "location": {"t": 0.0},
            "value_expr": {
                "type": "fn",
                "name": "u0",
                "args": [
                    {"type": "var", "name": "x"},
                    {"type": "var", "name": "y"},
                ],
            },
        },
        {
            "type": "ic",
            "dep": "v",
            "location": {"t": 0.0},
            "value_expr": {
                "type": "fn",
                "name": "v0",
                "args": [
                    {"type": "var", "name": "x"},
                    {"type": "var", "name": "y"},
                ],
            },
        },
        {
            "type": "ic",
            "dep": "p",
            "location": {"t": 0.0},
            "value_expr": {
                "type": "fn",
                "name": "p0",
                "args": [
                    {"type": "var", "name": "x"},
                    {"type": "var", "name": "y"},
                ],
            },
        },
    ],
    "boundary_conditions": [
        {
            "type": "dirichlet",
            "dep": "u",
            "spec": "boundary",
            "value_expr": {"type": "const", "value": 0.0},
            "notes": "no-slip: u = 0 on spatial boundary",
        },
        {
            "type": "dirichlet",
            "dep": "v",
            "spec": "boundary",
            "value_expr": {"type": "const", "value": 0.0},
            "notes": "no-slip: v = 0 on spatial boundary",
        },
        {
            "type": "dirichlet",
            "dep": "p",
            "spec": {"x": 0.0, "y": 0.0},
            "value_expr": {"type": "const", "value": 0.0},
            "notes": "pressure reference to fix gauge: p(0,0,t)=0",
        },
    ],
}


def convert_pde_to_json_file(pde_name: str, pde_description: str) -> str:
    """
    Use GPT‑5.1 to convert a PDE description into a JSON object following EXAMPLE_SCHEMA,
    then save it under OUTPUT_DIR with filename `<pde_name>.json`.
    """
    system_prompt = (
        "You are an expert in partial differential equations and symbolic expression trees. "
        "Convert PDE descriptions into a structured JSON object following the example "
        "Navier–Stokes JSON schema with PDEs, initial conditions, and boundary conditions. "
        "Use the same operator-tree style for 'lhs', 'rhs', and 'value_expr' expressions. "
        "Respond with VALID JSON ONLY, no Markdown, no explanations."
    )

    user_prompt = (
        "Convert the given PDE into JSON format. Use the SAME structure as the example below:\n"
        "- Top-level keys: at least 'metadata', 'variables', 'parameters', 'pdes'. You may also include 'domain', 'initial_conditions', and 'boundary_conditions'.\n"
        "- Each PDE in 'pdes' has 'equation_id', 'type', 'lhs', 'rhs'.\n"
        "- 'lhs' and 'rhs' are expression trees built using 'op', 'deriv', 'dep', 'param', 'const', and optionally 'fn'/'var'.\n"
        "- Initial and boundary conditions, when present, use 'value_expr' nodes that follow the same expression-tree conventions.\n\n"
        "IMPORTANT INSTRUCTIONS:\n"
        " - Follow the schema closely but adapt field values to this PDE.\n"
        " - If some information is missing, use null or a short best-guess description.\n"
        " - Do NOT include any text outside the JSON object.\n\n"
        "Example JSON schema:\n"
        f"{json.dumps(EXAMPLE_SCHEMA, indent=2)}\n\n"
        "Now convert this PDE description into JSON:\n"
        f"{pde_description}\n"
    )

    # Print the exact prompt sent to the model for transparency/debugging.
    print("\n" + "=" * 80)
    print(f"MODEL INPUT for PDE '{pde_name}':")
    print("-" * 80)
    print("System message:")
    print(system_prompt)
    print("-" * 80)
    print("User message:")
    print(user_prompt)
    print("=" * 80 + "\n")

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        # temperature=0.1,
    )

    content = response.choices[0].message.content.strip()

    # Try to be robust to occasional code fences.
    if content.startswith("```"):
        # Strip possible Markdown fences like ```json ... ```
        parts = content.split("```")
        # Take the largest non-empty chunk as the JSON candidate
        candidates = [p.strip() for p in parts if p.strip()]
        if candidates:
            content = max(candidates, key=len)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON. Raw content:\n{content}") from e

    output_path = os.path.join(OUTPUT_DIR, f"{pde_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return output_path


def main() -> None:
    """
    Simple example: generate JSON representations for a few PDEs.
    Edit the `pdes` dictionary as needed for your dataset.
    """
    pdes: Dict[str, str] = {
        "heat_equation_1d": (
            "The one-dimensional heat equation on a rod of length L:\n"
            "∂u/∂t = α ∂²u/∂x² for 0 < x < L, t > 0.\n"
            "Boundary conditions: u(0, t) = 0, u(L, t) = 0.\n"
            "Initial condition: u(x, 0) = f(x)."
        ),
        "wave_equation_1d": (
            "The one-dimensional wave equation:\n"
            "∂²u/∂t² = c² ∂²u/∂x² on 0 < x < L, t > 0.\n"
            "Boundary conditions: u(0, t) = 0, u(L, t) = 0.\n"
            "Initial conditions: u(x, 0) = g(x), ∂u/∂t(x, 0) = h(x)."
        ),
    }

    for name, desc in pdes.items():
        path = convert_pde_to_json_file(name, desc)
        print(f"Saved JSON for '{name}' to: {path}")


if __name__ == "__main__":
    main()


