from typing import List, Protocol
from codebase_cartographer.models.lineage import LineageEdge

class DAGParserPlugin(Protocol):
    def can_handle(self, filepath: str) -> bool: ...
    def parse(self, filepath: str, identity: str) -> List[LineageEdge]: ...

class DAGConfigAnalyzer:
    """
    Orchestrates configuration-based lineage extraction using a plugin architecture.
    Handles virtual dependencies from Airflow DAGs, dbt configs, etc.
    """
    
    def __init__(self):
        self.parsers: List[DAGParserPlugin] = []

    def register_parser(self, parser: DAGParserPlugin):
        self.parsers.append(parser)

    def analyze(self, filepath: str, identity: str) -> List[LineageEdge]:
        """Analyzes a configuration file using all registered parsers."""
        edges = []
        for parser in self.parsers:
            if parser.can_handle(filepath):
                try:
                    edges.extend(parser.parse(filepath, identity))
                except Exception:
                    # Log failure and continue to next parser
                    pass
        return edges
