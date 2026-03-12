"""
Codebase Cartographer — Web UI Server
FastAPI backend that serves the UI and exposes REST APIs for the frontend.

Usage:
    python src/server.py <repo_path>
    # Or via CLI:
    python src/cli.py serve <repo_path>
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Path setup ────────────────────────────────────────────────────────────────
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(os.path.dirname(SRC_DIR), "ui")
sys.path.insert(0, SRC_DIR)

app = FastAPI(title="Codebase Cartographer API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Global repo path (set at startup)
REPO_PATH: str = "."


# ── Request / Response models ─────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    repo_path: str
    llm_enabled: bool = False
    semantic_depth: str = "light"

class CloneRequest(BaseModel):
    url: str  # GitHub / HTTPS / SSH git URL

class QueryRequest(BaseModel):
    question: str
    repo_path: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_remote_url(s: str) -> bool:
    """Returns True if s looks like a remote git URL."""
    s = s.strip()
    return (
        s.startswith("http://")
        or s.startswith("https://")
        or s.startswith("git@")
        or s.startswith("git://")
    )

def _get_repo(repo_path: Optional[str] = None) -> str:
    return os.path.abspath(repo_path or REPO_PATH)

def _load_json(path: str) -> Dict:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def _catalog(repo: str) -> Dict:
    return _load_json(os.path.join(repo, ".cartography", "catalog.json")).get("latest_analysis", {})

def _resolve_artifact(repo: str, key: str, fallback_name: str) -> str:
    """Resolve artifact path from catalog, fall back to .cartography/"""
    cat = _catalog(repo)
    rel = cat.get(key)
    if rel:
        path = os.path.join(repo, rel)
        if os.path.exists(path):
            return path
    # Fallback to versioned artifacts dir
    artifacts = os.path.join(repo, "artifacts")
    if os.path.exists(artifacts):
        candidates = [f for f in os.listdir(artifacts) if f.startswith(fallback_name.split(".")[0])]
        if candidates:
            return os.path.join(artifacts, sorted(candidates)[-1])
    return os.path.join(repo, ".cartography", fallback_name)


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/status")
def status(repo_path: Optional[str] = None):
    repo = _get_repo(repo_path)
    catalog = _catalog(repo)
    module_graph_path = _resolve_artifact(repo, "module_graph", "module_graph.json")
    return {
        "repo_path": repo,
        "has_analysis": bool(catalog),
        "git_commit": catalog.get("git_commit", "N/A"),
        "timestamp": catalog.get("timestamp", "N/A"),
        "module_graph_exists": os.path.exists(module_graph_path),
        "lineage_graph_exists": os.path.exists(
            _resolve_artifact(repo, "lineage_graph", "lineage_graph.json")
        ),
    }


@app.post("/api/clone")
def clone_repo(req: CloneRequest):
    """
    Clones a remote git repository into a temp directory and returns the local path.
    Supports HTTPS (github.com, gitlab.com, etc.) and git@ SSH URLs.
    """
    import tempfile, subprocess, re
    url = req.url.strip()
    if not _is_remote_url(url):
        raise HTTPException(400, f"'{url}' does not look like a remote git URL.")

    # Derive a friendly folder name from the URL
    repo_name = re.sub(r'\.git$', '', url.rstrip('/').split('/')[-1])
    clone_dir = os.path.join(tempfile.gettempdir(), f"cartographer_{repo_name}")

    # Reuse clone if already exists (avoids re-cloning on refresh)
    if os.path.exists(os.path.join(clone_dir, ".git")):
        # Pull latest
        subprocess.run(["git", "-C", clone_dir, "pull", "--ff-only"], capture_output=True)
        return {"path": clone_dir, "cached": True, "repo_name": repo_name}

    os.makedirs(clone_dir, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", "--depth", "1", url, clone_dir],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise HTTPException(500, f"git clone failed: {result.stderr.strip()[:400]}")

    return {"path": clone_dir, "cached": False, "repo_name": repo_name}


@app.get("/api/module-graph")
def module_graph(repo_path: Optional[str] = None):
    repo = _get_repo(repo_path)
    path = _resolve_artifact(repo, "module_graph", "module_graph.json")
    if not os.path.exists(path):
        raise HTTPException(404, "Module graph not found. Run analysis first.")
    return _load_json(path)


@app.get("/api/lineage-graph")
def lineage_graph(repo_path: Optional[str] = None):
    repo = _get_repo(repo_path)
    path = _resolve_artifact(repo, "lineage_graph", "lineage_graph.json")
    if not os.path.exists(path):
        raise HTTPException(404, "Lineage graph not found. Run analysis first.")
    return _load_json(path)


@app.get("/api/artifacts/codebase")
def codebase_md(repo_path: Optional[str] = None):
    repo = _get_repo(repo_path)
    for candidate in [
        os.path.join(repo, "artifacts", "CODEBASE.md"),
        os.path.join(repo, ".cartography", "CODEBASE.md"),
    ]:
        if os.path.exists(candidate):
            with open(candidate) as f:
                return {"content": f.read()}
    raise HTTPException(404, "CODEBASE.md not found.")


@app.get("/api/artifacts/onboarding")
def onboarding_brief(repo_path: Optional[str] = None):
    repo = _get_repo(repo_path)
    for candidate in [
        os.path.join(repo, "artifacts", "onboarding_brief.md"),
        os.path.join(repo, ".cartography", "onboarding_brief.md"),
    ]:
        if os.path.exists(candidate):
            with open(candidate) as f:
                return {"content": f.read()}
    raise HTTPException(404, "onboarding_brief.md not found.")


@app.get("/api/trace")
def trace_log(repo_path: Optional[str] = None, lines: int = 100):
    repo = _get_repo(repo_path)
    path = os.path.join(repo, ".cartography", "cartography_trace.jsonl")
    if not os.path.exists(path):
        return {"events": []}
    events = []
    with open(path) as f:
        all_lines = f.readlines()
    for line in all_lines[-lines:]:
        try:
            events.append(json.loads(line))
        except Exception:
            pass
    return {"events": list(reversed(events))}


@app.post("/api/query")
def navigator_query(req: QueryRequest):
    repo = _get_repo(req.repo_path)
    try:
        from agents.navigator import NavigatorAgent
        nav = NavigatorAgent(repo)
        answer = nav.query(req.question)
        return {"answer": answer, "question": req.question}
    except Exception as e:
        raise HTTPException(500, f"Navigator error: {e}")


@app.post("/api/analyze")
def run_analysis(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Triggers a full analysis run in the background."""
    def _run():
        try:
            from orchestrator import Orchestrator
            orch = Orchestrator(req.repo_path)
            orch.run_analysis(llm_enabled=req.llm_enabled, semantic_depth=req.semantic_depth)
        except Exception as e:
            print(f"[Server] Analysis error: {e}")

    background_tasks.add_task(_run)
    return {"status": "started", "repo_path": req.repo_path}


