# 🗺️ Codebase Technical Overview
**Commit SHA:** `391fb7ca6ac4e19fa6a28d9b1b8ab98d505e304c`
**Generated:** 2026-03-15T01:46:20.626408
**Total Modules:** 71

## 🏗️ Architecture Overview
This repository is organized into distinct functional layers and business domains. The system manages data transformations and structural logic across multiple languages, with dependencies visualized in the lineage and module graphs.

## 📈 Critical Path
The following sequence represents the longest dependency chain in the system, making it a primary target for architectural review:
> `src/models/nodes.py` → `src/analyzers/tree_sitter_analyzer.py` → `src/analyzers/python_dataflow_analyzer.py` → `src/agents/hydrologist.py` → `src/orchestrator.py` → `tests/verify_recon.py`

## 🚿 Data Sources & Sinks
### Entry Points (Sources)
| Name | System | Environment | Namespace |
| :--- | :--- | :--- | :--- |
| `task_a` | unknown | production | unknown |

### Exit Points (Sinks)
| Name | System | Environment | Namespace |
| :--- | :--- | :--- | :--- |
| `//bucket/processed_orders.parquet` | s3 | production | s3 |
| `process_orders` | unknown | production | unknown |
| `utf-8` | unknown | production | unknown |
| `task_b` | unknown | production | unknown |

## 🚀 High-Velocity Files
| File | 30d Commits | Authors | Risk |
| :--- | :--- | :--- | :--- |
| `src/orchestrator.py` | 10 | 1 | High churn |
| `src/agents/surveyor.py` | 7 | 1 | High churn |
| `src/agents/archivist.py` | 6 | 1 | High churn |
| `src/server.py` | 6 | 1 | High churn |
| `ui/app.js` | 6 | 1 | High churn |

