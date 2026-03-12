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
    decorators: List[str] = Field(default_factory=list)

class ClassNode(BaseModel):
    """Represents a class parsed from the AST."""
    name: str
    parent_module: str
    docstring_summary: Optional[str] = None
    bases: List[str] = Field(default_factory=list)
    methods: List[FunctionNode] = Field(default_factory=list)

class ModuleNode(BaseModel):
    """Represents a source code file (Python, SQL, YAML, JS, etc)."""
    path: str
    identity: str  # E.g., module name like 'codebase_cartographer.cli'
    language: str
    architecture_layer: str = "unknown"
    
    # Imports now track {"name": "target_name", "type": "dbt_ref|import"}
    imports: List[Dict[str, str]] = Field(default_factory=list)
    
    functions: List[FunctionNode] = Field(default_factory=list)
    classes: List[ClassNode] = Field(default_factory=list)
    
    # Intelligence Flags
    complexity_score: float = 0.0
    velocity_score: float = 0.0
    change_velocity_30d: float = 0.0
    commit_count_30d: int = 0
    unique_authors_30d: int = 0
    pagerank_score: float = 0.0
    importance_score: int = 1 # 1-100 normalized
    
    is_high_complexity: bool = False
    is_high_velocity: bool = False
    is_architectural_hub: bool = False
    is_dead_code_candidate: bool = False
    is_sink_node: bool = False
    is_informational: bool = False
    
    # Semantic Intelligence (Phase 3 Upgrade)
    purpose_statement: Optional[str] = None
    purpose_confidence: Optional[float] = None
    domain_cluster: Optional[str] = None
    documentation_drift: Optional[bool] = None  # None if docstring missing
    semantic_embedding: Optional[List[float]] = None # Only if --store-embeddings is enabled
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
