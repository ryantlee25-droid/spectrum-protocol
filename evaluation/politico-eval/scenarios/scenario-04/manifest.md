# Manifest: etl-pipeline-0331

**Rain ID**: etl-pipeline-0331
**Mode**: full
**Base Branch**: main
**Base Commit**: 7b1e9c4

## Task List

| Howler | Scope | Effort | Serial Risk |
|--------|-------|--------|-------------|
| howler-extract | Implement data extraction from S3 CSV files, pagination over large datasets, and raw record buffering | M | no |
| howler-schema | Define Pydantic models for raw and validated records, write Alembic migration for the target PostgreSQL table | M | no |
| howler-validate | Apply business validation rules to extracted records: type coercion, null checks, domain constraints | M | no |
| howler-transform | Apply field mappings, compute derived fields, and produce normalized records ready for loading | M | no |
| howler-load | Batch-insert normalized records into PostgreSQL, handle conflicts, write audit log | L | no |

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `etl/extract/s3_reader.py` | howler-extract | CREATES |
| `etl/extract/paginator.py` | howler-extract | CREATES |
| `etl/extract/buffer.py` | howler-extract | CREATES |
| `etl/models/raw_record.py` | howler-schema | CREATES |
| `etl/models/validated_record.py` | howler-schema | CREATES |
| `etl/models/normalized_record.py` | howler-schema | CREATES |
| `etl/validate/rules.py` | howler-validate | CREATES |
| `etl/validate/coercion.py` | howler-validate | CREATES |
| `etl/validate/runner.py` | howler-validate | CREATES |
| `etl/transform/mappings.py` | howler-transform | CREATES |
| `etl/transform/derived.py` | howler-transform | CREATES |
| `etl/transform/runner.py` | howler-transform | CREATES |
| `etl/load/inserter.py` | howler-load | CREATES |
| `etl/load/conflict_handler.py` | howler-load | CREATES |
| `etl/load/audit.py` | howler-load | CREATES |
| `config/pipeline.yaml` | howler-extract | CREATES |

**CONFLICTS**: none (verified — no file appears in more than one Howler's ownership)

## Dependency Graph (DAG)

```yaml
- id: howler-schema
  deps: []
  branch: spectrum/etl-pipeline-0331/howler-schema
  base_branch: main
  base_commit: 7b1e9c4

- id: howler-extract
  deps: [howler-schema#types]
  branch: spectrum/etl-pipeline-0331/howler-extract
  base_branch: main
  base_commit: 7b1e9c4

- id: howler-validate
  deps: [howler-schema#types]
  branch: spectrum/etl-pipeline-0331/howler-validate
  base_branch: main
  base_commit: 7b1e9c4

- id: howler-transform
  deps: [howler-schema#types]
  branch: spectrum/etl-pipeline-0331/howler-transform
  base_branch: main
  base_commit: 7b1e9c4

- id: howler-load
  deps: [howler-schema#types, howler-transform]
  branch: spectrum/etl-pipeline-0331/howler-load
  base_branch: main
  base_commit: 7b1e9c4
```

## Decomposition Rationale

I chose 5 Howlers because extract, validate, transform, and load are the classic ETL stages with clear data contracts at each boundary. howler-schema provides the Pydantic models and database schema that all other Howlers depend on; it runs first with no deps. howler-extract, howler-validate, and howler-transform are all parallel after schema's #types checkpoint — they operate on different stages of the pipeline and don't share files. howler-load depends on howler-transform (full completion) because it needs the NormalizedRecord model to be finalized before building insert logic. Alternative: merging validate+transform — rejected because validation rules and field mapping are independent policy concerns maintained by different teams.

## Politico Review

_Not yet conducted — pre-freeze review scheduled._