## 📂 Module Inventory
| Module | Domain | Rank | Sync | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `src/utils/git_provider.py` | AIIntegrationTools | 0.010 | — | Inferred purpose: This module manages 6 functions and imports 3 dependencies. Key features likely include __init__, prefetch_metadata. |
| `src/utils/llm_client.py` | AIIntegrationTools | 0.010 | — | Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, can_afford_batch. |
| `fix_pagerank.py` | Data Analytics Orchestration | 0.010 | — | The module 'fix_pagerank.py' is likely used to fix or improve the PageRank algorithm, possibly by handling data preprocessing or fixing issues in existing pagerank calculations. |
| `mock_project/dag.py` | Data Analytics Orchestration | 0.010 | — | The module 'dag.py' is part of a DAG (Directed Acyclic Graph) structure, which suggests it might be used for orchestrating tasks or workflows within an Airflow environment. |
| `mock_project/models/stg_orders.sql` | Data Analytics Orchestration | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 1 dependencies. Key features likely include stg_orders. |
| `src/analyzers/dag_config_parser.py` | Data Analytics Orchestration | 0.011 | — | Inferred purpose: This module manages 5 functions and imports 2 dependencies. Key features likely include can_handle, parse. |
| `src/analyzers/dag_parsers/plugins.py` | Data Analytics Orchestration | 0.011 | — | Inferred purpose: This module manages 4 functions and imports 4 dependencies. Key features likely include can_handle, parse. |
| `src/models/nodes.py` | Data Analytics Orchestration | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 2 dependencies. Key features likely include system coordination. |
| `src/utils/module_summary.py` | Data Analytics Orchestration | 0.011 | — | Inferred purpose: This module manages 1 functions and imports 4 dependencies. Key features likely include build_module_summary. |
| `src/utils/similarity.py` | Data Analytics Orchestration | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 2 dependencies. Key features likely include cosine_similarity. |
| `test_parse.py` | Data Analytics Orchestration | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 5 dependencies. Key features likely include system coordination. |
| `test_pr.py` | Data Analytics Orchestration | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 1 dependencies. Key features likely include system coordination. |
| `test_scope.py` | Data Analytics Orchestration | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 3 dependencies. Key features likely include resolve_table. |
| `tests/test_archivist_excellence.py` | Data Analytics Orchestration | 0.040 | — | Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include repo_path, test_artifact_metadata_header. |
| `tests/test_lineage_graph.py` | Data Analytics Orchestration | 0.011 | — | Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include test_lineage_graph_impact_analysis, test_lineage_graph_integrity. |
| `tests/test_python_dataflow.py` | Data Analytics Orchestration | 0.017 | — | Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include test_python_dataflow_pandas, test_python_dataflow_sqlalchemy. |
| `tests/test_semanticist.py` | Data Analytics Orchestration | 0.030 | — | Inferred purpose: This module manages 4 functions and imports 5 dependencies. Key features likely include mock_llm, test_semantic_analysis_flow. |
| `tests/test_sql_lineage.py` | Data Analytics Orchestration | 0.010 | — | Inferred purpose: This module manages 4 functions and imports 2 dependencies. Key features likely include test_sql_lineage_dbt_ref, test_sql_lineage_dbt_source. |
| `tests/test_surveyor.py` | Data Analytics Orchestration | 0.025 | — | Inferred purpose: This module manages 2 functions and imports 4 dependencies. Key features likely include test_surveyor_negative_dead_code, test_surveyor_phase1_5_features. |
| `tests/verify_recon.py` | Data Analytics Orchestration | 0.034 | — | Inferred purpose: This module manages 1 functions and imports 7 dependencies. Key features likely include verify_recon_generation. |
| `uv.lock` | Data Analytics Orchestration | 0.010 | — | The module 'uv.lock' does not contain any functions, classes, constants or imports that provide a clear business purpose based on the provided code implementation. |
| `src/agents/archivist.py` | DataScienceTools | 0.011 | — | Inferred purpose: This module manages 4 functions and imports 6 dependencies. Key features likely include __init__, apply_overrides. |
| `src/agents/semanticist.py` | DataScienceTools | 0.036 | — | Inferred purpose: This module manages 5 functions and imports 7 dependencies. Key features likely include __init__, analyze_modules. |
| `src/analyzers/python_dataflow_analyzer.py` | DataScienceTools | 0.016 | — | Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, _generate_logic_hash. |
| `src/analyzers/sql_lineage.py` | DataScienceTools | 0.011 | — | Inferred purpose: This module manages 8 functions and imports 10 dependencies. Key features likely include __init__, _generate_logic_hash. |
| `src/utils/git_utils.py` | DataScienceTools | 0.010 | — | Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include __init__, _run_git_cmd. |
| `src/utils/identity_resolver.py` | DataScienceTools | 0.010 | — | Inferred purpose: This module manages 6 functions and imports 4 dependencies. Key features likely include __init__, resolve. |
| `src/utils/trace_logger.py` | DataScienceTools | 0.010 | — | Inferred purpose: This module manages 3 functions and imports 5 dependencies. Key features likely include __init__, log_event. |
| `.pytest_cache/README.md` | DocumentationAndTools | 0.000 | — | Provides documentation and guidelines for using the pytest cache directory structure. |
| `README.md` | DocumentationAndTools | 0.000 | — | Provides an overview and instructions for using the project's files and directories. |
| `mock_project/models/schema.yml` | DocumentationAndTools | 0.000 | — | The 'schema.yml' file likely defines the schema for data models, specifying how data should be structured and stored in the database or other storage systems. |
| `mock_project/process_orders.py` | DocumentationAndTools | 0.010 | — | Unknown purpose (Fallback enabled) |
| `pyproject.toml` | DocumentationAndTools | 0.010 | — | Configuration file: Defines project settings, dependencies, or environment-specific parameters. |
| `src/agents/__init__.py` | DocumentationAndTools | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/agents/hydrologist.py` | DocumentationAndTools | 0.066 | — | Analyzes and provides dynamic confidence for hydrological data processing pipelines. |
| `src/agents/navigator.py` | DocumentationAndTools | 0.016 | ⚠️ Drift | Provides tools to query the codebase knowledge graph using natural language or structured queries, tracing lineage and dependencies. |
| `src/analyzers/__init__.py` | DocumentationAndTools | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/analyzers/dag_parsers/__init__.py` | DocumentationAndTools | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/analyzers/tree_sitter_analyzer.py` | DocumentationAndTools | 0.011 | — | This module analyzes code written in different languages (Python, JavaScript, YAML, SQL) using the Tree-Sitter parser. |
| `src/cli.py` | DocumentationAndTools | 0.066 | — | This module provides command-line interface functionalities for orchestrating and managing various codebase operations such as analysis, lineage tracking, impact assessment, and serving API endpoints. |
| `src/codebase_cartographer.egg-info/PKG-INFO` | DocumentationAndTools | 0.010 | — | Unknown purpose (Fallback enabled) |
| `src/graph/__init__.py` | DocumentationAndTools | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/graph/graph_builder.py` | DocumentationAndTools | 0.011 | — | This module builds a graph representation of the codebase structure by adding modules and computing intelligence based on their relationships and dependencies. |
| `src/graph/knowledge_graph.py` | DocumentationAndTools | 0.011 | — | This module manages the creation and manipulation of a knowledge graph, including adding nodes (data nodes, transformation nodes, module nodes) and edges representing lineage relationships. |
| `src/models/__init__.py` | DocumentationAndTools | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/models/lineage.py` | DocumentationAndTools | 0.010 | — | This module defines classes for different types of nodes in the knowledge graph, such as dataset roles, column references, data nodes, transformation nodes, and lineage edges. |
| `src/orchestrator.py` | DocumentationAndTools | 0.099 | — | This module orchestrates various analysis tasks for a codebase, including loading cache, saving cache, computing hashes, updating catalogs, running analyses, and generating reconnaissance reports. |
| `src/server.py` | DocumentationAndTools | 0.038 | ⚠️ Drift | This module provides the backend server for serving the UI of a codebase analysis tool, handling requests related to cloning repositories, analyzing codebases, and managing various artifacts and logs. |
| `src/utils/__init__.py` | DocumentationAndTools | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/utils/canonicalization_service.py` | DocumentationAndTools | 0.010 | — | This module provides utilities for normalizing and canonicalizing paths within a codebase, as well as detecting collisions and simplifying paths to avoid naming conflicts. |
| `src/utils/clustering.py` | DocumentationAndTools | 0.010 | — | This module clusters files or directories based on their content similarity using clustering algorithms from the SciPy library, aiding in domain identification and analysis. |
| `src/utils/semantic_index.py` | DocumentationAndTools | 0.013 | ✅ | Estimated purpose: Semantic Index — Persistent vector store for module purpose statements.  Stores embeddings as a flat JSON file in semantic_index/ directory. Provides fast cosine-similarity search without requiring an external vector DB.  Used by:   - NavigatorTools.find_implementation() (runtime lookup)   - Orchestrator (build/update on each analysis run) |
| `ui/app.js` | DocumentationAndTools | 0.010 | — | Unknown purpose (Fallback enabled) |
| `ui/index.html` | DocumentationAndTools | 0.010 | — | Unknown purpose (Fallback enabled) |
| `ui/style.css` | DocumentationAndTools | 0.010 | — | Unknown purpose (Fallback enabled) |
| `.env` | ProjectConfigurationTools | 0.010 | — | Stores environment variables for the project. |
| `.env.example` | ProjectConfigurationTools | 0.010 | — | Serves as an example configuration file for .env. |
| `.gitignore` | ProjectConfigurationTools | 0.000 | — | Defines files and directories to ignore during version control operations. |
| `.pytest_cache/v/cache/lastfailed` | ProjectConfigurationTools | 0.010 | — | Stores information about failed tests in the pytest cache. |
| `.pytest_cache/v/cache/nodeids` | ProjectConfigurationTools | 0.010 | — | Keeps track of test node IDs for pytest caching and reporting. |
| `FINAL_REPORT.md` | ProjectInsight | 0.000 | — | Contains the final report generated by a testing or deployment process. |
| `RECONNAISSANCE.md` | ProjectInsight | 0.000 | — | Documentation: Provides high-level project information, instructions, or architectural context. |
| `src/agents/surveyor.py` | ProjectInsight | 0.035 | — | Analyzes and summarizes module structures within a project for better understanding and management. |
| `semantic_index/index.json` | ResourceRepository | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/codebase_cartographer.egg-info/SOURCES.txt` | ResourceRepository | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/codebase_cartographer.egg-info/dependency_links.txt` | ResourceRepository | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/codebase_cartographer.egg-info/entry_points.txt` | ResourceRepository | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/codebase_cartographer.egg-info/requires.txt` | ResourceRepository | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `src/codebase_cartographer.egg-info/top_level.txt` | ResourceRepository | 0.000 | — | Data/Static resource: Stores structured data or plain text used by the system. |
| `.pytest_cache/.gitignore` | TestAutomationTools | 0.000 | — | Defines files and directories to ignore within the pytest cache directory structure. |
| `.pytest_cache/CACHEDIR.TAG` | TestAutomationTools | 0.010 | — | Specifies the naming convention for cache directories in the pytest cache. |

