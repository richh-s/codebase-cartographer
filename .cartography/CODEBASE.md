# 🗺️ Codebase Technical Overview
**Commit SHA:** `f445ffe6c0bdc814d316ed42494ffac807b5fc5a`
**Generated:** 2026-03-15T05:00:10.505383
**Total Modules:** 71

## 📂 Module Inventory
| Module | Domain | Layer | Rank | Status | Sync | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `.env` | General | unknown | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `.env.example` | General | unknown | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `.gitignore` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `.pytest_cache/.gitignore` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `.pytest_cache/CACHEDIR.TAG` | General | unknown | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `.pytest_cache/README.md` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `.pytest_cache/v/cache/lastfailed` | General | unknown | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `.pytest_cache/v/cache/nodeids` | General | unknown | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `FINAL_REPORT.md` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `README.md` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `RECONNAISSANCE.md` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `fix_pagerank.py` | General | core | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `mock_project/dag.py` | General | core | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `mock_project/models/schema.yml` | General | tooling | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `mock_project/models/stg_orders.sql` | General | model | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `mock_project/process_orders.py` | General | core | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `pyproject.toml` | General | tooling | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `semantic_index/index.json` | General | meta | 0.000 | ⚠️ Potentially Stale | — | No purpose statement generated. |
| `src/agents/__init__.py` | General | agent | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/agents/archivist.py` | General | agent | 0.011 | ⚠️ Potentially Stale | — | No purpose statement generated. |
| `src/agents/hydrologist.py` | General | agent | 0.066 | ✅ Stable | — | No purpose statement generated. |
| `src/agents/navigator.py` | General | agent | 0.016 | ✅ Stable | — | No purpose statement generated. |
| `src/agents/semanticist.py` | General | agent | 0.036 | ⚠️ Potentially Stale | — | No purpose statement generated. |
| `src/agents/surveyor.py` | General | agent | 0.035 | ⚠️ Potentially Stale | — | No purpose statement generated. |
| `src/analyzers/__init__.py` | General | analyzer | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/analyzers/dag_config_parser.py` | General | analyzer | 0.011 | ✅ Stable | — | No purpose statement generated. |
| `src/analyzers/dag_parsers/__init__.py` | General | analyzer | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/analyzers/dag_parsers/plugins.py` | General | analyzer | 0.011 | ✅ Stable | — | No purpose statement generated. |
| `src/analyzers/python_dataflow_analyzer.py` | General | analyzer | 0.016 | ✅ Stable | — | No purpose statement generated. |
| `src/analyzers/sql_lineage.py` | General | analyzer | 0.011 | ✅ Stable | — | No purpose statement generated. |
| `src/analyzers/tree_sitter_analyzer.py` | General | analyzer | 0.011 | ✅ Stable | — | No purpose statement generated. |
| `src/cli.py` | General | core | 0.066 | ✅ Stable | — | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/PKG-INFO` | General | core | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/SOURCES.txt` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/dependency_links.txt` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/entry_points.txt` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/requires.txt` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `src/codebase_cartographer.egg-info/top_level.txt` | General | meta | 0.000 | ✅ Stable | — | No purpose statement generated. |
| `src/graph/__init__.py` | General | graph | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/graph/graph_builder.py` | General | graph | 0.011 | ✅ Stable | — | No purpose statement generated. |
| `src/graph/knowledge_graph.py` | General | graph | 0.011 | ✅ Stable | — | No purpose statement generated. |
| `src/models/__init__.py` | General | model | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/models/lineage.py` | General | model | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/models/nodes.py` | General | model | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/orchestrator.py` | General | core | 0.099 | ⚠️ Potentially Stale | — | No purpose statement generated. |
| `src/server.py` | General | core | 0.038 | ⚠️ Potentially Stale | — | No purpose statement generated. |
| `src/utils/__init__.py` | General | utility | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/canonicalization_service.py` | General | utility | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/clustering.py` | General | utility | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/git_provider.py` | General | utility | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/git_utils.py` | General | utility | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/identity_resolver.py` | General | utility | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/llm_client.py` | General | utility | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/module_summary.py` | General | utility | 0.011 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/semantic_index.py` | General | utility | 0.013 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/similarity.py` | General | utility | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `src/utils/trace_logger.py` | General | utility | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `test_parse.py` | General | core | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `test_pr.py` | General | core | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `test_scope.py` | General | core | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `tests/test_archivist_excellence.py` | General | test | 0.040 | ✅ Stable | — | No purpose statement generated. |
| `tests/test_lineage_graph.py` | General | test | 0.011 | ✅ Stable | — | No purpose statement generated. |
| `tests/test_python_dataflow.py` | General | test | 0.017 | ✅ Stable | — | No purpose statement generated. |
| `tests/test_semanticist.py` | General | test | 0.030 | ✅ Stable | — | No purpose statement generated. |
| `tests/test_sql_lineage.py` | General | test | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `tests/test_surveyor.py` | General | test | 0.025 | ✅ Stable | — | No purpose statement generated. |
| `tests/verify_recon.py` | General | test | 0.034 | ✅ Stable | — | No purpose statement generated. |
| `ui/app.js` | General | unknown | 0.010 | ⚠️ Potentially Stale | — | No purpose statement generated. |
| `ui/index.html` | General | unknown | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `ui/style.css` | General | unknown | 0.010 | ✅ Stable | — | No purpose statement generated. |
| `uv.lock` | General | unknown | 0.010 | ✅ Stable | — | No purpose statement generated. |

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
| `src/agents/hydrologist.py` | Coupling | Low | Significant architectural hub; changes may have high blast radius. |
| `src/agents/navigator.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/agents/semanticist.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/agents/surveyor.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/analyzers/__init__.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/analyzers/dag_parsers/__init__.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/analyzers/python_dataflow_analyzer.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/analyzers/sql_lineage.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/cli.py` | Coupling | Low | Significant architectural hub; changes may have high blast radius. |
| `src/codebase_cartographer.egg-info/PKG-INFO` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/graph/__init__.py` | Logic | Low | Potential dead code (produced but never consumed). |
| `src/graph/graph_builder.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/graph/knowledge_graph.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/orchestrator.py` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |
| `src/orchestrator.py` | Coupling | Low | Significant architectural hub; changes may have high blast radius. |
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

## 🔄 Circular Dependencies
✅ No circular dependencies detected.