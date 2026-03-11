# Codebase Cartographer

A powerful tool for autonomous code mapping, structural analysis, and data lineage intelligence. Built to achieve 100% architectural transparency.

## 🚀 Installation

Install using `uv` or `pip`:

```bash
uv pip install -e .
```

## 🛠 Usage

### Full Analysis
Analyze a repository to generate structural and lineage maps:

```bash
# Basic analyze
codebase-cartographer analyze /path/to/repo

# Rubric-aligned semantic analysis (Requires API Key)
codebase-cartographer analyze /path/to/repo --llm --velocity-days 60 --sql-dialect snowflake
```

**Options:**
- `--llm`: Enable semantic analysis (requires `OPENAI_API_KEY` or `GOOGLE_API_KEY`).
- `--velocity-days`: Window for git change velocity (default: 30).
- `--sql-dialect`: Language for SQL AST parsing (default: `duckdb`).
- `--semantic-depth`: `light` or `deep` analysis.
- `--store-embeddings`: Save vector embeddings to JSON for downstream search.

### Helper Commands
- `codebase-cartographer lineage <node_id>`: Show immediate upstream/downstream dependencies.
- `codebase-cartographer impact <node_id>`: Calculate the topological "blast radius" of a change.
- `codebase-cartographer hydrologist`: Run lineage extraction as a standalone pass.

## 📊 Output Artifacts

Results are saved to the `.cartography/` directory:
- `module_graph.json`: Structural graph containing PageRank, SCCs, complexity, and **git velocity**.
- `lineage_graph.json`: Data lineage graph with **READ/WRITE (PRODUCT) distinction** and column-level maps.
- `RECONNAISSANCE.md`: (Requires `--llm`) Automated business-level report summarizing architectural health and system purpose.

## 🤖 Semantic Intelligence

To enable LLM features, set your API keys in a `.env` file:
```bash
OPENAI_API_KEY=sk-...
# OR
GOOGLE_API_KEY=...
```

The Semanticist Agent uses **Context-Aware Budgeting** to process large codebases efficiently without exceeding API limits.

## 📂 Project Structure

- `src/cli.py`: Entry point and auxiliary commands.
- `src/orchestrator.py`: Multi-agent coordination pipeline.
- `src/agents/`: Surveyor (Structure), Hydrologist (Lineage), and Semanticist (Intelligence).
- `src/analyzers/`: Tree-sitter AST (Python, SQL, YAML) and logic hashes.
- `src/graph/`: NetworkX-powered knowledge graph with persistence.

## 🧪 Development

```bash
pytest tests/
```
