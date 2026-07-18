# Security

## Purpose

Document security-sensitive areas of the project.

## Sensitive Areas

- Authentication
- Authorization
- Payment
- SSO
- API keys
- Personal data
- Logs
- Vendor integrations

## Secrets

| Secret | Storage Location | Rotation |
|---|---|---|
| [Secret name] | [Secret Manager/.env/etc.] | [Rotation rule] |

## Security Rules

- Never commit secrets.
- Do not log sensitive data.
- Mask personal identifiers where possible.
- API keys must be validated server-side.
- Payment callbacks/postbacks must be allowlisted and verified.
- Authentication changes require human approval.

## Review Requirements

Any change touching the following must be reviewed carefully:

- Login/session handling
- Token validation
- Payment gateway
- Webhook/callback endpoint
- Personal data export
- Database access control
