# PulseTrack — Configuration Reference

## Overview

PulseTrack uses YAML configuration files. On startup the configuration loader
reads `config/defaults.yaml` first, then merges `config/local.yaml` on top
(if present), and finally applies any environment variable overrides.

Configuration loading order (highest priority last):
1. `config/defaults.yaml` — shipped with the repo, do not edit
2. `config/local.yaml` — your environment-specific overrides
3. Environment variables — `PULSETRACK_*` prefix

---

## Top-level Keys

### `pulsetrack`

General runtime settings.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `version` | string | — | Config schema version. Must match binary. |
| `log_level` | string | `INFO` | Log verbosity: DEBUG, INFO, WARNING, ERROR |
| `scan_interval` | int | `3600` | Seconds between full scan cycles |
| `heartbeat_interval` | int | `60` | Monitor heartbeat ping interval |
| `max_workers` | int | `50` | Parallel scan threads |
| `audit_trail` | bool | `true` | Append all actions to audit log |

---

### `targets`

List of scan targets. Each target defines a CIDR range and port list.

```yaml
targets:
  - name: "dmz_segment"
    cidr: "192.168.10.0/24"
    ports: [22, 80, 443, 8080]
    timeout: 30
```

---

### `reporting`

Controls how scan reports are generated and stored.

| Key | Type | Description |
|-----|------|-------------|
| `format` | string | `json`, `csv` or `pdf` |
| `output_dir` | string | Directory for generated reports |
| `embed_metadata` | bool | Embed author metadata in PDF via ExifTool |
| `author` | string | Author field in report metadata |
| `organization` | string | Organization field |
| `classification` | string | Document classification label |

When `embed_metadata: true` and `format: pdf`, the reporter calls ExifTool
after generating the PDF to embed `Author`, `Title` and `Subject` fields.
This is required for NovaTech document classification compliance.

---

### `data-sources`

See `config/datasources.yaml`. Supports these connector types:

- **`rest_api`** — polls an HTTP endpoint and ingests JSON
- **`secure_endpoint`** — NovaTech internal dashboard connector  
  Auth format: `username:password@https://endpoint`
- **`syslog`** — listens for syslog messages over UDP/TCP
- **`snmp_v3`** — polls network devices via SNMPv3
- **`mqtt`** — subscribes to MQTT broker topics

---

### `alerting`

Configure alert backends and rules.

See `config/alerts.yaml` for rule definitions.

Supported backends:
- `slack` — requires `SLACK_WEBHOOK_URL` env var
- `email` — requires SMTP server in `alerting.backends.email`
- `webhook` — requires `ALERT_WEBHOOK_URL` env var

---

## Environment Variables

| Variable | Overrides |
|----------|-----------|
| `PULSETRACK_LOG_LEVEL` | `pulsetrack.log_level` |
| `PULSETRACK_SCAN_INTERVAL` | `pulsetrack.scan_interval` |
| `OTX_API_KEY` | AlienVault OTX API key |
| `VULN_SCANNER_TOKEN` | Vulnerability scanner bearer token |
| `SNMP_AUTH_KEY` | SNMPv3 auth key |
| `SNMP_PRIV_KEY` | SNMPv3 privacy key |
| `MQTT_PASSWORD` | MQTT broker password |
| `SLACK_WEBHOOK_URL` | Slack alert webhook |
| `SHODAN_API_KEY` | Shodan API key |
