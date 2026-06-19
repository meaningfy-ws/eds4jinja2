<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Parent: EPIC `in-memory-sparql-datasource` (proposal.md) — derived from DEC-1..DEC-5.

## Context

`eds4jinja2` drives Jinja2 report templates from pluggable data sources. Templates call
builder lambdas registered in `DATA_SOURCE_BUILDERS` (`builders/jinja_builder.py`):

```python
DATA_SOURCE_BUILDERS = {
    "from_endpoint": lambda endpoint: RemoteSPARQLEndpointDataSource(endpoint),
    "from_file":     lambda file_path: FileDataSource(file_path),
    "from_rdf_file": lambda from_rdf_file: RDFFileDataSource(from_rdf_file),
}
```

`build_eds_environment(external_data_source_builders=…, external_filters=…, **kwargs)` already
accepts injected builders and filters. The gap is upstream: `ReportBuilder.__init__`
(`builders/report_builder.py`, line ~103) calls it **without** forwarding any injection:

```python
self.template_env = build_eds_environment(loader=template_loader, **self.template_flavour_syntax_spec)
```

So a consumer cannot redirect `from_endpoint` — the templates' default data-source call — to a
non-remote source. The two local-ish sources today:

- `RemoteSPARQLEndpointDataSource` — needs a live endpoint; tabular = CSV→`pd.read_csv`
  (`DataFrame`), tree = `JSON` via `query.convert()` (SPARQL-JSON `dict`). This is the parity
  reference.
- `RDFFileDataSource` — file-path only, **re-parses the file on every `_fetch_tabular`**
  (`self.__graph__.parse(self.__filename__)`), tabular only, `_fetch_tree` raises
  `UnsupportedRepresentation`.

The `DataSource` ABC (`adapters/base_data_source.py`) defines the fail-safe wrappers
(`fetch_tabular` / `fetch_tree` returning `(result, error)`) and the four abstract methods
(`_can_be_tabular`, `_can_be_tree`, `_fetch_tabular`, `_fetch_tree`).

**Constraints**: layers `entrypoints > builders > adapters` (adapters innermost — import-linter
enforced); Python 3.11/3.12; pip + tox + pyproject; rdflib already a dependency; pyoxigraph is
NOT a dependency and must not become one.

## Goals / Non-Goals

**Goals:**
- Render reports against an in-process RDF graph with **unchanged templates**.
- Provide an in-memory `DataSource` that supports **both** tabular and tree, with shapes
  **identical** to `RemoteSPARQLEndpointDataSource`.
- Work for both `rdflib.Graph` and pyoxigraph-backed consumers via a `query(...)` callable.
- Be fully backward-compatible (empty-default kwargs; additive registration).

**Non-Goals:**
- No SPARQL engine implementation; no query optimisation.
- No template edits, no CLI changes, no new mandatory dependency.
- No file/socket I/O inside the new source (the consumer owns graph loading).
- No change to `RDFFileDataSource` / `RemoteSPARQLEndpointDataSource`.

## Decisions

- **DEC-1 (seam)**: `ReportBuilder.__init__(..., external_data_source_builders: dict = {},
  external_filters: dict = {})`, forwarded as
  `build_eds_environment(loader=…, external_data_source_builders=external_data_source_builders,
  external_filters=external_filters, **syntax)`. *Caveat:* `build_eds_environment`'s defaults
  **replace** the registries (`external_data_source_builders={**DATA_SOURCE_BUILDERS, …}`), so
  forwarding a *partial* dict from `ReportBuilder` would drop the defaults. Therefore
  `ReportBuilder` MUST **merge** the injected dicts over the defaults before forwarding
  (`{**DATA_SOURCE_BUILDERS, **TABULAR_HELPERS, **TREE_HELPERS, **external_data_source_builders}`
  and `{**ADDITIONAL_FILTERS, **external_filters}`). This preserves `invert_dict`,
  `from_file`, the tabular helpers, `escape_latex`, etc., while letting the consumer override
  `from_endpoint`. With empty dicts the merged result equals the current defaults exactly →
  no behaviour change. *(Alternatives: forwarding raw partial dicts — rejected, silently drops
  helper globals; a dedicated builder subclass — rejected, larger surface for no gain.)*
