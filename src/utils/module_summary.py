import os
import tree_sitter_python as tspy
from tree_sitter import Language, Parser
from typing import Dict, Any, List
from models.nodes import ModuleNode

PY_LANGUAGE = Language(tspy.language())

def build_module_summary(module_node: ModuleNode) -> Dict[str, Any]:
    """
    Generates a structured summary of a module using existing metadata as the primary source.
    Falls back to parsing the source file if necessary (e.g., for constants or missing docstrings).
    """
    summary = {
        "module_path": module_node.identity,
        "file_path": module_node.path,
        "language": module_node.language,
        "line_range": {"start": 1, "end": 0}, # To be filled if parsing
        "docstring": None,
        "imports": [imp.get("name") for imp in module_node.imports if imp.get("name")],
        "functions": [f.qualified_name for f in module_node.functions],
        "classes": [c.name for c in module_node.classes],
        "constants": []
    }

    # Attempt to load docstring and constants if it's a python file
    if module_node.language == "py" and os.path.exists(module_node.path):
        try:
            with open(module_node.path, 'rb') as f:
                content = f.read()
                parser = Parser(PY_LANGUAGE)
                tree = parser.parse(content)
                root = tree.root_node
                
                # Update line count
                summary["line_range"]["end"] = root.end_point[0] + 1
                
                # Check for module-level docstring
                # Usually the first expression statement if it contains a string
                first_child = root.children[0] if root.children else None
                if first_child and first_child.type == "expression_statement":
                    string_node = first_child.children[0]
                    if string_node.type == "string":
                        summary["docstring"] = string_node.text.decode('utf-8').strip('"\' \n\t')

                # Extract top-level constants/variables
                for child in root.children:
                    if child.type == "expression_statement":
                        assignment = next((c for c in child.children if c.type == "assignment"), None)
                        if assignment:
                            left = next((c for c in assignment.children if c.type == "identifier"), None)
                            if left:
                                summary["constants"].append(left.text.decode('utf-8'))
        except Exception:
            pass
    
    return summary
