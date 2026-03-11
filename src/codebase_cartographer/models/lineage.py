from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, computed_field

class DatasetRole(str, Enum):
    """Semantic role of a dataset in the lineage graph."""
    SOURCE = "SOURCE"
    INTERMEDIATE = "INTERMEDIATE"
    TERMINAL = "TERMINAL"

class ColumnRef(BaseModel):
    """Richer representation of a column for future-proofing lineage."""
    name: str
    source_columns: List[str] = Field(default_factory=list)
    inferred_type: Optional[str] = None
    confidence: float = 1.0

class DataNode(BaseModel):
    """Represents a data entity (table, file, bucket) in the lineage graph."""
    identity: str  # Unique key, typically 'namespace:canonical_name'
    name: str  # Observed raw string from source code/config
    canonical_name: str  # Resolved normalized identity
    namespace: str  # System context: e.g., 'postgres', 'snowflake', 's3', 'local_fs'
    
    type: str = "unknown"  # 'file', 'object_storage', 'database_table'
    format: Optional[str] = None  # 'csv', 'parquet', 'delta', 'iceberg'
    location: Optional[str] = None  # Full URI or path
    
    # Phase 2.6: Versioning & Metadata
    version: Optional[str] = None
    partition: Optional[str] = None
    timestamp: Optional[datetime] = None
    owner_team: Optional[str] = None
    system: Optional[str] = None  # Normalized system name (Snowflake, S3, etc.)
    environment: Optional[str] = None  # prod, staging, dev
    dataset_type_confidence: float = 1.0

    # Phase 2.7: Fully Qualified Identity
    database: Optional[str] = None
    schema_: Optional[str] = Field(default=None, alias="schema")
    table: Optional[str] = None

    # Richer schema awareness
    columns: List[ColumnRef] = Field(default_factory=list)
    role: Optional[DatasetRole] = None
    
    is_dynamic_reference: bool = False
    
    # Merged structural (from Phase 1) and lineage (from Phase 2) importance
    importance_score: int = 1
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TransformationNode(BaseModel):
    """Represents a processing step (Python script, SQL model, Airflow task)."""
    identity: str  # Module path or task ID
    name: str
    type: str  # 'PYTHON_SCRIPT', 'DBT_MODEL', 'AIRFLOW_TASK'
    logic_hash: str
    
    # Traceability
    owner_team: Optional[str] = None
    environment: Optional[str] = None
    
    # Phase 2.7/2.8: Lineage Enrichment & Semantics
    operations: List[Dict[str, Any]] = Field(default_factory=list)
    column_lineage: List[Dict[str, Any]] = Field(default_factory=list)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LineageEdge(BaseModel):
    """Represents a directed data flow between data entities or code and data."""
    source: str  # Identity of the source node
    target: str  # Identity of the target node
    
    # Semantic taxonomy: DBT_REF, DBT_SOURCE, PYTHON_READ, PYTHON_WRITE, CONFIG_DEPENDENCY, SQL_PRODUCT
    type: str
    
    origin_analyzer: str  # 'python_dataflow', 'sql_lineage', 'dag_config'
    confidence_score: float = 1.0  # 1.0: Deterministic, 0.7: Propagation, 0.3: Heuristic
    
    # Stable hash of the logic (SQL/Python) producing this edge
    logic_hash: Optional[str] = None

    @computed_field
    @property
    def is_heuristic(self) -> bool:
        """Derived boolean for convenience based on confidence."""
        return self.confidence_score < 0.5
    
    # Traceability to source code
    source_module: Optional[str] = None
    line_number: Optional[int] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