- **DEC-2 (engine-agnostic input)**: constructor accepts `source: rdflib.Graph | Callable`.
  If it has a callable `query` attribute that is an `rdflib.Graph`, use `graph.query`;
  otherwise treat `source` itself as the `query(sparql_text)` callable. Normalisation of the
  result handles both rdflib `Result` objects and pyoxigraph `QuerySolutions`. *(Why: one
  class serves rdflib AND pyoxigraph without importing pyoxigraph.)*
- **DEC-3 (parity)**: tabular returns `pd.DataFrame` of stringified bindings (mirroring
  `RDFFileDataSource`'s reduce-to-string approach, which already matches what templates
  expect); tree returns the SPARQL-JSON dict shape `{"head": {"vars": [...]},
  "results": {"bindings": [{var: {"type": ..., "value": ...}}]}}` mirroring
  `RemoteSPARQLEndpointDataSource._fetch_tree`. *(Why: templates must be source-blind.)*
- **DEC-4 (substitution + chaining)**: provide `with_query(sparql_query, substitution_variables=None,
  prefixes="")` returning `self`, reusing `SubstitutionTemplate` like the other sources, so the
  fluent call style the framework uses elsewhere keeps working.
- **DEC-5 (optional registration)**: add `from_graph` (alias `from_memory`) to
  `DATA_SOURCE_BUILDERS` for explicit template use — additive, does not affect existing keys.

## Algorithm / approach

**A. ReportBuilder seam** (`report_builder.py`):
```python
def __init__(self, target_path, config_file="config.json", output_path=None,
             additional_config={}, external_data_source_builders={}, external_filters={}):
    ...
    data_source_builders = {**DATA_SOURCE_BUILDERS, **TABULAR_HELPERS, **TREE_HELPERS,
                            **external_data_source_builders}
    filters = {**ADDITIONAL_FILTERS, **external_filters}
    self.template_env = build_eds_environment(
        loader=template_loader,
        external_data_source_builders=data_source_builders,
        external_filters=filters,
        **self.template_flavour_syntax_spec)
```
(Import the registries from `jinja_builder`. Empty-default kwargs → merged dicts equal current
defaults → byte-identical behaviour.)

**B. InMemorySPARQLDataSource** (`adapters/in_memory_sparql_ds.py`):
```python
class InMemorySPARQLDataSource(DataSource):
    def __init__(self, source):                 # rdflib.Graph OR query callable
        self.__query_fn = source.query if isinstance(source, rdflib.Graph) else source
        self.__query__ = ""
        self.__can_be_tabular = True
        self.__can_be_tree = True

    def with_query(self, sparql_query, substitution_variables=None, prefixes=""):
        q = SubstitutionTemplate(sparql_query).safe_substitute(substitution_variables) \
            if substitution_variables else sparql_query
        self.__query__ = (prefixes + " " + q).strip()
        return self

    def _fetch_tabular(self):                    # -> pd.DataFrame (string bindings)
        result = self.__query_fn(self.__query__)
        rows = [{str(k): str(v) for k, v in binding.items()} for binding in _iter_bindings(result)]
        return pd.DataFrame(rows)

    def _fetch_tree(self):                        # -> SPARQL-JSON dict
        result = self.__query_fn(self.__query__)
        return _to_sparql_json(result)            # {"head": {"vars": [...]}, "results": {"bindings": [...]}}
```
`_iter_bindings` / `_to_sparql_json` are small normalisers: for an rdflib `Result` they read
`result.vars` and `result.bindings`; for a callable returning an rdflib `Result` the same path
applies; for pyoxigraph-style solutions they iterate variables/values. Term typing for tree:
`URIRef → "uri"`, `Literal → "literal"` (carry `datatype` / `xml:lang` when present),
`BNode → "bnode"`.