## 🚩 Technical Debt & Risks
| Area | Debt Type | Severity | Description |
| :--- | :--- | :--- | :--- |
| `src/utils/llm_client.py` | Complexity | Medium | High cyclomatic complexity. |
| `fix_pagerank.py` | Logic | Low | Produced but never consumed. |
| `mock_project/dag.py` | Logic | Low | Produced but never consumed. |
| `test_parse.py` | Logic | Low | Produced but never consumed. |
| `test_pr.py` | Logic | Low | Produced but never consumed. |
| `test_scope.py` | Logic | Low | Produced but never consumed. |
| `tests/test_archivist_excellence.py` | Logic | Low | Produced but never consumed. |
| `tests/test_lineage_graph.py` | Logic | Low | Produced but never consumed. |
| `tests/test_python_dataflow.py` | Logic | Low | Produced but never consumed. |
| `tests/test_semanticist.py` | Logic | Low | Produced but never consumed. |
| `tests/test_sql_lineage.py` | Logic | Low | Produced but never consumed. |
| `tests/test_surveyor.py` | Logic | Low | Produced but never consumed. |
| `tests/verify_recon.py` | Logic | Low | Produced but never consumed. |
| `uv.lock` | Logic | Low | Produced but never consumed. |
| `src/agents/archivist.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/agents/semanticist.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/analyzers/python_dataflow_analyzer.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/analyzers/sql_lineage.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/utils/git_utils.py` | Complexity | Medium | High cyclomatic complexity. |
| `mock_project/process_orders.py` | Logic | Low | Produced but never consumed. |
| `pyproject.toml` | Logic | Low | Produced but never consumed. |
| `src/agents/__init__.py` | Logic | Low | Produced but never consumed. |
| `src/agents/hydrologist.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/agents/hydrologist.py` | Coupling | High | Major architectural hub; critical for blast radius. |
| `src/agents/navigator.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/analyzers/__init__.py` | Logic | Low | Produced but never consumed. |
| `src/analyzers/dag_parsers/__init__.py` | Logic | Low | Produced but never consumed. |
| `src/cli.py` | Coupling | High | Major architectural hub; critical for blast radius. |
| `src/codebase_cartographer.egg-info/PKG-INFO` | Logic | Low | Produced but never consumed. |
| `src/graph/__init__.py` | Logic | Low | Produced but never consumed. |
| `src/graph/graph_builder.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/graph/knowledge_graph.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/orchestrator.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/orchestrator.py` | Coupling | High | Major architectural hub; critical for blast radius. |
| `src/server.py` | Logic | Low | Produced but never consumed. |
| `src/utils/__init__.py` | Logic | Low | Produced but never consumed. |
| `src/utils/canonicalization_service.py` | Logic | Low | Produced but never consumed. |
| `ui/app.js` | Logic | Low | Produced but never consumed. |
| `ui/index.html` | Logic | Low | Produced but never consumed. |
| `ui/style.css` | Logic | Low | Produced but never consumed. |
| `.env` | Logic | Low | Produced but never consumed. |
| `.env.example` | Logic | Low | Produced but never consumed. |
| `.pytest_cache/v/cache/lastfailed` | Logic | Low | Produced but never consumed. |
| `.pytest_cache/v/cache/nodeids` | Logic | Low | Produced but never consumed. |
| `src/agents/surveyor.py` | Complexity | Medium | High cyclomatic complexity. |
| `.pytest_cache/CACHEDIR.TAG` | Logic | Low | Produced but never consumed. |

