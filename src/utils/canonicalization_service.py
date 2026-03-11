import re
from typing import Optional, List, Dict, Set, Any

class CanonicalizationService:
    """Normalizes and resolves dataset identities into a unified canonical form with Phase 2.5 refinements."""
    
    def __init__(self, alias_mapping: Optional[Dict[str, str]] = None):
        # Maps canonical_name -> Set of (namespace, raw_name) for collision detection
        self.registry: Dict[str, Set[tuple]] = {}
        
        # Default alias mapping for namespaces
        self.aliases = {
            "postgresql": "postgres",
            "pg": "postgres",
            "snowflake": "sf",
            "s3a": "s3",
            "s3n": "s3",
            "google_cloud_storage": "gcs",
            "local_fs": "local",
            "filesystem": "local"
        }
        if alias_mapping:
            self.aliases.update(alias_mapping)

    def normalize(self, name: str) -> str:
        """
        Applies basic normalization rules:
        - lowercase
        - strip quotes
        - strip file extensions
        - strip trailing slashes
        """
        if not name:
            return "unknown"
            
        # Strip protocol if present (but protocol usually defines namespace)
        if "://" in name:
            name = name.split("://")[-1]
            
        name = name.lower().strip('"').strip("'").strip("`")
        
        # Strip extensions (more comprehensive)
        name = re.sub(r"\.(csv|parquet|json|avro|delta|txt|orc|iceberg|hudi|sql)$", "", name)
        
        # Strip trailing slashes
        name = name.rstrip("/")
        
        return name

    def canonicalize(self, raw_name: str, namespace: str) -> str:
        """
        Main entry point for resolving a raw string into a canonical identity.
        Returns 'namespace:normalized_name'.
        """
        # Normalize namespace using aliases
        namespace = self.aliases.get(namespace.lower(), namespace.lower())
        
        # Normalize dataset name
        canon_name = self.normalize(raw_name)
        
        # Unified identity preserves namespace to prevent collisions
        identity = f"{namespace}:{canon_name}"
        
        # Track for collision detection / sanity checks
        # We track if the SAME canonical name is used in DIFFERENT namespaces
        if canon_name not in self.registry:
            self.registry[canon_name] = set()
        self.registry[canon_name].add((namespace, raw_name))
        
        return identity

    def detect_collisions(self) -> List[Dict[str, Any]]:
        """
        Checks for canonical names that are used across multiple namespaces.
        Returns warning metadata with full provenance.
        """
        collisions = []
        for canon, occurrences in self.registry.items():
            if len(occurrences) > 1:
                namespaces = list(set([o[0] for o in occurrences]))
                if len(namespaces) > 1:
                    collisions.append({
                        "canonical_name": canon,
                        "occurrences": [{"namespace": o[0], "raw_name": o[1]} for o in occurrences],
                        "severity": "medium",
                        "message": f"Canonical name '{canon}' used across multiple namespaces: {namespaces}"
                    })
        return collisions

    @staticmethod
    def simplify_path(path: str) -> str:
        """
        Collapses partitioned object storage paths into globs.
        """
        # Match patterns like /year=2024/ /month=01/ /date=2024-01-01/
        path = re.sub(r"([a-zA-Z0-9_-]+=)[a-zA-Z0-9_-]+", r"\1*", path)
        
        # Match numeric path segments (e.g. /2024/01/01/)
        path = re.sub(r"/\d{4}/\d{2}/\d{2}/", r"/*/*/*/", path)
        
        return path
