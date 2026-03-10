import re
import os
from typing import Dict, List, Optional, Tuple, Any
from tree_sitter import Language, Parser

from codebase_cartographer.models.nodes import FunctionNode

class LanguageRouter:
    """Maps file extensions to the appropriate tree-sitter grammar."""
    
    _LANGUAGES: Dict[str, str] = {
        ".py": "python",
        ".sql": "sql",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".js": "javascript",
        ".ts": "javascript",  # Approximation for now
    }
    
    _grammars: Dict[str, Language] = {}
    
    @classmethod
    def get_language(cls, extension: str) -> Optional[Language]:
        lang_name = cls._LANGUAGES.get(extension.lower())
        if not lang_name:
            return None
            
        if lang_name not in cls._grammars:
            try:
                # Tree-sitter >= 0.22 uses direct imports
                if lang_name == "python":
                    import tree_sitter_python
                    cls._grammars[lang_name] = Language(tree_sitter_python.language())
                elif lang_name == "javascript":
                    import tree_sitter_javascript
                    cls._grammars[lang_name] = Language(tree_sitter_javascript.language())
                elif lang_name == "yaml":
                    import tree_sitter_yaml
                    cls._grammars[lang_name] = Language(tree_sitter_yaml.language())
                elif lang_name == "sql":
                    import tree_sitter_sql
                    cls._grammars[lang_name] = Language(tree_sitter_sql.language())
            except ImportError:
                return None
        return cls._grammars.get(lang_name)