## 🏷️ Module Purpose Index (by Domain)
### AIIntegrationTools
- **`src/utils/git_provider.py`**: Inferred purpose: This module manages 6 functions and imports 3 dependencies. Key features likely include __init__, prefetch_metadata.
- **`src/utils/llm_client.py`**: Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, can_afford_batch.

### Data Analytics Orchestration
- **`fix_pagerank.py`**: The module 'fix_pagerank.py' is likely used to fix or improve the PageRank algorithm, possibly by handling data preprocessing or fixing issues in existing pagerank calculations.
- **`mock_project/dag.py`**: The module 'dag.py' is part of a DAG (Directed Acyclic Graph) structure, which suggests it might be used for orchestrating tasks or workflows within an Airflow environment.
- **`mock_project/models/stg_orders.sql`**: Inferred purpose: This module manages 1 functions and imports 1 dependencies. Key features likely include stg_orders.
- **`src/analyzers/dag_config_parser.py`**: Inferred purpose: This module manages 5 functions and imports 2 dependencies. Key features likely include can_handle, parse.
- **`src/analyzers/dag_parsers/plugins.py`**: Inferred purpose: This module manages 4 functions and imports 4 dependencies. Key features likely include can_handle, parse.
- **`src/models/nodes.py`**: Inferred purpose: This module manages 0 functions and imports 2 dependencies. Key features likely include system coordination.
- **`src/utils/module_summary.py`**: Inferred purpose: This module manages 1 functions and imports 4 dependencies. Key features likely include build_module_summary.
- **`src/utils/similarity.py`**: Inferred purpose: This module manages 1 functions and imports 2 dependencies. Key features likely include cosine_similarity.
- **`test_parse.py`**: Inferred purpose: This module manages 0 functions and imports 5 dependencies. Key features likely include system coordination.
- **`test_pr.py`**: Inferred purpose: This module manages 0 functions and imports 1 dependencies. Key features likely include system coordination.
- **`test_scope.py`**: Inferred purpose: This module manages 1 functions and imports 3 dependencies. Key features likely include resolve_table.
- **`tests/test_archivist_excellence.py`**: Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include repo_path, test_artifact_metadata_header.
- **`tests/test_lineage_graph.py`**: Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include test_lineage_graph_impact_analysis, test_lineage_graph_integrity.
- **`tests/test_python_dataflow.py`**: Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include test_python_dataflow_pandas, test_python_dataflow_sqlalchemy.
- **`tests/test_semanticist.py`**: Inferred purpose: This module manages 4 functions and imports 5 dependencies. Key features likely include mock_llm, test_semantic_analysis_flow.
- **`tests/test_sql_lineage.py`**: Inferred purpose: This module manages 4 functions and imports 2 dependencies. Key features likely include test_sql_lineage_dbt_ref, test_sql_lineage_dbt_source.
- **`tests/test_surveyor.py`**: Inferred purpose: This module manages 2 functions and imports 4 dependencies. Key features likely include test_surveyor_negative_dead_code, test_surveyor_phase1_5_features.
- **`tests/verify_recon.py`**: Inferred purpose: This module manages 1 functions and imports 7 dependencies. Key features likely include verify_recon_generation.
- **`uv.lock`**: The module 'uv.lock' does not contain any functions, classes, constants or imports that provide a clear business purpose based on the provided code implementation.

