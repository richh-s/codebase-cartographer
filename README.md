# Codebase Cartographer

A tool for autonomous code mapping and data lineage intelligence.

## 🚀 Installation

Install using `uv` or `pip`:

```bash
uv pip install -e .
```

## 🛠 Usage

To analyze a repository and generate mapping artifacts:

```bash
codebase-cartographer analyze /path/to/your/repo
```

This will generate a `.cartography/` directory in the target repository containing:
- `module_graph.json`: Structural dependency graph, PageRank, and complexity metrics.
- `lineage_graph.json`: Data lineage extraction from Python, SQL, and YAML.
- `RECONNAISSANCE.md`: (Requires `--llm`) AI-generated business reconnaissance report summarizing system purpose and architectural health.

## 🤖 Semantic Intelligence (Phase 3)

To enable LLM-powered analysis, set your API keys in a `.env` file:
```bash
GOOGLE_API_KEY=your_key
# OR
OPENAI_API_KEY=your_key
```

Run full semantic analysis:
```bash
codebase-cartographer analyze /path/to/repo --llm --semantic-depth full
```

## 📂 Project Structure

- `src/cli.py`: CLI entry point.
- `src/orchestrator.py`: Coordinates agents.
- `src/agents/`: Surveyor (Structure) and Hydrologist (Lineage) agents.
- `src/analyzers/`: SQL, Python, and YAML parsers.
- `src/graph/`: Knowledge and Lineage graph implementations.
- `src/models/`: Pydantic schemas.

## 🧪 Development

Run tests with `pytest`:

```bash
pytest tests/
```
