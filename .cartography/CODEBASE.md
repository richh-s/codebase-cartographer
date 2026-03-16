# 🗺️ Codebase Technical Overview
**Commit SHA:** `ea72a6cf65c2e851ce670edbad6df96c6b5028f3`
**Analysis Timestamp:** `2026-03-16 08:53:02`
**Total Modules:** 72

## 🏗️ Architecture Layer Summary
This repository is organized into functional layers that manage data flow and logic.

| Layer | Module Count | Description |
| :--- | :--- | :--- |
| **agent** | 6 | General system component. |
| **analyzer** | 7 | General system component. |
| **core** | 10 | Primary application logic. |
| **graph** | 3 | General system component. |
| **meta** | 13 | Configuration and documentation. |
| **model** | 4 | General system component. |
| **test** | 7 | General system component. |
| **tooling** | 2 | General system component. |
| **unknown** | 9 | General system component. |
| **utility** | 11 | Shared helper functions. |

## 📈 Critical Dependency Path
The sequence below represents the longest data transformation chain. Changes to these files have the highest probability of cascading impacts:

┌─ **src/models/nodes.py**  
  └─ **src/analyzers/tree_sitter_analyzer.py**  
  └─ **src/analyzers/python_dataflow_analyzer.py**  
  └─ **src/agents/hydrologist.py**  
  └─ **src/orchestrator.py**  
  └─ **tests/verify_recon.py**

## 🚩 High-Impact Modules (Architectural Hubs)
The following files are central to the codebase. Modifications here require careful review.
| Hub Module | Importance | Layer | Potential Risk |
| :--- | :--- | :--- | :--- |
| `src/orchestrator.py` | **100** | core | High Blast Radius |
| `src/cli.py` | **63** | core | High Blast Radius |
| `src/agents/hydrologist.py` | **62** | agent | High Blast Radius |

## 🚿 Data Life Cycle
- **Primary Sources:** 1 entry points detected.
- **Primary Sinks:** 4 terminal datasets detected.

**Key Sources:** `task_a`

**Key Sinks:** `//bucket/processed_orders.parquet`, `process_orders`, `utf-8`, `task_b`

## 📂 Module Inventory
| Module | Layer | Importance | Rank | Sync | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `src/agents/archivist.py` | agent | 2 | 0.011 | — | Inferred purpose: This module manages 5 functions and imports 6 dependencies. |
| `src/agents/semanticist.py` | agent | 29 | 0.036 | — | Inferred purpose: This module manages 5 functions and imports 7 dependencies. |
| `src/agents/surveyor.py` | agent | 28 | 0.035 | — | Inferred purpose: This module manages 3 functions and imports 7 dependencies. |
| `src/analyzers/tree_sitter_analyzer.py` | analyzer | 2 | 0.011 | — | Inferred purpose: This module manages 14 functions and imports 9 dependencies. |
| `src/graph/graph_builder.py` | graph | 2 | 0.011 | — | Inferred purpose: This module manages 7 functions and imports 4 dependencies. |
| `src/graph/knowledge_graph.py` | graph | 2 | 0.011 | — | Inferred purpose: This module manages 18 functions and imports 3 dependencies. |
| `src/orchestrator.py` | core | 100 | 0.099 | — | Inferred purpose: This module manages 11 functions and imports 15 dependencies. |
| `src/utils/canonicalization_service.py` | utility | 1 | 0.010 | — | Inferred purpose: This module manages 5 functions and imports 2 dependencies. |
| `src/utils/identity_resolver.py` | utility | 1 | 0.010 | — | Inferred purpose: This module manages 6 functions and imports 4 dependencies. |
| `src/utils/llm_client.py` | utility | 1 | 0.010 | — | Inferred purpose: This module manages 8 functions and imports 7 dependencies. |
| `src/utils/trace_logger.py` | utility | 1 | 0.010 | — | Inferred purpose: This module manages 3 functions and imports 5 dependencies. |
| `mock_project/models/schema.yml` | tooling | 1 | 0.000 | — | Configuration file: Defines project settings, dependencies, or environment-specific parameters. |
| `pyproject.toml` | tooling | 1 | 0.010 | — | Configuration file: Defines project settings, dependencies, or environment-specific parameters. |
| `src/agents/navigator.py` | agent | 7 | 0.016 | — | Estimated purpose: Navigator Agent — Phase 5: The Query Interface

