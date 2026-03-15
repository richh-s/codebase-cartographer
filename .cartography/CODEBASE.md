# 🗺️ Codebase Technical Overview
**Commit SHA:** `589927b72c7b78b3e4124459caef8516f5648a58`
**Generated:** 2026-03-15T04:07:07.648422
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
| `src/orchestrator.py` | 12 | 1 | High churn |
| `src/agents/archivist.py` | 7 | 1 | High churn |
| `src/agents/surveyor.py` | 7 | 1 | High churn |
| `semantic_index/index.json` | 7 | 1 | High churn |
| `src/server.py` | 6 | 1 | High churn |
| `ui/app.js` | 6 | 1 | High churn |
| `src/agents/semanticist.py` | 6 | 1 | High churn |

## 📂 Module Inventory
| Module | Domain | Rank | Sync | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `.pytest_cache/README.md` | CodeBaseOrchestrator | 0.000 | — | Provides documentation and guidelines for using the pytest cache directory structure. |
| `fix_pagerank.py` | CodeBaseOrchestrator | 0.010 | — | The module 'fix_pagerank.py' is likely used to fix or improve the PageRank algorithm, possibly by handling data preprocessing or fixing issues in existing pagerank calculations. |
| `mock_project/dag.py` | CodeBaseOrchestrator | 0.010 | — | The module 'dag.py' is part of a DAG (Directed Acyclic Graph) structure, which suggests it might be used for orchestrating tasks or workflows within an Airflow environment. |
| `mock_project/models/schema.yml` | CodeBaseOrchestrator | 0.000 | — | The 'schema.yml' file likely defines the schema for data models, specifying how data should be structured and stored in the database or other storage systems. |
| `src/cli.py` | CodeBaseOrchestrator | 0.066 | — | This module provides command-line interface functionalities for orchestrating and managing various codebase operations such as analysis, lineage tracking, impact assessment, and serving API endpoints. |
| `src/graph/graph_builder.py` | CodeBaseOrchestrator | 0.011 | — | This module builds a graph representation of the codebase structure by adding modules and computing intelligence based on their relationships and dependencies. |
| `src/graph/knowledge_graph.py` | CodeBaseOrchestrator | 0.011 | — | This module manages the creation and manipulation of a knowledge graph representing data lineage, including adding nodes for different types of entities (data nodes, transformation nodes, module nodes) and edges between them. |
| `src/models/lineage.py` | CodeBaseOrchestrator | 0.010 | — | This module defines classes representing various components in the data lineage graph such as dataset roles, column references, data nodes, transformation nodes, and lineage edges, which are essential for tracking how data flows through different stages of processing. |
| `src/orchestrator.py` | CodeBaseOrchestrator | 0.099 | — | This module orchestrates the analysis process by managing tasks such as loading and saving cache, computing hashes, propagating domains, running analyses, and generating reports, ensuring that data lineage information is accurately tracked throughout a repository. |
| `src/server.py` | CodeBaseOrchestrator | 0.038 | ⚠️ Drift | This module provides the backend for a web UI server that serves REST APIs to interact with the codebase analysis and management functionalities, including cloning repositories, analyzing them, and providing metadata. |
| `src/utils/canonicalization_service.py` | CodeBaseOrchestrator | 0.010 | — | This module handles the normalization and canonicalization of paths to ensure consistency in how files are referenced within a codebase, which is crucial for accurate data lineage tracking. |
| `src/utils/clustering.py` | CodeBaseOrchestrator | 0.010 | — | This module clusters different parts of the codebase into domains based on their similarity and dependencies, aiding in understanding how various components interact within a repository. |
| `src/utils/git_provider.py` | CodeBaseOrchestrator | 0.010 | — | This module provides utilities for interacting with Git repositories to fetch metadata such as file metrics, current SHA, and changed files, which is essential for tracking changes in the codebase over time. |
| `uv.lock` | CodeBaseOrchestrator | 0.010 | — | The module 'uv.lock' does not contain any functions, classes, constants or imports that provide a clear business purpose based on the provided code implementation. |
| `mock_project/process_orders.py` | CodeInsight | 0.010 | — | Unknown purpose (Fallback enabled) |
| `pyproject.toml` | CodeInsight | 0.010 | — | Configuration file: Defines project settings, dependencies, or environment-specific parameters. |
| `src/agents/__init__.py` | CodeInsight | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/agents/hydrologist.py` | CodeInsight | 0.066 | — | Analyzes and provides dynamic confidence for hydrological data processing pipelines. |
| `src/agents/navigator.py` | CodeInsight | 0.016 | ⚠️ Drift | Provides tools to query the codebase knowledge graph using natural language or structured queries, tracing lineage and dependencies. |
| `src/analyzers/__init__.py` | CodeInsight | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/analyzers/dag_parsers/__init__.py` | CodeInsight | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/analyzers/tree_sitter_analyzer.py` | CodeInsight | 0.011 | — | This module analyzes code written in different languages (Python, JavaScript, YAML, SQL) using the Tree-Sitter parser. |
| `src/codebase_cartographer.egg-info/PKG-INFO` | CodeInsight | 0.010 | — | Unknown purpose (Fallback enabled) |
| `src/graph/__init__.py` | CodeInsight | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/models/__init__.py` | CodeInsight | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/utils/__init__.py` | CodeInsight | 0.010 | — | Package initialization: Defines the module structure and exposes public interfaces for this directory. |
| `src/utils/semantic_index.py` | CodeInsight | 0.013 | ✅ | Estimated purpose: Semantic Index — Persistent vector store for module purpose statements.  Stores embeddings as a flat JSON file in semantic_index/ directory. Provides fast cosine-similarity search without requiring an external vector DB.  Used by:   - NavigatorTools.find_implementation() (runtime lookup)   - Orchestrator (build/update on each analysis run) |
| `ui/app.js` | CodeInsight | 0.010 | — | Unknown purpose (Fallback enabled) |
| `ui/index.html` | CodeInsight | 0.010 | — | Unknown purpose (Fallback enabled) |
| `ui/style.css` | CodeInsight | 0.010 | — | Unknown purpose (Fallback enabled) |
| `mock_project/models/stg_orders.sql` | DataIntegrationAndAnalysis | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 1 dependencies. Key features likely include stg_orders. |
| `src/analyzers/dag_config_parser.py` | DataIntegrationAndAnalysis | 0.011 | — | Inferred purpose: This module manages 5 functions and imports 2 dependencies. Key features likely include can_handle, parse. |
| `src/analyzers/dag_parsers/plugins.py` | DataIntegrationAndAnalysis | 0.011 | — | Inferred purpose: This module manages 4 functions and imports 4 dependencies. Key features likely include can_handle, parse. |
| `src/models/nodes.py` | DataIntegrationAndAnalysis | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 2 dependencies. Key features likely include system coordination. |
| `src/utils/module_summary.py` | DataIntegrationAndAnalysis | 0.011 | — | Inferred purpose: This module manages 1 functions and imports 4 dependencies. Key features likely include build_module_summary. |
| `src/utils/similarity.py` | DataIntegrationAndAnalysis | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 2 dependencies. Key features likely include cosine_similarity. |
| `test_parse.py` | DataIntegrationAndAnalysis | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 5 dependencies. Key features likely include system coordination. |
| `test_pr.py` | DataIntegrationAndAnalysis | 0.010 | — | Inferred purpose: This module manages 0 functions and imports 1 dependencies. Key features likely include system coordination. |
| `test_scope.py` | DataIntegrationAndAnalysis | 0.010 | — | Inferred purpose: This module manages 1 functions and imports 3 dependencies. Key features likely include resolve_table. |
| `tests/test_archivist_excellence.py` | DataIntegrationAndAnalysis | 0.040 | — | Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include repo_path, test_artifact_metadata_header. |
| `tests/test_lineage_graph.py` | DataIntegrationAndAnalysis | 0.011 | — | Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include test_lineage_graph_impact_analysis, test_lineage_graph_integrity. |
| `tests/test_python_dataflow.py` | DataIntegrationAndAnalysis | 0.017 | — | Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include test_python_dataflow_pandas, test_python_dataflow_sqlalchemy. |
| `tests/test_semanticist.py` | DataIntegrationAndAnalysis | 0.030 | — | Inferred purpose: This module manages 4 functions and imports 5 dependencies. Key features likely include mock_llm, test_semantic_analysis_flow. |
| `tests/test_sql_lineage.py` | DataIntegrationAndAnalysis | 0.010 | — | Inferred purpose: This module manages 4 functions and imports 2 dependencies. Key features likely include test_sql_lineage_dbt_ref, test_sql_lineage_dbt_source. |
| `tests/test_surveyor.py` | DataIntegrationAndAnalysis | 0.025 | — | Inferred purpose: This module manages 2 functions and imports 4 dependencies. Key features likely include test_surveyor_negative_dead_code, test_surveyor_phase1_5_features. |
| `tests/verify_recon.py` | DataIntegrationAndAnalysis | 0.034 | — | Inferred purpose: This module manages 1 functions and imports 7 dependencies. Key features likely include verify_recon_generation. |
| `src/agents/archivist.py` | DataScienceTools | 0.011 | — | Inferred purpose: This module manages 4 functions and imports 6 dependencies. Key features likely include __init__, apply_overrides. |
| `src/agents/semanticist.py` | DataScienceTools | 0.036 | — | Inferred purpose: This module manages 5 functions and imports 7 dependencies. Key features likely include __init__, analyze_modules. |
| `src/analyzers/python_dataflow_analyzer.py` | DataScienceTools | 0.016 | — | Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, _generate_logic_hash. |
| `src/analyzers/sql_lineage.py` | DataScienceTools | 0.011 | — | Inferred purpose: This module manages 8 functions and imports 10 dependencies. Key features likely include __init__, _generate_logic_hash. |
| `src/utils/git_utils.py` | DataScienceTools | 0.010 | — | Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include __init__, _run_git_cmd. |
| `src/utils/identity_resolver.py` | DataScienceTools | 0.010 | — | Inferred purpose: This module manages 6 functions and imports 4 dependencies. Key features likely include __init__, resolve. |
| `src/utils/llm_client.py` | DataScienceTools | 0.010 | — | Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, can_afford_batch. |
| `src/utils/trace_logger.py` | DataScienceTools | 0.010 | — | Inferred purpose: This module manages 3 functions and imports 5 dependencies. Key features likely include __init__, log_event. |
| `.env` | ProjectConfigurationTools | 0.010 | — | Stores environment variables for the project. |
| `.env.example` | ProjectConfigurationTools | 0.010 | — | Serves as an example configuration file for .env. |
| `.gitignore` | ProjectConfigurationTools | 0.000 | — | Defines files and directories to ignore during version control operations. |
| `.pytest_cache/v/cache/lastfailed` | ProjectConfigurationTools | 0.010 | — | Stores information about failed tests in the pytest cache. |
| `.pytest_cache/v/cache/nodeids` | ProjectConfigurationTools | 0.010 | — | Keeps track of test node IDs for pytest caching and reporting. |
| `FINAL_REPORT.md` | ProjectInsight | 0.000 | — | Contains the final report generated by a testing or deployment process. |
| `README.md` | ProjectInsight | 0.000 | — | Provides an overview and instructions for using the project's files and directories. |
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
| `fix_pagerank.py` | Logic | Low | Produced but never consumed. |
| `mock_project/dag.py` | Logic | Low | Produced but never consumed. |
| `src/cli.py` | Coupling | High | Major architectural hub; critical for blast radius. |
| `src/graph/graph_builder.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/graph/knowledge_graph.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/orchestrator.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/orchestrator.py` | Coupling | High | Major architectural hub; critical for blast radius. |
| `src/server.py` | Logic | Low | Produced but never consumed. |
| `src/utils/canonicalization_service.py` | Logic | Low | Produced but never consumed. |
| `uv.lock` | Logic | Low | Produced but never consumed. |
| `mock_project/process_orders.py` | Logic | Low | Produced but never consumed. |
| `pyproject.toml` | Logic | Low | Produced but never consumed. |
| `src/agents/__init__.py` | Logic | Low | Produced but never consumed. |
| `src/agents/hydrologist.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/agents/hydrologist.py` | Coupling | High | Major architectural hub; critical for blast radius. |
| `src/agents/navigator.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/analyzers/__init__.py` | Logic | Low | Produced but never consumed. |
| `src/analyzers/dag_parsers/__init__.py` | Logic | Low | Produced but never consumed. |
| `src/codebase_cartographer.egg-info/PKG-INFO` | Logic | Low | Produced but never consumed. |
| `src/graph/__init__.py` | Logic | Low | Produced but never consumed. |
| `src/utils/__init__.py` | Logic | Low | Produced but never consumed. |
| `ui/app.js` | Logic | Low | Produced but never consumed. |
| `ui/index.html` | Logic | Low | Produced but never consumed. |
| `ui/style.css` | Logic | Low | Produced but never consumed. |
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
| `src/agents/archivist.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/agents/semanticist.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/analyzers/python_dataflow_analyzer.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/analyzers/sql_lineage.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/utils/git_utils.py` | Complexity | Medium | High cyclomatic complexity. |
| `src/utils/llm_client.py` | Complexity | Medium | High cyclomatic complexity. |
| `.env` | Logic | Low | Produced but never consumed. |
| `.env.example` | Logic | Low | Produced but never consumed. |
| `.pytest_cache/v/cache/lastfailed` | Logic | Low | Produced but never consumed. |
| `.pytest_cache/v/cache/nodeids` | Logic | Low | Produced but never consumed. |
| `src/agents/surveyor.py` | Complexity | Medium | High cyclomatic complexity. |
| `.pytest_cache/CACHEDIR.TAG` | Logic | Low | Produced but never consumed. |

## 🏷️ Module Purpose Index (by Domain)
### CodeBaseOrchestrator
- **`.pytest_cache/README.md`**: Provides documentation and guidelines for using the pytest cache directory structure.
- **`fix_pagerank.py`**: The module 'fix_pagerank.py' is likely used to fix or improve the PageRank algorithm, possibly by handling data preprocessing or fixing issues in existing pagerank calculations.
- **`mock_project/dag.py`**: The module 'dag.py' is part of a DAG (Directed Acyclic Graph) structure, which suggests it might be used for orchestrating tasks or workflows within an Airflow environment.
- **`mock_project/models/schema.yml`**: The 'schema.yml' file likely defines the schema for data models, specifying how data should be structured and stored in the database or other storage systems.
- **`src/cli.py`**: This module provides command-line interface functionalities for orchestrating and managing various codebase operations such as analysis, lineage tracking, impact assessment, and serving API endpoints.
- **`src/graph/graph_builder.py`**: This module builds a graph representation of the codebase structure by adding modules and computing intelligence based on their relationships and dependencies.
- **`src/graph/knowledge_graph.py`**: This module manages the creation and manipulation of a knowledge graph representing data lineage, including adding nodes for different types of entities (data nodes, transformation nodes, module nodes) and edges between them.
- **`src/models/lineage.py`**: This module defines classes representing various components in the data lineage graph such as dataset roles, column references, data nodes, transformation nodes, and lineage edges, which are essential for tracking how data flows through different stages of processing.
- **`src/orchestrator.py`**: This module orchestrates the analysis process by managing tasks such as loading and saving cache, computing hashes, propagating domains, running analyses, and generating reports, ensuring that data lineage information is accurately tracked throughout a repository.
- **`src/server.py`**: This module provides the backend for a web UI server that serves REST APIs to interact with the codebase analysis and management functionalities, including cloning repositories, analyzing them, and providing metadata.
- **`src/utils/canonicalization_service.py`**: This module handles the normalization and canonicalization of paths to ensure consistency in how files are referenced within a codebase, which is crucial for accurate data lineage tracking.
- **`src/utils/clustering.py`**: This module clusters different parts of the codebase into domains based on their similarity and dependencies, aiding in understanding how various components interact within a repository.
- **`src/utils/git_provider.py`**: This module provides utilities for interacting with Git repositories to fetch metadata such as file metrics, current SHA, and changed files, which is essential for tracking changes in the codebase over time.
- **`uv.lock`**: The module 'uv.lock' does not contain any functions, classes, constants or imports that provide a clear business purpose based on the provided code implementation.

### CodeInsight
- **`mock_project/process_orders.py`**: Unknown purpose (Fallback enabled)
- **`pyproject.toml`**: Configuration file: Defines project settings, dependencies, or environment-specific parameters.
- **`src/agents/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/agents/hydrologist.py`**: Analyzes and provides dynamic confidence for hydrological data processing pipelines.
- **`src/agents/navigator.py`**: Provides tools to query the codebase knowledge graph using natural language or structured queries, tracing lineage and dependencies.
- **`src/analyzers/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/analyzers/dag_parsers/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/analyzers/tree_sitter_analyzer.py`**: This module analyzes code written in different languages (Python, JavaScript, YAML, SQL) using the Tree-Sitter parser.
- **`src/codebase_cartographer.egg-info/PKG-INFO`**: Unknown purpose (Fallback enabled)
- **`src/graph/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/models/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/utils/__init__.py`**: Package initialization: Defines the module structure and exposes public interfaces for this directory.
- **`src/utils/semantic_index.py`**: Estimated purpose: Semantic Index — Persistent vector store for module purpose statements.

Stores embeddings as a flat JSON file in semantic_index/ directory.
Provides fast cosine-similarity search without requiring an external vector DB.

Used by:
  - NavigatorTools.find_implementation() (runtime lookup)
  - Orchestrator (build/update on each analysis run)
- **`ui/app.js`**: Unknown purpose (Fallback enabled)
- **`ui/index.html`**: Unknown purpose (Fallback enabled)
- **`ui/style.css`**: Unknown purpose (Fallback enabled)

### DataIntegrationAndAnalysis
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

### DataScienceTools
- **`src/agents/archivist.py`**: Inferred purpose: This module manages 4 functions and imports 6 dependencies. Key features likely include __init__, apply_overrides.
- **`src/agents/semanticist.py`**: Inferred purpose: This module manages 5 functions and imports 7 dependencies. Key features likely include __init__, analyze_modules.
- **`src/analyzers/python_dataflow_analyzer.py`**: Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, _generate_logic_hash.
- **`src/analyzers/sql_lineage.py`**: Inferred purpose: This module manages 8 functions and imports 10 dependencies. Key features likely include __init__, _generate_logic_hash.
- **`src/utils/git_utils.py`**: Inferred purpose: This module manages 3 functions and imports 3 dependencies. Key features likely include __init__, _run_git_cmd.
- **`src/utils/identity_resolver.py`**: Inferred purpose: This module manages 6 functions and imports 4 dependencies. Key features likely include __init__, resolve.
- **`src/utils/llm_client.py`**: Inferred purpose: This module manages 8 functions and imports 7 dependencies. Key features likely include __init__, can_afford_batch.
- **`src/utils/trace_logger.py`**: Inferred purpose: This module manages 3 functions and imports 5 dependencies. Key features likely include __init__, log_event.

### ProjectConfigurationTools
- **`.env`**: Stores environment variables for the project.
- **`.env.example`**: Serves as an example configuration file for .env.
- **`.gitignore`**: Defines files and directories to ignore during version control operations.
- **`.pytest_cache/v/cache/lastfailed`**: Stores information about failed tests in the pytest cache.
- **`.pytest_cache/v/cache/nodeids`**: Keeps track of test node IDs for pytest caching and reporting.

### ProjectInsight
- **`FINAL_REPORT.md`**: Contains the final report generated by a testing or deployment process.
- **`README.md`**: Provides an overview and instructions for using the project's files and directories.
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