**Worked example (consumer, templates unchanged):**
```python
graph = rdflib.Graph().parse("dataset.ttl")            # consumer owns loading
ReportBuilder(
    target_path="report/",
    external_data_source_builders={
        "from_endpoint": lambda _endpoint: InMemorySPARQLDataSource(graph),
    },
).make_document()
# template still calls {{ from_endpoint(conf.default_endpoint) }} — now served in-memory
```
pyoxigraph variant: pass `lambda _e: InMemorySPARQLDataSource(store.query)`.

### Anti-patterns
- ❌ Forwarding partial builder dicts straight into `build_eds_environment` (drops the default
  helpers/globals — always merge over the defaults).
- ❌ Importing `pyoxigraph` anywhere in `eds4jinja2`.
- ❌ Reading files or opening connections inside `InMemorySPARQLDataSource`.
- ❌ Re-parsing a graph per query (the `RDFFileDataSource` smell we are explicitly avoiding).
- ❌ Returning a tree shape that differs from `RemoteSPARQLEndpointDataSource` (breaks
  source-blindness of templates).
- ❌ Free strings for SPARQL-JSON keys / term types scattered inline — define them as module
  constants (`HEAD`, `VARS`, `RESULTS`, `BINDINGS`, `TYPE`, `VALUE`, `URI`, `LITERAL`, `BNODE`).
- ❌ Mutating `DATA_SOURCE_BUILDERS` defaults at call time.

## Error matrix

| Failure mode | Expected handling |
|---|---|
| `with_query` never called / empty query | `_fetch_*` raises `Exception("The query is empty.")`; `fetch_*` wrapper returns `(None, error)` |
| `source` is neither `rdflib.Graph` nor callable | `TypeError` at construction (fail fast, clear message) |
| Query callable raises (bad SPARQL, engine error) | propagates to `_fetch_*`; `fetch_*` wrapper catches → `(None, str(e))` (same fail-safe contract as siblings) |
| ASK / boolean result requested as tabular | normaliser yields a single-column/empty DataFrame; documented limitation, no crash |
| Unknown RDF term type in tree | fall back to `"literal"` with stringified value (no crash); refine later (Open Questions) |
| Empty result set | tabular → empty `DataFrame`; tree → `{"head": {"vars": [...]}, "results": {"bindings": []}}` |

## Risks / Trade-offs

- **[Result-shape drift between in-memory and remote]** → Mitigation: parity tests assert the
  tree dict structure and the tabular column/row stringification against the documented
  SPARQL-JSON shape; the `RemoteSPARQLEndpointDataSource` doctest/behaviour is the reference.
- **[`build_eds_environment` replace-not-merge default]** → Mitigation: DEC-1 merges over the
  defaults in `ReportBuilder`; a regression test asserts default globals (`from_file`,
  `invert_dict`, `escape_latex`) still present after injecting only `from_endpoint`.
- **[pyoxigraph result-object variance]** → Mitigation: the normaliser is the only
  engine-aware seam and is covered by callable-input tests; rdflib path is covered separately.
- **[Backward-compat regression]** → Mitigation: an explicit test constructs `ReportBuilder`
  with no new kwargs and asserts the environment globals equal the pre-change set.

## Open Questions

- Exact SPARQL-JSON fidelity for typed literals from rdflib vs pyoxigraph (datatype IRI vs
  prefixed form) — first pass carries the raw datatype string; revisit if a consumer needs
  canonical typing. *(Parked: low risk for dqgen tabular-first templates.)*
- Whether to keep `from_memory` as an alias of `from_graph` (kept, for support)
  — defaulting to alias; reconsider if a template needs a distinct semantics.
