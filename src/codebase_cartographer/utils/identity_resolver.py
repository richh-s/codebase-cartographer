import re
import os
from typing import List, Dict, Optional, Set, Any
from pydantic import BaseModel, Field

class DatasetIdentity(BaseModel):
    """Represents a unified logical dataset identity across systems."""
    canonical_name: str
    namespaces: Set[str] = Field(default_factory=set)
    aliases: Set[str] = Field(default_factory=set)
    confidence: float = 1.0
    
    database: Optional[str] = None
    schema_: Optional[str] = Field(default=None, alias="schema")
    table: Optional[str] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

class IdentityResolver:
    """Resolves raw strings and namespace context into unified logical identities."""
    
    def __init__(self, custom_mappings: Optional[Dict[str, str]] = None):
        # Maps alias/raw_name -> canonical_name
        self.mappings: Dict[str, str] = {}
        if custom_mappings:
            self.mappings.update(custom_mappings)
            
        self.identities: Dict[str, DatasetIdentity] = {}

    def resolve(self, raw_name: str, namespace: str, allow_fuzzy: bool = True) -> str:
        """
        Resolves a raw name and namespace to a canonical identity.
        If a mapping exists, returns the mapped canonical name.
        Otherwise, returns a normalized string.
        """
        # 1. Direct mapping lookup
        if raw_name in self.mappings:
            canon = self.mappings[raw_name]
        else:
            # 2. Heuristic normalization
            canon = self._normalize(raw_name)
            
        # 3. Fuzzy matching for dbt sources (orders -> raw_orders)
        if allow_fuzzy and canon not in self.identities and namespace in ["unknown", "dbt"]:
            potential_raw = f"raw_{canon}"
            if potential_raw in self.identities:
                return potential_raw

        # 4. Registry tracking
        if canon not in self.identities:
            components = self._parse_components(raw_name)
            self.identities[canon] = DatasetIdentity(
                canonical_name=canon,
                database=components["database"],
                schema_=components["schema_"],
                table=components["table"]
            )
        
        self.identities[canon].namespaces.add(namespace)
        self.identities[canon].aliases.add(raw_name)
        
        return canon

    def _normalize(self, name: str) -> str:
        """Basic normalization for fallback resolution."""
        name = name.lower().strip('"').strip("'").strip("`")
        if "://" in name:
            name = name.split("://")[-1]
        
        # Strip common extensions and paths
        name = re.sub(r"\.(csv|parquet|sql|json|delta|avro|txt)$", "", name)
        name = name.split("/")[-1]
        
        return name

    def _parse_components(self, raw_name: str) -> Dict[str, Optional[str]]:
        """Extracts database, schema, and table from common string formats."""
        clean = raw_name.lower().strip('"').strip("'").strip("`")
        if "://" in clean:
            clean = clean.split("://")[-1]
        
        # If it's a file path, take the basename without extension
        if "/" in clean or "\\" in clean:
            clean = os.path.splitext(os.path.basename(clean))[0]
        
        parts = clean.split(".")
        if len(parts) >= 3:
            return {"database": parts[-3], "schema_": parts[-2], "table": parts[-1]}
        elif len(parts) == 2:
            return {"database": None, "schema_": parts[0], "table": parts[1]}
        else:
            # For dbt models like stg_orders, the table is the whole name
            return {"database": None, "schema_": None, "table": clean}

    def get_identities(self) -> List[DatasetIdentity]:
        """Returns all discovered logical identities."""
        return list(self.identities.values())