### DataScienceTools
- **`src/agents/archivist.py`**: Inferred purpose: This module manages 4 functions and imports 6 dependencies. Key features likely include __init__, apply_overrides.
- **`src/agents/semanticist.py`**: Inferred purpose: This module manages 5 functions and imports 7 dependencies. Key features likely include __init__, analyze_modules.
- **`src/analyzers/python_dataflow_analyzer.py`**: Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, _generate_logic_hash.
- **`src/analyzers/sql_lineage.py`**: Inferred purpose: This module manages 8 functions and imports 10 dependencies. Key features likely include __init__, _generate_logic_hash.
- **`src/utils/git_utils.py`**: Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include __init__, _run_git_cmd.
- **`src/utils/identity_resolver.py`**: Inferred purpose: This module manages 6 functions and imports 4 dependencies. Key features likely include __init__, resolve.
- **`src/utils/trace_logger.py`**: Inferred purpose: This module manages 3 functions and imports 5 dependencies. Key features likely include __init__, log_event.

### DocumentationAndTools
- **`.pytest_cache/README.md`**: Provides documentation and guidelines for using the pytest cache directory structure.
- **`README.md`**: Provides an overview and instructions for using the project's files and directories.
- **`mock_project/models/schema.yml`**: The 'schema.yml' file likely defines the schema for data models, specifying how data should be structured and stored in the database or other storage systems.
- **`mock_project/process_orders.py`**: Unknown purpose (Fallback enabled)
- **`pyproject.toml`**: Configuration file: Defines project settings, dependencies, or environment-specific parameters.
- **`src/agents/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/agents/hydrologist.py`**: Analyzes and provides dynamic confidence for hydrological data processing pipelines.
- **`src/agents/navigator.py`**: Provides tools to query the codebase knowledge graph using natural language or structured queries, tracing lineage and dependencies.
- **`src/analyzers/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/analyzers/dag_parsers/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/analyzers/tree_sitter_analyzer.py`**: This module analyzes code written in different languages (Python, JavaScript, YAML, SQL) using the Tree-Sitter parser.
- **`src/cli.py`**: This module provides command-line interface functionalities for orchestrating and managing various codebase operations such as analysis, lineage tracking, impact assessment, and serving API endpoints.
- **`src/codebase_cartographer.egg-info/PKG-INFO`**: Unknown purpose (Fallback enabled)
- **`src/graph/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/graph/graph_builder.py`**: This module builds a graph representation of the codebase structure by adding modules and computing intelligence based on their relationships and dependencies.
- **`src/graph/knowledge_graph.py`**: This module manages the creation and manipulation of a knowledge graph, including adding nodes (data nodes, transformation nodes, module nodes) and edges representing lineage relationships.
- **`src/models/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/models/lineage.py`**: This module defines classes for different types of nodes in the knowledge graph, such as dataset roles, column references, data nodes, transformation nodes, and lineage edges.
- **`src/orchestrator.py`**: This module orchestrates various analysis tasks for a codebase, including loading cache, saving cache, computing hashes, updating catalogs, running analyses, and generating reconnaissance reports.
- **`src/server.py`**: This module provides the backend server for serving the UI of a codebase analysis tool, handling requests related to cloning repositories, analyzing codebases, and managing various artifacts and logs.
- **`src/utils/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/utils/canonicalization_service.py`**: This module provides utilities for normalizing and canonicalizing paths within a codebase, as well as detecting collisions and simplifying paths to avoid naming conflicts.
- **`src/utils/clustering.py`**: This module clusters files or directories based on their content similarity using clustering algorithms from the SciPy library, aiding in domain identification and analysis.
- **`src/utils/semantic_index.py`**: Estimated purpose: Semantic Index — Persistent vector store for module purpose statements.

