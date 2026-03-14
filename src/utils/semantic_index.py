"""
Semantic Index — Persistent vector store for module purpose statements.

Stores embeddings as a flat JSON file in semantic_index/ directory.
Provides fast cosine-similarity search without requiring an external vector DB.

Used by:
  - NavigatorTools.find_implementation() (runtime lookup)
  - Orchestrator (build/update on each analysis run)
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Tuple

from utils.similarity import cosine_similarity


SEMANTIC_INDEX_DIR = "semantic_index"
INDEX_FILE = "index.json"


class SemanticIndex:
    """
    Lightweight persistent vector store backed by a JSON file.
    Stores embeddings per module identity with associated metadata.
    """

    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.index_dir = os.path.join(repo_path, SEMANTIC_INDEX_DIR)
        self.index_path = os.path.join(self.index_dir, INDEX_FILE)
        os.makedirs(self.index_dir, exist_ok=True)
        self._store: Dict[str, Dict] = {}
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r") as f:
                    data = json.load(f)
                    self._store = data.get("entries", {})
            except Exception:
                self._store = {}

    def save(self):
        payload = {
            "schema_version": "1.0",
            "entry_count": len(self._store),
            "entries": self._store,
        }
        with open(self.index_path, "w") as f:
            json.dump(payload, f, indent=2)

    # ------------------------------------------------------------------
    # Index operations
    # ------------------------------------------------------------------

    def upsert(self, identity: str, purpose: str, embedding: List[float], metadata: Optional[Dict] = None):
        """
        Adds or updates an entry in the semantic index.
        Uses a content hash to avoid re-indexing unchanged modules.
        """
        content_hash = hashlib.sha256(purpose.encode()).hexdigest()[:12]
        existing = self._store.get(identity, {})
        if existing.get("content_hash") == content_hash:
            return  # No change, skip

        self._store[identity] = {
            "identity": identity,
            "purpose": purpose,
            "embedding": embedding,
            "content_hash": content_hash,
            "metadata": metadata or {},
        }

    def build_from_graph(self, module_graph: Dict, llm_client=None):
        """
        Populates the index from a module_graph dict (as produced by GraphBuilder.export_dict()).
        Requires nodes to have purpose_statement and semantic_embedding fields.
        """
        nodes = module_graph.get("nodes", [])
        indexed = 0
        needs_embed = []

        for node in nodes:
            purpose = node.get("purpose_statement")
            if not purpose:
                continue
            embedding = node.get("semantic_embedding")
            if embedding:
                self.upsert(
                    identity=node.get("identity", ""),
                    purpose=purpose,
                    embedding=embedding,
                    metadata={
                        "path": node.get("path"),
                        "domain": node.get("domain_cluster"),
                        "layer": node.get("architecture_layer"),
                    },
                )
                indexed += 1
            elif llm_client:
                needs_embed.append(node)

        # Generate missing embeddings
        if needs_embed and llm_client:
            texts = [n["purpose_statement"] for n in needs_embed]
            embeddings = llm_client.embed_texts(texts)
            for node, emb in zip(needs_embed, embeddings):
                if emb:
                    self.upsert(
                        identity=node.get("identity", ""),
                        purpose=node["purpose_statement"],
                        embedding=emb,
                        metadata={
                            "path": node.get("path"),
                            "domain": node.get("domain_cluster"),
                            "layer": node.get("architecture_layer"),
                        },
                    )
                    indexed += 1

        self.save()
        return indexed

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[float, Dict]]:
        """
        Returns the top-k most similar entries by cosine similarity.
        """
        scores = []
        for entry in self._store.values():
            emb = entry.get("embedding")
            if not emb:
                continue
            sim = cosine_similarity(query_embedding, emb)
            scores.append((sim, entry))
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:top_k]

    def keyword_search(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict]]:
        """
        Keyword-based fallback search when no query embedding is available.
        """
        query_lower = query.lower()
        terms = query_lower.split()
        scored = []
        for entry in self._store.values():
            purpose = entry.get("purpose", "").lower()
            identity = entry.get("identity", "").lower()
            score = sum(purpose.count(t) * 3 + identity.count(t) for t in terms)
            if score > 0:
                scored.append((score, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    @property
    def size(self) -> int:
        return len(self._store)
