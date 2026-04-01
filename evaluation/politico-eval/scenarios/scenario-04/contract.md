# Contract: etl-pipeline-0331

**Frozen at**: 2026-03-31T11:00:00Z
**Status**: FROZEN — do not modify. File AMENDMENT.md if changes are needed.

---

## Shared Types

All Howlers importing shared models MUST use the paths defined here. Do not re-declare these Pydantic models.

### RawRecord (source: howler-schema)
```python
# etl/models/raw_record.py
from pydantic import BaseModel
from typing import Optional

class RawRecord(BaseModel):
    source_id: str
    source_file: str
    row_index: int
    raw_fields: dict[str, str]   # All values are strings at extraction time
```

### ValidatedRecord (source: howler-schema)
```python
# etl/models/validated_record.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

class ValidatedRecord(BaseModel):
    source_id: str
    account_id: str
    event_type: str
    event_date: date
    amount: float
    currency: str
    metadata: object              # Flexible bag for non-standard fields
    validation_errors: list[str]  # Non-empty means soft-failed (still passes through)
```

### NormalizedRecord (source: howler-schema)
```python
# etl/models/normalized_record.py
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class NormalizedRecord(BaseModel):
    id: str                  # UUID, generated during transform
    account_id: str
    event_type: str
    event_date: date
    amount_cents: int        # Always in cents; currency conversion applied during transform
    currency_code: str       # ISO 4217
    metadata: dict[str, str] # Normalized to string values only
    pipeline_run_id: str
```

---

## Naming Conventions

- **Module structure**: `etl/{stage}/{module}.py` — stages are `extract`, `validate`, `transform`, `load`, `models`
- **Runner pattern**: each stage exposes a `runner.py` with a `run(records: list[...]) -> list[...]` function
- **Pydantic models**: PascalCase class names, snake_case fields
- **Config**: `config/pipeline.yaml` owns global pipeline configuration (owned by howler-extract)
- **Database**: SQLAlchemy + Alembic; connection string from `DATABASE_URL` environment variable
- **Tests**: `pytest` in `tests/` directory; one test file per stage (`tests/test_validate.py`, etc.)

---

## Integration Points

| From | To | Interface | Where |
|------|----|-----------|-------|
| howler-schema | howler-extract | `RawRecord` model | extract creates RawRecord instances from CSV rows |
| howler-schema | howler-validate | `RawRecord` → `ValidatedRecord` | validate transforms RawRecord into ValidatedRecord |
| howler-schema | howler-transform | `ValidatedRecord` → `NormalizedRecord` | transform maps ValidatedRecord fields to NormalizedRecord |
| howler-schema | howler-load | `NormalizedRecord` model | load inserts NormalizedRecord into PostgreSQL |
| howler-transform | howler-load | `run()` output format | load receives list of NormalizedRecord from transform runner |
| howler-extract | (pipeline orchestrator) | `RawRecord` buffer | orchestrator is out of scope; Howlers implement stages only |

---

## Design-by-Contract: howler-schema

### Preconditions
- `pydantic`, `sqlalchemy`, `alembic` in `requirements.txt`
- PostgreSQL available at `DATABASE_URL`

### Postconditions
- `etl/models/raw_record.py` exports `RawRecord` matching the contract definition
- `etl/models/validated_record.py` exports `ValidatedRecord` matching the contract definition
- `etl/models/normalized_record.py` exports `NormalizedRecord` matching the contract definition
- Alembic migration creates a `pipeline_records` table with columns matching `NormalizedRecord` fields
- Migration file follows naming convention: `{revision}_initial_pipeline_schema.py`

### Invariants
- Pydantic models are immutable (`model_config = ConfigDict(frozen=True)`)
- No business logic in model files — models are pure data shapes

---

## Design-by-Contract: howler-extract

### Preconditions
- `howler-schema#types` checkpoint is STABLE (RawRecord finalized)
- AWS credentials available via environment (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- `boto3` in `requirements.txt`

### Postconditions
- `etl/extract/s3_reader.py` exports `read_csv_from_s3(bucket: str, key: str) -> Iterator[dict[str, str]]`
- `etl/extract/paginator.py` exports `paginate(iterator, page_size: int) -> Iterator[list[dict]]`
- `etl/extract/buffer.py` exports `to_raw_records(rows: list[dict], source_file: str) -> list[RawRecord]`
- `config/pipeline.yaml` defines: `s3_bucket`, `s3_prefix`, `page_size` (default: 1000), `max_retries`

### Invariants
- Extraction is read-only — never writes to S3
- `to_raw_records` assigns sequential `row_index` starting from 0

---

## Design-by-Contract: howler-validate

### Preconditions
- `howler-schema#types` checkpoint is STABLE (RawRecord and ValidatedRecord finalized)

### Postconditions
- `etl/validate/rules.py` exports `VALIDATION_RULES: list[Callable[[RawRecord], list[str]]]`
- `etl/validate/coercion.py` exports type coercion functions: `to_date()`, `to_float()`, `to_currency_code()`
- `etl/validate/runner.py` exports `run(records: list[RawRecord]) -> list[ValidatedRecord]`
- Records with validation errors are NOT dropped — they pass through with `validation_errors` populated

### Invariants
- `run()` is a pure function — no side effects, no database or network calls
- Output list length equals input list length (no records dropped by validation)

---

## Design-by-Contract: howler-transform

### Preconditions
- `howler-schema#types` checkpoint is STABLE (ValidatedRecord and NormalizedRecord finalized)

### Postconditions
- `etl/transform/mappings.py` exports `FIELD_MAPPINGS: dict[str, str]` (raw field name → normalized field name)
- `etl/transform/derived.py` exports `compute_amount_cents(amount: float, currency: str) -> int`
- `etl/transform/runner.py` exports `run(records: list[ValidatedRecord], pipeline_run_id: str) -> list[NormalizedRecord]`
- Records with non-empty `validation_errors` are logged and excluded from transform output

### Invariants
- `run()` is a pure function — no side effects
- `compute_amount_cents` uses banker's rounding (Python `Decimal` with `ROUND_HALF_EVEN`)
- All `metadata` values coerced to `str` before output (NormalizedRecord invariant)

---

## Design-by-Contract: howler-load

### Preconditions
- `howler-schema#types` checkpoint is STABLE (NormalizedRecord finalized)
- `howler-transform` is fully complete (not just #types — full NormalizedRecord output format confirmed)
- PostgreSQL available at `DATABASE_URL`
- `sqlalchemy` in `requirements.txt`

### Postconditions
- `etl/load/inserter.py` exports `batch_insert(records: list[NormalizedRecord], session: Session) -> int` (returns inserted count)
- `etl/load/conflict_handler.py` exports `on_conflict_do_update` strategy for upsert by `id`
- `etl/load/audit.py` exports `write_audit_log(pipeline_run_id: str, inserted: int, errors: int) -> None`

### Invariants
- Inserts are batched (default batch size: 500 records)
- Conflicts on `id` are resolved by updating all non-key fields (upsert semantics)
- Audit log is written regardless of insert success or failure