A tool-loop agent that provides four query tools for interrogating the
codebase knowledge graph with natural language and structured queries. |
| `src/server.py` | core | 32 | 0.038 | — | Estimated purpose: Codebase Cartographer — Web UI Server
FastAPI backend that serves the UI and exposes REST APIs for the frontend. |
| `src/utils/semantic_index.py` | utility | 4 | 0.013 | — | Estimated purpose: Semantic Index — Persistent vector store for module purpose statements. |
| `mock_project/models/stg_orders.sql` | model | 1 | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 1 dependencies. |
| `src/agents/hydrologist.py` | agent | 62 | 0.066 | — | Inferred purpose: This module manages 6 functions and imports 14 dependencies. |
| `src/analyzers/dag_config_parser.py` | analyzer | 2 | 0.011 | — | Inferred purpose: This module manages 5 functions and imports 2 dependencies. |
| `src/analyzers/dag_parsers/plugins.py` | analyzer | 2 | 0.011 | — | Inferred purpose: This module manages 4 functions and imports 4 dependencies. |
| `src/analyzers/python_dataflow_analyzer.py` | analyzer | 7 | 0.016 | — | Inferred purpose: This module manages 8 functions and imports 7 dependencies. |
| `src/analyzers/sql_lineage.py` | analyzer | 2 | 0.011 | — | Inferred purpose: This module manages 8 functions and imports 10 dependencies. |
| `src/models/lineage.py` | model | 1 | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 4 dependencies. |
| `src/utils/clustering.py` | utility | 1 | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 2 dependencies. |
| `src/utils/git_utils.py` | utility | 1 | 0.010 | — | Inferred purpose: This module manages 3 functions and imports 3 dependencies. |
| `src/utils/module_summary.py` | utility | 2 | 0.011 | — | Inferred purpose: This module manages 1 functions and imports 4 dependencies. |
| `src/utils/similarity.py` | utility | 1 | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 2 dependencies. |
| `test_scope.py` | core | 1 | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 3 dependencies. |
| `tests/test_archivist_excellence.py` | test | 34 | 0.040 | — | Inferred purpose: This module manages 8 functions and imports 7 dependencies. |
| `tests/test_lineage_graph.py` | test | 2 | 0.011 | — | Inferred purpose: This module manages 3 functions and imports 3 dependencies. |
| `tests/test_python_dataflow.py` | test | 8 | 0.017 | — | Inferred purpose: This module manages 3 functions and imports 3 dependencies. |
| `tests/test_semanticist.py` | test | 22 | 0.030 | — | Inferred purpose: This module manages 4 functions and imports 5 dependencies. |
| `tests/test_sql_lineage.py` | test | 1 | 0.010 | — | Inferred purpose: This module manages 4 functions and imports 2 dependencies. |
| `tests/test_surveyor.py` | test | 17 | 0.025 | — | Inferred purpose: This module manages 2 functions and imports 4 dependencies. |
| `tests/verify_recon.py` | test | 26 | 0.034 | — | Inferred purpose: This module manages 1 functions and imports 7 dependencies. |
| `src/utils/git_provider.py` | utility | 1 | 0.010 | — | Inferred purpose: This module manages 6 functions and imports 3 dependencies. |
| `src/cli.py` | core | 63 | 0.066 | — | Inferred purpose: This module manages 7 functions and imports 16 dependencies. |
| `mock_project/process_orders.py` | core | 1 | 0.010 | — | This file is probably a script for processing orders, handling data operations such as loading and manipulating datasets. |
| `src/codebase_cartographer.egg-info/PKG-INFO` | core | 1 | 0.010 | — | This file likely contains metadata about the codebase cartographer package, including its name, version, and dependencies. |
| `ui/app.js` | unknown | 1 | 0.010 | — | This JavaScript file is probably part of a web application's frontend logic, handling user interactions or rendering UI elements. |
| `ui/style.css` | unknown | 1 | 0.010 | — | This CSS file is probably used to style elements within the web application's UI, ensuring visual consistency and responsiveness. |
| `.env` | unknown | 1 | 0.010 | — | Environment variables: Manages secrets and environment-specific configurations. |
| `.env.example` | unknown | 1 | 0.010 | — | Environment variables: Manages secrets and environment-specific configurations. |
| `.pytest_cache/README.md` | meta | 1 | 0.000 | — | Documentation: Provides high-level project information, instructions, or architectural context. |
| `FINAL_REPORT.md` | meta | 1 | 0.000 | — | Documentation: Provides high-level project information, instructions, or architectural context. |
| `README.md` | meta | 1 | 0.000 | — | Documentation: Provides high-level project information, instructions, or architectural context. |
| `RECONNAISSANCE.md` | meta | 1 | 0.000 | — | Documentation: Provides high-level project information, instructions, or architectural context. |
| `TECHNICAL_GUIDE.md` | meta | 1 | 0.000 | — | Documentation: Provides high-level project information, instructions, or architectural context. |
| `semantic_index/index.json` | meta | 1 | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/agents/__init__.py` | agent | 1 | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/analyzers/__init__.py` | analyzer | 1 | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/analyzers/dag_parsers/__init__.py` | analyzer | 1 | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/codebase_cartographer.egg-info/SOURCES.txt` | meta | 1 | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/codebase_cartographer.egg-info/dependency_links.txt` | meta | 1 | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/codebase_cartographer.egg-info/entry_points.txt` | meta | 1 | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/codebase_cartographer.egg-info/requires.txt` | meta | 1 | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/codebase_cartographer.egg-info/top_level.txt` | meta | 1 | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/graph/__init__.py` | graph | 1 | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/models/__init__.py` | model | 1 | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/utils/__init__.py` | utility | 1 | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `.gitignore` | meta | 1 | 0.000 | — | This module is likely used for specifying files and directories to ignore when using Git. |
| `.pytest_cache/.gitignore` | meta | 1 | 0.000 | — | This module is probably used for specifying files and directories to ignore within the pytest cache directory. |
| `.pytest_cache/CACHEDIR.TAG` | unknown | 1 | 0.010 | — | This file likely contains metadata about the pytest cache directory, possibly indicating its name or location. |
| `.pytest_cache/v/cache/lastfailed` | unknown | 1 | 0.010 | — | This module is probably used to store information about failed tests within the pytest cache. |
| `.pytest_cache/v/cache/nodeids` | unknown | 1 | 0.010 | — | This module likely stores information related to test nodes (e. |
| `fix_pagerank.py` | core | 1 | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 1 dependencies. |
| `mock_project/dag.py` | core | 1 | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 1 dependencies. |
| `src/models/nodes.py` | model | 1 | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 2 dependencies. |
| `test_parse.py` | core | 1 | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 5 dependencies. |
| `test_pr.py` | core | 1 | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 1 dependencies. |
| `ui/index.html` | unknown | 1 | 0.010 | — | This HTML file is likely the main entry point for a web application’s user interface, defining its structure and layout. |
| `uv.lock` | unknown | 1 | 0.010 | — | The module 'uv. |

## 🏷️ Business Domain Map
### AIKnowledgeOrchestration
- **`src/orchestrator.py`**: Inferred purpose: This module manages 11 functions and imports 15 dependencies. Key features likely include __init__, _load_cache.
- **`src/analyzers/tree_sitter_analyzer.py`**: Inferred purpose: This module manages 14 functions and imports 9 dependencies. Key features likely include get_language, __init__.
- **`src/graph/knowledge_graph.py`**: Inferred purpose: This module manages 18 functions and imports 3 dependencies. Key features likely include __init__, add_data_node.
- **`src/graph/graph_builder.py`**: Inferred purpose: This module manages 7 functions and imports 4 dependencies. Key features likely include __init__, add_module.
- **`src/agents/surveyor.py`**: Inferred purpose: This module manages 3 functions and imports 7 dependencies. Key features likely include __init__, _get_identity.
- **`src/agents/archivist.py`**: Inferred purpose: This module manages 5 functions and imports 6 dependencies. Key features likely include __init__, apply_overrides.
- **`src/agents/semanticist.py`**: Inferred purpose: This module manages 5 functions and imports 7 dependencies. Key features likely include __init__, analyze_modules.
- **`src/utils/trace_logger.py`**: Inferred purpose: This module manages 3 functions and imports 5 dependencies. Key features likely include __init__, log_event.
- **`src/utils/identity_resolver.py`**: Inferred purpose: This module manages 6 functions and imports 4 dependencies. Key features likely include __init__, resolve.
- **`src/utils/llm_client.py`**: Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, can_afford_batch.
- **`src/utils/canonicalization_service.py`**: Inferred purpose: This module manages 5 functions and imports 2 dependencies. Key features likely include __init__, normalize.

### CodebaseExplorer
- **`pyproject.toml`**: Configuration file: Defines project settings, dependencies, or environment-specific parameters.
- **`mock_project/models/schema.yml`**: Configuration file: Defines project settings, dependencies, or environment-specific parameters.
- **`src/server.py`**: Estimated purpose: Codebase Cartographer — Web UI Server
FastAPI backend that serves the UI and exposes REST APIs for the frontend.

Usage:
    python src/server.py <repo_path>
    # Or via CLI:
    python src/cli.py serve <repo_path>
- **`src/agents/navigator.py`**: Estimated purpose: Navigator Agent — Phase 5: The Query Interface

A tool-loop agent that provides four query tools for interrogating the
codebase knowledge graph with natural language and structured queries.

Tools:
    find_implementation(concept) - Semantic search via embeddings
    trace_lineage(dataset, direction) - Graph traversal upstream/downstream
    blast_radius(module_path) - Full dependency impact analysis
    explain_module(path) - Generative LLM explanation with evidence

Every answer cites: source file, line range, and analysis method
(static_analysis | llm_inference).
- **`src/utils/semantic_index.py`**: Estimated purpose: Semantic Index — Persistent vector store for module purpose statements.

Stores embeddings as a flat JSON file in semantic_index/ directory.
Provides fast cosine-similarity search without requiring an external vector DB.

Used by:
  - NavigatorTools.find_implementation() (runtime lookup)
  - Orchestrator (build/update on each analysis run)

### DataIntegrationAndAnalysis
- **`test_scope.py`**: Inferred purpose: This module manages 1 functions and imports 3 dependencies. Key features likely include resolve_table.
- **`mock_project/models/stg_orders.sql`**: Inferred purpose: This module manages 1 functions and imports 1 dependencies. Key features likely include stg_orders.
- **`tests/test_surveyor.py`**: Inferred purpose: This module manages 2 functions and imports 4 dependencies. Key features likely include test_surveyor_negative_dead_code, test_surveyor_phase1_5_features.
- **`tests/verify_recon.py`**: Inferred purpose: This module manages 1 functions and imports 7 dependencies. Key features likely include verify_recon_generation.
- **`tests/test_sql_lineage.py`**: Inferred purpose: This module manages 4 functions and imports 2 dependencies. Key features likely include test_sql_lineage_dbt_ref, test_sql_lineage_dbt_source.
- **`tests/test_lineage_graph.py`**: Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include test_lineage_graph_impact_analysis, test_lineage_graph_integrity.
- **`tests/test_python_dataflow.py`**: Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include test_python_dataflow_pandas, test_python_dataflow_sqlalchemy.
- **`tests/test_semanticist.py`**: Inferred purpose: This module manages 4 functions and imports 5 dependencies. Key features likely include mock_llm, test_semantic_analysis_flow.
- **`tests/test_archivist_excellence.py`**: Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include repo_path, test_artifact_metadata_header.
- **`src/analyzers/sql_lineage.py`**: Inferred purpose: This module manages 8 functions and imports 10 dependencies. Key features likely include __init__, _generate_logic_hash.
- **`src/analyzers/dag_config_parser.py`**: Inferred purpose: This module manages 5 functions and imports 2 dependencies. Key features likely include can_handle, parse.
- **`src/analyzers/python_dataflow_analyzer.py`**: Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, _generate_logic_hash.
- **`src/analyzers/dag_parsers/plugins.py`**: Inferred purpose: This module manages 4 functions and imports 4 dependencies. Key features likely include can_handle, parse.
- **`src/agents/hydrologist.py`**: Inferred purpose: This module manages 6 functions and imports 14 dependencies. Key features likely include __init__, _get_git_version.
- **`src/utils/clustering.py`**: Inferred purpose: This module manages 1 functions and imports 2 dependencies. Key features likely include cluster_into_domains.
- **`src/utils/similarity.py`**: Inferred purpose: This module manages 1 functions and imports 2 dependencies. Key features likely include cosine_similarity.
- **`src/utils/module_summary.py`**: Inferred purpose: This module manages 1 functions and imports 4 dependencies. Key features likely include build_module_summary.
- **`src/utils/git_utils.py`**: Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include __init__, _run_git_cmd.
- **`src/models/lineage.py`**: Inferred purpose: This module manages 1 functions and imports 4 dependencies. Key features likely include is_heuristic.

### GitManagement
- **`src/utils/git_provider.py`**: Inferred purpose: This module manages 6 functions and imports 3 dependencies. Key features likely include __init__, prefetch_metadata.

### Hydrological Analysis CLI
- **`src/cli.py`**: Inferred purpose: This module manages 7 functions and imports 16 dependencies. Key features likely include analyze, hydrologist.

### OrderEngine
- **`mock_project/process_orders.py`**: This file is probably a script for processing orders, handling data operations such as loading and manipulating datasets.
- **`ui/style.css`**: This CSS file is probably used to style elements within the web application's UI, ensuring visual consistency and responsiveness.
- **`ui/app.js`**: This JavaScript file is probably part of a web application's frontend logic, handling user interactions or rendering UI elements.
- **`src/codebase_cartographer.egg-info/PKG-INFO`**: This file likely contains metadata about the codebase cartographer package, including its name, version, and dependencies.

### ProjectDocumentationAndConfiguration
- **`FINAL_REPORT.md`**: Documentation: Provides high-level project information, instructions, or architectural context.
- **`TECHNICAL_GUIDE.md`**: Documentation: Provides high-level project information, instructions, or architectural context.
- **`RECONNAISSANCE.md`**: Documentation: Provides high-level project information, instructions, or architectural context.
- **`README.md`**: Documentation: Provides high-level project information, instructions, or architectural context.
- **`.env`**: Environment variables: Manages secrets and environment-specific configurations.
- **`.env.example`**: Environment variables: Manages secrets and environment-specific configurations.
- **`semantic_index/index.json`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`.pytest_cache/README.md`**: Documentation: Provides high-level project information, instructions, or architectural context.
- **`src/analyzers/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/analyzers/dag_parsers/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/graph/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/agents/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/utils/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/models/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/codebase_cartographer.egg-info/SOURCES.txt`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`src/codebase_cartographer.egg-info/entry_points.txt`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`src/codebase_cartographer.egg-info/requires.txt`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`src/codebase_cartographer.egg-info/top_level.txt`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`src/codebase_cartographer.egg-info/dependency_links.txt`**: Data/Static resource: Stores structured data or plain text used by the system.

### System Coordination Tools
- **`uv.lock`**: The module 'uv.lock' does not contain any functions, classes, constants or imports that provide a clear business purpose based on the provided code implementation.
- **`test_parse.py`**: Inferred purpose: This module manages 0 functions and imports 5 dependencies. Key features likely include system coordination.
- **`.gitignore`**: This module is likely used for specifying files and directories to ignore when using Git.
- **`test_pr.py`**: Inferred purpose: This module manages 0 functions and imports 1 dependencies. Key features likely include system coordination.
- **`fix_pagerank.py`**: Inferred purpose: This module manages 0 functions and imports 1 dependencies. Key features likely include system coordination.
- **`mock_project/dag.py`**: Inferred purpose: This module manages 0 functions and imports 1 dependencies. Key features likely include system coordination.
- **`ui/index.html`**: This HTML file is likely the main entry point for a web application’s user interface, defining its structure and layout.
- **`.pytest_cache/CACHEDIR.TAG`**: This file likely contains metadata about the pytest cache directory, possibly indicating its name or location.
- **`.pytest_cache/.gitignore`**: This module is probably used for specifying files and directories to ignore within the pytest cache directory.
- **`.pytest_cache/v/cache/nodeids`**: This module likely stores information related to test nodes (e.g., function names or identifiers) within the pytest cache.
- **`.pytest_cache/v/cache/lastfailed`**: This module is probably used to store information about failed tests within the pytest cache.
- **`src/models/nodes.py`**: Inferred purpose: This module manages 0 functions and imports 2 dependencies. Key features likely include system coordination.