class TreeSitterAnalyzer:
    """Analyzes source code files using tree-sitter to extract structures."""
    
    def __init__(self):
        self.parsers: Dict[str, Parser] = {}

    def get_parser(self, extension: str) -> Optional[Parser]:
        if extension not in self.parsers:
            language = LanguageRouter.get_language(extension)
            if not language:
                return None
            
            # tree-sitter >= 0.22 accepts Language in constructor, no set_language method
            try:
                parser = Parser(language)
            except Exception:
                # Fallback for older tree-sitter versions if needed
                parser = Parser()
                parser.set_language(language)
                
            self.parsers[extension] = parser
        return self.parsers[extension]

    def _extract_docstring(self, node, source: bytes) -> Optional[str]:
        # Simple extraction for python docstrings
        if node.type in ("function_definition", "class_definition"):
            if len(node.children) > 0 and node.children[-1].type == "block":
                block = node.children[-1]
                if len(block.children) > 0 and block.children[0].type == "expression_statement":
                    expr = block.children[0]
                    if len(expr.children) > 0 and expr.children[0].type == "string":
                        doc = expr.children[0].text.decode('utf-8')
                        # Clean quotes
                        if doc.startswith('"""') or doc.startswith("'''"):
                            doc = doc[3:-3]
                        elif doc.startswith('"') or doc.startswith("'"):
                            doc = doc[1:-1]
                        return doc.strip().split('\n\n')[0] # Return first para
        return None
        
    def _count_branches(self, node) -> int:
        """Approximates cyclomatic complexity by counting conditionals/loops."""
        count = 0
        if node.type in ("if_statement", "for_statement", "while_statement", "case_statement", "elif_clause"):
            count += 1
        for child in node.children:
            count += self._count_branches(child)
        return count

    def analyze_python_functions(self, root_node, source: bytes, module_path: str) -> List[FunctionNode]:
        functions_found = []
        
        def traverse(node, is_nested=False):
            if node.type == "function_definition":
                name_node = next((c for c in node.children if c.type == "identifier"), None)
                if not name_node:
                    return

                name = name_node.text.decode('utf-8')
                
                # Exclude purely internal helpers from public API, but keep for complexity isolation
                docstring = self._extract_docstring(node, source)
                complexity = 1 + self._count_branches(node)
                
                param_list = next((c for c in node.children if c.type == "parameters"), None)
                signature = f"def {name}{param_list.text.decode('utf-8')}" if param_list else f"def {name}()"
                
                func_node = FunctionNode(
                    qualified_name=name,
                    signature=signature,
                    parent_module=module_path,
                    docstring_summary=docstring,
                    complexity_score=complexity,
                    is_nested=is_nested
                )
                functions_found.append(func_node)
                
                # Traverse block to find nested functions
                block = next((c for c in node.children if c.type == "block"), None)
                if block:
                    for child in block.children:
                        traverse(child, is_nested=True)
            else:
                for child in node.children:
                    traverse(child, is_nested=is_nested)

        traverse(root_node)
        return functions_found

    def analyze_python_imports(self, root_node, source: bytes) -> List[Dict[str, str]]:
        imports = []
        
        def traverse(node):
            if node.type == "import_statement":
                # import X
                for child in node.children:
                    if child.type == "dotted_name":
                        imports.append({"name": child.text.decode('utf-8'), "type": "python_import"})
            elif node.type == "import_from_statement":
                # from X import Y
                module_name = next((c.text.decode('utf-8') for c in node.children if c.type == "dotted_name"), None)
                if module_name:
                    imports.append({"name": module_name, "type": "python_import"})
                    
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return imports

    def analyze_dbt_jinja(self, content: str) -> Tuple[List[Dict[str, str]], List[str]]:
        """
        Parses Jinja constructs for dbt graphs using regex.
        Returns (dependencies, metadata_variables).
        """
        imports = []
        variables = []
        
        # ref('model_name')
        for match in re.finditer(r"ref\(\s*['\"]([^'\"]+)['\"]\s*\)", content):
            imports.append({"name": match.group(1), "type": "dbt_ref"})
            
        # source('schema', 'table')
        for match in re.finditer(r"source\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)", content):
            imports.append({"name": f"{match.group(1)}.{match.group(2)}", "type": "dbt_source"})
            
        # var('variable_name')
        for match in re.finditer(r"var\(\s*['\"]([^'\"]+)['\"]\s*\)", content):
            variables.append(match.group(1))
            
        # macro calls: {{ macro_name(...) }}
        # Exclude known built-ins like ref, source, var, config
        for match in re.finditer(r"\{\{\s*([a-zA-Z0-9_]+)\(", content):
            macro_name = match.group(1)
            if macro_name not in ("ref", "source", "var", "config", "log"):
                imports.append({"name": macro_name, "type": "dbt_macro"})
            
        return imports, variables

    def _count_sql_complexity(self, content: str) -> float:
        """
        Approximates SQL complexity without a heavy AST parser by counting structural keywords.
        """
        content_lower = content.lower()
        complexity = 0.0
        
        # Count JOINs (each adds 1.0)
        complexity += len(re.findall(r'\bjoin\b', content_lower)) * 1.0
        
        # Count CTEs mapping (WITH ... AS) (each adds 0.5)
        complexity += len(re.findall(r'\bwith\b|\bas\b(?=\s*\()', content_lower)) * 0.5
        
        # Count CASE WHEN branches (each adds 0.5)
        complexity += len(re.findall(r'\bwhen\b', content_lower)) * 0.5
        
        # Count grouped aggregations
        complexity += len(re.findall(r'\bgroup by\b', content_lower)) * 1.0
        
        # Count Window functions (OVER)
        complexity += len(re.findall(r'\bover\b', content_lower)) * 1.5
        
        return max(1.0, complexity)  # Base complexity of 1.0

    def _extract_classes(self, root_node, source: bytes) -> List[str]:
        classes = []
        def traverse(node):
            if node.type == "class_definition":
                name_node = next((c for c in node.children if c.type == "identifier"), None)
                if name_node:
                    classes.append(name_node.text.decode('utf-8'))
            for child in node.children:
                traverse(child)
        traverse(root_node)
        return classes

    def analyze_file(self, filepath: str, identity: Optional[str] = None) -> Dict[str, Any]:
        """
        Parses a file and returns extracted AST metadata.
        """
        _, ext = os.path.splitext(filepath)
        parser = self.get_parser(ext)
        module_path = identity if identity else filepath
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            source_bytes = content.encode('utf-8')
        except Exception:
            # Fallback or gracefully ignore unreadable files
            return {}

        result = {
            "functions": [],
            "imports": [],
            "classes": [],
            "metadata": {}
        }

        # Analyze Jinja syntax regardless of tree-sitter since it can occur in SQL/YAML easily
        if ext in (".sql", ".yml", ".yaml"):
            jinja_imports, jinja_vars = self.analyze_dbt_jinja(content)
            
            # YAML descriptors should be typed 'describes', not execution 'dbt_ref'
            if ext in (".yml", ".yaml"):
                for imp in jinja_imports:
                    imp["type"] = "describes"
            
            result["imports"].extend(jinja_imports)
            if jinja_vars:
                result["metadata"]["variables_used"] = jinja_vars

        if not parser:
            return result

        try:
            tree = parser.parse(source_bytes)
            root = tree.root_node
            
            if ext == ".py":
                result["imports"].extend(self.analyze_python_imports(root, source_bytes))
                result["functions"] = self.analyze_python_functions(root, source_bytes, module_path)
                result["classes"] = self._extract_classes(root, source_bytes)
            elif ext == ".sql":
                # Add SQL fallback complexity and symbol mapping (module itself is the symbol in dbt)
                base = os.path.basename(filepath)
                # Ensure the sql model name itself is available as a discoverable symbol in the graph
                result["functions"].append(FunctionNode(
                    qualified_name=os.path.splitext(base)[0],
                    signature="SQL Model",
                    parent_module=module_path,
                    complexity_score=int(self._count_sql_complexity(content))
                ))
                
            # For SQL and YAML, semantic tree-sitter analysis can be added later as needed
            # For now, dbt jinja parses handle the core linkage.
        except Exception:
            # Graceful failure on parse errors
            pass
            
        return result
