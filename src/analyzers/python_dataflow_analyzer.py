import os
import re
import hashlib
from typing import List, Optional, Dict, Tuple, Any
from tree_sitter import Language, Parser
from analyzers.tree_sitter_analyzer import LanguageRouter
from models.lineage import DataNode, LineageEdge

class PythonDataFlowAnalyzer:
    """Uses tree-sitter to extract dataflow lineage from Python source code."""
    
    def __init__(self):
        lang = LanguageRouter.get_language(".py")
        if lang:
            try:
                self.parser = Parser(lang)
            except Exception:
                self.parser = Parser()
                self.parser.set_language(lang)
        else:
            self.parser = Parser()
        self.engines = {} # Track engine_name -> dialect/namespace mapping
            
    def _generate_logic_hash(self, text: str) -> str:
        """Generates a stable, whitespace-insensitive hash for a code block."""
        # Normalize whitespace: collapse all internal whitespace and strip
        normalized = " ".join(text.split()).strip()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]

    def _resolve_constant(self, node, source: bytes, constants: Dict[str, str]) -> Tuple[Optional[str], float]:
        """
        Attempts to resolve a node's value if it's a literal or a known constant.
        Returns (value, confidence).
        """
        if node.type == "string":
            # If it's an f-string, it will have children like interpolation and string_content
            if any(child.type == "interpolation" for child in node.children):
                resolved_parts = []
                confidence = 0.7 # Propagated confidence
                for child in node.children:
                    if child.type == "string_content":
                        resolved_parts.append(child.text.decode('utf-8'))
                    elif child.type == "interpolation":
                        expr = child.named_children[0] if child.named_children else None
                        if expr and expr.type == "identifier":
                            name = expr.text.decode('utf-8')
                            if name in constants:
                                resolved_parts.append(constants[name])
                            else:
                                resolved_parts.append(f"{{{name}}}")
                                confidence = 0.3 # Reduced confidence if part is unresolved
                        else:
                            confidence = 0.3
                return "".join(resolved_parts), confidence

            text = node.text.decode('utf-8')
            if text.startswith(('f"', "f'", '"', "'")):
                if text.startswith(('f"', "f'")):
                    text = text[1:]
                text = text[1:-1]
            return text, 1.0
            
        if node.type == "identifier":
            name = node.text.decode('utf-8')
            if name in constants:
                return constants[name], 0.7
                
        return None, 0.3

    def _extract_constants(self, root_node, source: bytes) -> Dict[str, str]:
        """Extracts module-level global constants."""
        constants = {}
        for child in root_node.children:
            if child.type == "expression_statement":
                assignment = child.children[0]
                if assignment.type == "assignment":
                    left = assignment.child_by_field_name("left")
                    right = assignment.child_by_field_name("right")
                    if left and right and left.type == "identifier" and right.type == "string":
                        name = left.text.decode('utf-8')
                        val = right.text.decode('utf-8')
                        if val.startswith(('"', "'")): val = val[1:-1]
                        constants[name] = val
        return constants

    def _detect_engines(self, root_node, source: bytes, constants: Dict[str, str]):
        """Detects create_engine calls and maps variables to dialects."""
        def traverse(node):
            if node.type == "assignment":
                left = node.child_by_field_name("left")
                right = node.child_by_field_name("right")
                if left and right and left.type == "identifier" and right.type == "call":
                    func = right.child_by_field_name("function")
                    if func and "create_engine" in func.text.decode('utf-8'):
                        args = right.child_by_field_name("arguments")
                        if args and len(args.children) > 1:
                            conn_node = args.children[1]
                            val, _ = self._resolve_constant(conn_node, source, constants)
                            if val:
                                dialect = val.split("://")[0] if "://" in val else "unknown"
                                self.engines[left.text.decode('utf-8')] = dialect
            for child in node.children:
                traverse(child)
        traverse(root_node)

    def analyze(self, filepath: str, identity: str, shared_constants: Optional[Dict[str, str]] = None) -> Tuple[List[LineageEdge], Dict[str, str]]:
        """Analyzes a single python file for dataflow edges. Returns (edges, local_constants)."""
        if not filepath.endswith(".py"):
            return [], {}
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            source_bytes = content.encode("utf-8")
        except Exception:
            return [], {}
            
        tree = self.parser.parse(source_bytes)
        root = tree.root_node
        
        # 1. Extract Local Constants
        local_constants = self._extract_constants(root, source_bytes)
        
        # 2. Merge with shared constants for resolution
        merged_constants = {**(shared_constants or {}), **local_constants}
        
        # 3. Detect DB engines
        self._detect_engines(root, source_bytes, merged_constants)
        
        edges = []
        
        def traverse(node):
            # Detect pd.read_csv, sqlalchemy.execute, pyspark.read, etc.
            if node.type == "call":
                func_node = node.child_by_field_name("function")
                if not func_node: return
                
                func_text = func_node.text.decode('utf-8')
                
                # 1. Pandas Read/Write
                pandas_ios = [
                    "read_csv", "read_excel", "read_parquet", "read_sql", "read_json",
                    "to_csv", "to_parquet", "to_sql", "to_excel", "to_json"
                ]
                if any(k in func_text for k in pandas_ios):
                    args = node.child_by_field_name("arguments")
                    if args and len(args.children) > 1:
                        # Usually first arg is path
                        path_node = args.children[1]
                        val, confidence = self._resolve_constant(path_node, source_bytes, merged_constants)
                        if val:
                            etype = "PYTHON_WRITE" if "to_" in func_text else "PYTHON_READ"
                            edges.append(LineageEdge(
                                source=val if etype == "PYTHON_READ" else identity,
                                target=identity if etype == "PYTHON_READ" else val,
                                type=etype,
                                origin_analyzer="python_dataflow",
                                confidence_score=confidence,
                                logic_hash=self._generate_logic_hash(node.text.decode('utf-8')),
                                source_module=identity,
                                line_number=node.start_point[0] + 1
                            ))
                            
                # 2. PySpark Read/Write
                elif any(k in func_text for k in [".read.", ".write.", "read.csv", "read.parquet", "write.parquet", "write.save"]):
                    args = node.child_by_field_name("arguments")
                    if args and len(args.children) > 1:
                        path_node = args.children[1]
                        val, confidence = self._resolve_constant(path_node, source_bytes, merged_constants)
                        if val:
                            etype = "PYTHON_READ" if ".read" in func_text else "PYTHON_WRITE"
                            edges.append(LineageEdge(
                                source=val if etype == "PYTHON_READ" else identity,
                                target=identity if etype == "PYTHON_READ" else val,
                                type=etype,
                                origin_analyzer="python_dataflow",
                                confidence_score=confidence,
                                logic_hash=self._generate_logic_hash(node.text.decode('utf-8')),
                                source_module=identity,
                                line_number=node.start_point[0] + 1
                            ))

                # 3. SQLAlchemy / DB Execute
                elif "execute" in func_text:
                    args = node.child_by_field_name("arguments")
                    if args and len(args.children) > 1:
                        sql_node = args.children[1]
                        val, confidence = self._resolve_constant(sql_node, source_bytes, merged_constants)
                        if val and any(k in val.upper() for k in ["SELECT", "FROM", "INSERT", "UPDATE", "INTO"]):
                            patterns = [
                                r"FROM\s+([a-zA-Z0-9_\.]+)",
                                r"JOIN\s+([a-zA-Z0-9_\.]+)",
                                r"INTO\s+([a-zA-Z0-9_\.]+)"
                            ]
                            for p in patterns:
                                for match in re.finditer(p, val, re.IGNORECASE):
                                    table = match.group(1)
                                    etype = "PYTHON_WRITE" if "INTO" in p.upper() else "PYTHON_READ"
                                    
                                    # Try to find engine context
                                    namespace = "unknown"
                                    if "." in func_text:
                                        engine_var = func_text.split(".")[0]
                                        if engine_var in self.engines:
                                            namespace = self.engines[engine_var]
                                            table = f"{namespace}:{table}"
                                    elif etype == "PYTHON_READ" and self.engines:
                                        namespace = list(self.engines.values())[0]
                                        table = f"{namespace}:{table}"

                                    edges.append(LineageEdge(
                                        source=table if etype == "PYTHON_READ" else identity,
                                        target=identity if etype == "PYTHON_READ" else table,
                                        type=etype,
                                        origin_analyzer="python_dataflow",
                                        confidence_score=confidence * 0.4, # Heuristic penalty
                                        logic_hash=self._generate_logic_hash(val),
                                        source_module=identity,
                                        line_number=node.start_point[0] + 1
                                    ))

            for child in node.children:
                traverse(child)
                
        traverse(root)
        return edges, local_constants
