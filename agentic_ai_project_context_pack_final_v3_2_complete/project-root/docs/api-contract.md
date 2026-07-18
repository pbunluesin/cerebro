# API Contract

## Purpose

Document API endpoints, request/response contracts, authentication, and error behavior.

## Authentication

- Method: [API Key / OAuth / JWT / Basic / Other]
- Header: `[Header name]`
- Token storage: [Where/how]
- Rotation policy: [Policy]

## Endpoints

### `POST /example`

#### Request

```json
{
  "example": "value"
}
```

#### Response

```json
{
  "success": true
}
```

#### Error Response

```json
{
  "error": "message"
}
```

## Contract Rules

- Do not rename fields without approval.
- Do not change data type silently.
- Do not remove fields unless documented.
- Backward compatibility must be considered for vendor/external integrations.

## Change Log

| Date | Change | Reason |
|---|---|---|
| YYYY-MM-DD | [Change] | [Reason] |
