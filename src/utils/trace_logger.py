import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

class TraceLogger:
    """
    Thread-safe JSONL logger with rotation and strict schema enforcement.
    Mirroring Agent 4 excellence requirements for auditability.
    """
    
    # Allowed event types for consistency across units
    ALLOWED_EVENTS = {
        "GRAPH_NODE_CREATED",
        "GRAPH_EDGE_CREATED",
        "FILE_PARSED",
        "SEMANTIC_ENRICHMENT",
        "LINEAGE_EXTRACTED",
        "LINEAGE_CONFLICT",
        "DEAD_CODE_DETECTED",
        "ARTIFACT_GENERATED",
        "ERROR"
    }

    def __init__(self, output_dir: str, max_size_mb: int = 50):
        self.output_dir = os.path.abspath(output_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.log_file = os.path.join(self.output_dir, "cartography_trace.jsonl")
        self.schema_version = "1.0"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def log_event(self, 
                  agent: str, 
                  event_type: str, 
                  target_file: str, 
                  method: str = "static_analysis", 
                  confidence: float = 1.0, 
                  duration_ms: int = 0, 
                  metadata: Optional[Dict[str, Any]] = None):
        """
        Logs a schema-compliant event to the JSONL trace file.
        Handles rotation if file size exceeds threshold.
        """
        if event_type not in self.ALLOWED_EVENTS:
            print(f"[Warning] TraceLogger: Unknown event type '{event_type}'. Should be one of: {self.ALLOWED_EVENTS}")

        self._check_rotation()

        event = {
            "schema_version": self.schema_version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent": agent,
            "event_type": event_type,
            "target_file": target_file,
            "method": method,
            "confidence": confidence,
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }

        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"[Error] TraceLogger: Failed to write to {self.log_file}: {e}")

    def _check_rotation(self):
        """Rotates log file if it exceeds the max size."""
        if not os.path.exists(self.log_file):
            return

        try:
            if os.path.getsize(self.log_file) > self.max_size_bytes:
                # Find the next available rotation index
                index = 1
                while True:
                    rotated_path = os.path.join(self.output_dir, f"cartography_trace_{index:03}.jsonl")
                    if not os.path.exists(rotated_path):
                        break
                    index += 1
                
                os.rename(self.log_file, rotated_path)
                print(f"[Info] TraceLogger: Rotated log to {rotated_path}")
        except Exception as e:
            print(f"[Warning] TraceLogger: Rotation check failed: {e}")

class TraceEvents:
    """Namespace for event types to prevent string typos."""
    GRAPH_NODE_CREATED = "GRAPH_NODE_CREATED"
    GRAPH_EDGE_CREATED = "GRAPH_EDGE_CREATED"
    FILE_PARSED = "FILE_PARSED"
    SEMANTIC_ENRICHMENT = "SEMANTIC_ENRICHMENT"
    LINEAGE_EXTRACTED = "LINEAGE_EXTRACTED"
    LINEAGE_CONFLICT = "LINEAGE_CONFLICT"
    DEAD_CODE_DETECTED = "DEAD_CODE_DETECTED"
    ARTIFACT_GENERATED = "ARTIFACT_GENERATED"
    ERROR = "ERROR"

class Agents:
    """Namespace for agent names."""
    SURVEYOR = "Surveyor"
    HYDROLOGIST = "Hydrologist"
    SEMANTICIST = "Semanticist"
    ARCHIVIST = "Archivist"
    ORCHESTRATOR = "Orchestrator"
