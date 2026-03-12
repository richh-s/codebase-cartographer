import subprocess
import os
from typing import Dict, Any, Set

class GitProvider:
    """
    Handles optimized extraction of git metadata using batched subprocess calls.
    Fulfills Phase 4 requirements for churn analysis and rename detection.
    """
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self._churn_cache: Dict[str, Dict[str, Any]] = {}
        self._is_git_repo = os.path.exists(os.path.join(self.repo_path, ".git"))

    def prefetch_metadata(self, days: int = 30):
        """
        Batches git log queries into an in-memory map to avoid O(N) subprocess overhead.
        Uses -M for rename detection and --name-status for churn counts.
        """
        if not self._is_git_repo:
            return

        # -M ensures rename detection
        # --name-status gives us A/M/D/R status
        # --pretty=format:%an gives us the author name for each commit block
        cmd = [
            "git", "log", 
            f"--since={days}.days", 
            "--name-status", 
            "-M", 
            "--pretty=format:%an"
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.repo_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            self._parse_git_log(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[Warning] GitProvider: Batch query failed: {e}")

    def _parse_git_log(self, stdout: str):
        """
        Parses `git log --name-status` output into churn metrics.
        The format has author names on their own lines, followed by file status lines.
        """
        file_metrics: Dict[str, Dict[str, Any]] = {}
        current_author = None
        
        # We need to compute velocity over the window. 
        # For simplicity, we assume the window is the one used in prefetch_metadata.
        
        lines = stdout.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # If the line doesn't start with a status code (A, M, D, R, etc), it's an author
            if not any(line.startswith(c) for c in ["A\t", "M\t", "D\t", "R", "T\t", "U\t"]):
                current_author = line
                continue
                
            parts = line.split("\t")
            status = parts[0]
            
            # Handle Renames (R100 old new)
            if status.startswith("R"):
                target_file = parts[2]
            else:
                target_file = parts[1]
                
            if target_file not in file_metrics:
                file_metrics[target_file] = {
                    "commit_count": 0,
                    "unique_authors": set(),
                }
            
            file_metrics[target_file]["commit_count"] += 1
            if current_author:
                file_metrics[target_file]["unique_authors"].add(current_author)

        # Convert to final metrics
        for path, metrics in file_metrics.items():
            self._churn_cache[path] = {
                "commit_count_30d": metrics["commit_count"],
                "unique_authors_30d": len(metrics["unique_authors"]),
                "velocity_score": metrics["commit_count"] / 30.0 # Normalized per day
            }

    def get_file_metrics(self, file_path: str) -> Dict[str, Any]:
        """Returns cached metrics for a specific file relative to repo root."""
        # Ensure path is relative to repo_path
        if os.path.isabs(file_path):
            rel_path = os.path.relpath(file_path, self.repo_path)
        else:
            rel_path = file_path
            
        return self._churn_cache.get(rel_path, {
            "commit_count_30d": 0,
            "unique_authors_30d": 0,
            "velocity_score": 0.0
        })

    def get_current_sha(self) -> str:
        """Returns the current git commit SHA."""
        if not self._is_git_repo:
            return "no_git_detected"
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "HEAD"], 
                cwd=self.repo_path, 
                text=True
            ).strip()
        except:
            return "unknown_sha"
