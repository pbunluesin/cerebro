# Data Flow

## Purpose

Document how data moves through the system.

## Flow Diagram

```text
[Source System]
      |
      v
[Extract / API / Query]
      |
      v
[Staging / Validation]
      |
      v
[Transform / Mapping]
      |
      v
[Target System]
      |
      v
[Monitoring / Logs / Alerts]
```

## Data Sources

| Source | Type | Notes |
|---|---|---|
| [Source name] | [DB/API/File] | [Notes] |

## Data Targets

| Target | Type | Notes |
|---|---|---|
| [Target name] | [DB/API/File] | [Notes] |

## Validation Rules

- [Rule]
- [Rule]

## Failure Handling

| Failure | Expected Behavior |
|---|---|
| API timeout | Retry with backoff |
| Invalid payload | Log and stop batch |
| Duplicate data | Follow documented merge/upsert rule |