@app.get("/api/stats")
def stats(repo_path: Optional[str] = None):
    """Aggregated statistics for the dashboard."""
    repo = _get_repo(repo_path)
    mg_path = _resolve_artifact(repo, "module_graph", "module_graph.json")
    lg_path = _resolve_artifact(repo, "lineage_graph", "lineage_graph.json")

    result = {"modules": 0, "edges": 0, "hubs": 0, "dead_code": 0, "data_nodes": 0, "lineage_edges": 0, "sinks": 0}

    if os.path.exists(mg_path):
        mg = _load_json(mg_path)
        nodes = mg.get("nodes", [])
        result["modules"] = len(nodes)
        result["edges"] = len(mg.get("edges", []))
        result["hubs"] = sum(1 for n in nodes if n.get("is_architectural_hub"))
        result["dead_code"] = sum(1 for n in nodes if n.get("is_dead_code_candidate"))

    if os.path.exists(lg_path):
        lg = _load_json(lg_path)
        raw_nodes = lg.get("nodes", {})
        if isinstance(raw_nodes, dict):
            result["data_nodes"] = len(raw_nodes.get("data", [])) + len(raw_nodes.get("transformations", []))
        result["lineage_edges"] = len(lg.get("edges", []))

    return result


# ── Static files ──────────────────────────────────────────────────────────────

if os.path.exists(UI_DIR):
    app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")


# ── Dev entry ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    if len(sys.argv) > 1:
        REPO_PATH = os.path.abspath(sys.argv[1])
    print(f"🗺️  Cartographer UI: http://localhost:8370")
    print(f"   Repo: {REPO_PATH}")
    uvicorn.run(app, host="0.0.0.0", port=8370)
