import os
import time
from typing import List

from analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from utils.git_utils import GitUtils
from graph.graph_builder import GraphBuilder
from models.nodes import ModuleNode

class SurveyorAgent:
    """Orchestrates Phase 1: Static structure and git metadata extraction."""
    
    def __init__(self, target_dir: str):
        self.target_dir = os.path.abspath(target_dir)
        self.analyzer = TreeSitterAnalyzer()
        self.git_utils = GitUtils(self.target_dir)
        self.graph_builder = GraphBuilder()
        
    def _get_identity(self, filepath: str) -> str:
        """Converts absolute path to a relative identity for the graph."""
        rel_path = os.path.relpath(filepath, self.target_dir)
        return rel_path
        
    def run(self, output_json: str = ".cartography/module_graph.json", velocity_days: int = 30):
        """Executes the full Surveyor pipeline."""
        print(f"Starting SurveyorAgent on {self.target_dir}")
        print(f"Output will be saved to {output_json}")
        git_data = self.git_utils.get_file_metadata(days=velocity_days)
        
        # 1. Walk directory and parse files
        for root, dirs, files in os.walk(self.target_dir):
            if '.git' in dirs: dirs.remove('.git')
            if '.venv' in dirs: dirs.remove('.venv')
            if '.cartography' in dirs: dirs.remove('.cartography')
            if 'artifacts' in dirs: dirs.remove('artifacts')
            if '__pycache__' in dirs: dirs.remove('__pycache__')
            
            for file in files:
                filepath = os.path.join(root, file)
                
                try:
                    # Enforce relative paths globally
                    identity = os.path.relpath(filepath, self.target_dir)
                    
                    if file.lower() == '.gitkeep':
                        continue
                    
                    # Extract AST data
                    ast_data = self.analyzer.analyze_file(filepath, identity=identity)
                    if not ast_data:
                        continue # Unsupported or unreadable file
                    
                    # Extract functions correctly from AST
                    funcs = ast_data.get("functions", [])
                    
                    # Calculate complexity metrics
                    module_complexity = 0.0
                    is_high_complexity = False
                    
                    if funcs:
                        module_complexity = sum(f.complexity_score for f in funcs)
                        if any(f.complexity_score > 10 for f in funcs):
                            is_high_complexity = True
                    
                    # Attach Git Metadata
                    g_meta = git_data.get(identity, {})
                    velocity_score = g_meta.get("velocity_score", 0.0)
                    
                    # Determine Layer and Informational Status
                    layer = "unknown"
                    is_info = False
                    ext = os.path.splitext(file)[1].lower()
                    base = file.lower()
                    
                    # Default informational files
                    if ext in {'.md', '.txt', '.csv', '.json', '.yml', '.yaml'} or base in {'license', 'dbt_project.yml', 'readme.md', '.gitignore', '.gitkeep'}:
                        is_info = True
                        layer = "meta"
                    
                    # Explicit override for seed files (they are raw executable data, not informational meta)
                    if identity.startswith("seeds/") or identity.startswith("data/"):
                        layer = "raw"
                        # Only treat raw data (like csv) as executable entries; preserve .gitkeep/.md as info
                        if base not in {'.gitkeep', 'readme.md'} and ext != '.md':
                            is_info = False
                    elif not is_info:
                        if "staging/" in identity:
                            layer = "staging"
                        elif "models/marts/" in identity or identity.startswith("models/"):
                            layer = "product"
                    
                    # Create Node
                    node = ModuleNode(
                        path=identity,
                        identity=identity,
                        language=os.path.splitext(file)[1][1:],
                        architecture_layer=layer,
                        is_informational=is_info,
                        imports=ast_data.get("imports", []),
                        functions=funcs,
                        classes=ast_data.get("classes", []),
                        complexity_score=module_complexity,
                        is_high_complexity=is_high_complexity,
                        velocity_score=velocity_score,
                        change_velocity_30d=velocity_score,
                        last_modified=g_meta.get("last_modified", ""),  # Rubric field
                        metadata={
                            **ast_data.get("metadata", {}),
                            "last_modified": g_meta.get("last_modified", ""),
                            "last_author": g_meta.get("last_author", ""),
                            "author_breadth": g_meta.get("author_breadth", 1)
                        }
                    )
                    self.graph_builder.add_module(node)
                except Exception as e:
                    print(f"[Warning] Surveyor Agent: Log and Skip - Error processing {file}: {e}")
                    continue

        # 2. Build edges based on imports
        print(f"Extracted {len(self.graph_builder.nodes)} modules. Building edges...")
        self.graph_builder.build_edges()
        
        # 3. Compute Intelligence Computations
        print("Computing Structural Graph Intelligence (PageRank, Dead Code, SCCs)...")
        self.graph_builder.compute_intelligence()
        
        # 4. Export JSON
        out_path = os.path.join(self.target_dir, output_json)
        self.graph_builder.export_json(out_path)
        print(f"Analysis complete. Results saved to {out_path}")
        return self.graph_builder
