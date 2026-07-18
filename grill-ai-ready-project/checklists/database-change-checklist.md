# Database Change Checklist

Use before changing schema, stored procedures, migrations, ETL/ELT, sync jobs, or data ownership rules.

- [ ] Source of truth confirmed
- [ ] Primary/unique keys confirmed
- [ ] Nullability and duplicate behavior confirmed
- [ ] Existing consumers checked
- [ ] Backward compatibility reviewed
- [ ] Migration/backfill plan documented
- [ ] Rollback plan documented
- [ ] Data validation query/check defined
- [ ] Performance impact reviewed
- [ ] `docs/DATA_MODEL.md` updated
- [ ] `docs/PROJECT_STATE.md` updated
