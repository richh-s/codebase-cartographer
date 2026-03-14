# 🗺️ Codebase Technical Overview
**Commit SHA:** `de811aded186e04e56e9d55553a675842db6a8ac`
**Generated:** 2026-03-14T11:46:22.297096
**Total Modules:** 71

## 📂 Module Inventory
| Module | Domain | Layer | Status | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `.env` | General | unknown | ✅ Stable | No purpose statement generated. |
| `.env.example` | General | unknown | ✅ Stable | No purpose statement generated. |
| `.gitignore` | General | meta | ✅ Stable | No purpose statement generated. |
| `.pytest_cache/.gitignore` | General | meta | ✅ Stable | No purpose statement generated. |
| `.pytest_cache/CACHEDIR.TAG` | General | unknown | ✅ Stable | No purpose statement generated. |
| `.pytest_cache/README.md` | General | meta | ✅ Stable | No purpose statement generated. |
| `.pytest_cache/v/cache/lastfailed` | General | unknown | ✅ Stable | No purpose statement generated. |
| `.pytest_cache/v/cache/nodeids` | General | unknown | ✅ Stable | No purpose statement generated. |
| `INTERIM_REPORT.md` | General | meta | ✅ Stable | No purpose statement generated. |
| `README.md` | General | meta | ✅ Stable | No purpose statement generated. |
| `RECONNAISSANCE.md` | General | meta | ✅ Stable | No purpose statement generated. |
| `fix_pagerank.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `mock_project/dag.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `mock_project/models/schema.yml` | General | meta | ✅ Stable | No purpose statement generated. |
| `mock_project/models/stg_orders.sql` | General | unknown | ✅ Stable | No purpose statement generated. |
| `mock_project/process_orders.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `pyproject.toml` | General | unknown | ✅ Stable | No purpose statement generated. |
| `semantic_index/index.json` | General | meta | ✅ Stable | No purpose statement generated. |
| `src/agents/__init__.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/agents/archivist.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/agents/hydrologist.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/agents/navigator.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/agents/semanticist.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/agents/surveyor.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/analyzers/__init__.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/analyzers/dag_config_parser.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/analyzers/dag_parsers/__init__.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/analyzers/dag_parsers/plugins.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/analyzers/python_dataflow_analyzer.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/analyzers/sql_lineage.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/analyzers/tree_sitter_analyzer.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/cli.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/PKG-INFO` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/SOURCES.txt` | General | meta | ✅ Stable | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/dependency_links.txt` | General | meta | ✅ Stable | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/entry_points.txt` | General | meta | ✅ Stable | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/requires.txt` | General | meta | ✅ Stable | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/top_level.txt` | General | meta | ✅ Stable | No purpose statement generated. |
| `src/graph/__init__.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/graph/graph_builder.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/graph/knowledge_graph.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/models/__init__.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/models/lineage.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/models/nodes.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/orchestrator.py` | General | unknown | ⚠️ Potentially Stale | No purpose statement generated. |
| `src/server.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/__init__.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/canonicalization_service.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/clustering.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/git_provider.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/git_utils.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/identity_resolver.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/llm_client.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/module_summary.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/semantic_index.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/similarity.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `src/utils/trace_logger.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `test_parse.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `test_pr.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `test_scope.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `tests/test_archivist_excellence.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `tests/test_lineage_graph.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `tests/test_python_dataflow.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `tests/test_semanticist.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `tests/test_sql_lineage.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `tests/test_surveyor.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `tests/verify_recon.py` | General | unknown | ✅ Stable | No purpose statement generated. |
| `ui/app.js` | General | unknown | ✅ Stable | No purpose statement generated. |
| `ui/index.html` | General | unknown | ✅ Stable | No purpose statement generated. |
| `ui/style.css` | General | unknown | ✅ Stable | No purpose statement generated. |
| `uv.lock` | General | unknown | ✅ Stable | No purpose statement generated. |

## 🚩 Technical Debt & Risks
| Area | Debt Type | Severity | Description |
| :--- | :--- | :--- | :--- |
| `.env` | Logic | Low | Potential dead code (produced but never consumed). |
| `.env.example` | Logic | Low | Potential dead code (produced but never consumed). |
| `.pytest_cache/CACHEDIR.TAG` | Logic | Low | Potential dead code (produced but never consumed). |
| `.pytest_cache/v/cache/lastfailed` | Logic | Low | Potential dead code (produced but never consumed). |
| `.pytest_cache/v/cache/nodeids` | Logic | Low | Potential dead code (produced but never consumed). |
| `fix_pagerank.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `mock_project/dag.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `mock_project/process_orders.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `pyproject.toml` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/agents/__init__.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/agents/archivist.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/agents/hydrologist.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/agents/navigator.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/agents/semanticist.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/agents/surveyor.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/analyzers/__init__.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/analyzers/dag_parsers/__init__.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/analyzers/python_dataflow_analyzer.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/analyzers/sql_lineage.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/cli.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/codebase_cartographer.egg-info/PKG-INFO` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/graph/__init__.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/graph/graph_builder.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/graph/knowledge_graph.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/orchestrator.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/server.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/utils/__init__.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/utils/canonicalization_service.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/utils/git_utils.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/utils/llm_client.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `test_parse.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `test_pr.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `test_scope.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `tests/test_archivist_excellence.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `tests/test_lineage_graph.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `tests/test_python_dataflow.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `tests/test_semanticist.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `tests/test_sql_lineage.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `tests/test_surveyor.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `tests/verify_recon.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `ui/app.js` | Logic | Low | Potential dead code (produced but never consumed). |
| `ui/index.html` | Logic | Low | Potential dead code (produced but never consumed). |
| `ui/style.css` | Logic | Low | Potential dead code (produced but never consumed). |
| `uv.lock` | Logic | Low | Potential dead code (produced but never consumed). |