Stores embeddings as a flat JSON file in semantic_index/ directory.
Provides fast cosine-similarity search without requiring an external vector DB.

Used by:
  - NavigatorTools.find_implementation() (runtime lookup)
  - Orchestrator (build/update on each analysis run)
- **`ui/app.js`**: Unknown purpose (Fallback enabled)
- **`ui/index.html`**: Unknown purpose (Fallback enabled)
- **`ui/style.css`**: Unknown purpose (Fallback enabled)

### ProjectConfigurationTools
- **`.env`**: Stores environment variables for the project.
- **`.env.example`**: Serves as an example configuration file for .env.
- **`.gitignore`**: Defines files and directories to ignore during version control operations.
- **`.pytest_cache/v/cache/lastfailed`**: Stores information about failed tests in the pytest cache.
- **`.pytest_cache/v/cache/nodeids`**: Keeps track of test node IDs for pytest caching and reporting.

### ProjectInsight
- **`FINAL_REPORT.md`**: Contains the final report generated by a testing or deployment process.
- **`RECONNAISSANCE.md`**: Documentation: Provides high-level project information, instructions, or architectural context.
- **`src/agents/surveyor.py`**: Analyzes and summarizes module structures within a project for better understanding and management.

### ResourceRepository
- **`semantic_index/index.json`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`src/codebase_cartographer.egg-info/SOURCES.txt`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`src/codebase_cartographer.egg-info/dependency_links.txt`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`src/codebase_cartographer.egg-info/entry_points.txt`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`src/codebase_cartographer.egg-info/requires.txt`**: Data/Static resource: Stores structured data or plain text used by the system.
- **`src/codebase_cartographer.egg-info/top_level.txt`**: Data/Static resource: Stores structured data or plain text used by the system.

### TestAutomationTools
- **`.pytest_cache/.gitignore`**: Defines files and directories to ignore within the pytest cache directory structure.
- **`.pytest_cache/CACHEDIR.TAG`**: Specifies the naming convention for cache directories in the pytest cache.
