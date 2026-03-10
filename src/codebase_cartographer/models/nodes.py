from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FunctionNode(BaseModel):
    """Represents a function or method parsed from the AST."""
    qualified_name: str
    signature: str
    parent_module: str
    docstring_summary: Optional[str] = None
    complexity_score: int = 1
    
    # Track nested functions to avoid inflating parent complexity
    is_nested: bool = False

class ModuleNode(BaseModel):
    """Represents a source code file (Python, SQL, YAML, JS, etc)."""
    path: str
    identity: str  # E.g., module name like 'codebase_cartographer.cli'
    language: str
    architecture_layer: str = "unknown"
    
    # Imports now track {"name": "target_name", "type": "dbt_ref|import"}
    imports: List[Dict[str, str]] = Field(default_factory=list)
    
    functions: List[FunctionNode] = Field(default_factory=list)
    classes: List[str] = Field(default_factory=list)
    
    # Intelligence Flags
    complexity_score: float = 0.0
    velocity_score: float = 0.0
    pagerank_score: float = 0.0
    importance_score: int = 1 # 1-100 normalized
    
    is_high_complexity: bool = False
    is_high_velocity: bool = False
    is_architectural_hub: bool = False
    is_dead_code_candidate: bool = False
    is_sink_node: bool = False
    is_informational: bool = False
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
