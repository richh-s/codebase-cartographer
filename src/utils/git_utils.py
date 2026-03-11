import subprocess
import os
from typing import Dict, Any, List, Set

class GitUtils:
    """Extracts git metadata for architectural intelligence."""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
    
    def _run_git_cmd(self, cmd: List[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + cmd,
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def get_file_metadata(self, days: int = 30, logic_threshold: int = 3) -> Dict[str, Dict[str, Any]]:
        """
        Uses git log --numstat to calculate logical change velocity and author breadth.
        Returns a dict mapping filepath to metadata.
        """
        metadata_map: Dict[str, Dict[str, Any]] = {}
        
        # Format: commit_hash|author_name|author_date
        # Followed by numstat lines
        cmd = [
            "log",
            f"--since={days}.days.ago",
            "--format=commit:|%H|%an|%cI",
            "--numstat",
            "--no-merges",
            # ignore whitespace changes for the diff
            "-w"
        ]
        
        output = self._run_git_cmd(cmd)
        if not output:
            return metadata_map
            
        current_author = ""
        current_date = ""
        
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("commit:|"):
                parts = line.split("|")
                if len(parts) >= 4:
                    current_author = parts[2]
                    current_date = parts[3]
            else:
                # Numstat format: added deleted filepath
                stat_parts = line.split("\t")
                if len(stat_parts) == 3:
                    added_str, deleted_str, filepath = stat_parts
                    
                    # - means binary file modification
                    if added_str == "-" or deleted_str == "-":
                        continue
                        
                    try:
                        added = int(added_str)
                        deleted = int(deleted_str)
                    except ValueError:
                        continue
                        
                    # Filter trivial commits
                    if (added + deleted) < logic_threshold:
                        continue
                        
                    if filepath not in metadata_map:
                        metadata_map[filepath] = {
                            "velocity_score": 0.0,
                            "authors": set(),
                            "last_modified": current_date, # First seen is most recent due to git log order
                            "last_author": current_author
                        }
                    
                    # Increment logic velocity. Could weight by age, but simple sum mapped to score is good for Phase 1.
                    metadata_map[filepath]["velocity_score"] += 1.0  # Or could use (added + deleted)
                    metadata_map[filepath]["authors"].add(current_author)
                    
        # Post-process sets to lists and compute author breadth
        for filepath, data in metadata_map.items():
            data["author_breadth"] = len(data["authors"])
            data.pop("authors") # Cleanup
            
        return metadata_map
