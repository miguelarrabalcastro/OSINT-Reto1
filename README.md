# PulseTrack

> Internal asset monitoring and vulnerability reporting platform  
> NovaTech Solutions — Security Engineering Team

---

## Overview

PulseTrack is a lightweight, modular security monitoring framework developed internally by the NovaTech SOC team. It provides continuous visibility over exposed assets, runs scheduled scan cycles, correlates CVE feeds against your infrastructure inventory, and generates structured PDF reports.

Originally built to replace a patchwork of cron jobs and bash scripts, PulseTrack v2.x introduced a proper plugin architecture and support for multiple external data sources via the `datasources.yaml` configuration.

**Current version:** 2.4.1 (stable)  
**Python:** 3.9+  
**License:** Internal use only — NovaTech Solutions

---

## Features

- **Asset inventory** — automatic network enumeration and fingerprinting
- **CVE correlation** — matches discovered services against NVD feed
- **Multi-source ingestion** — REST APIs, file sockets, Syslog, SNMP
- **Scheduling** — cron-like job runner with retry and backoff
- **Reports** — JSON, CSV and PDF export via pluggable reporter backends
- **Alerting** — Slack, email and webhook integrations
- **Audit trail** — all scans and actions logged to append-only store

---

## Quick Start

```bash
git clone https://github.com/novatech-sec/pulsetrack
cd pulsetrack
pip install -r requirements.txt
cp config/defaults.yaml config/local.yaml
# Edit config/local.yaml with your environment
python -m pulsetrack scan --config config/local.yaml
```

---

## Project Structure

```
pulsetrack/
├── src/
│   ├── scanner.py          Core scanner engine
│   ├── reporter.py         Report generation
│   ├── monitor.py          Continuous monitoring loop
│   ├── utils.py            Shared utilities
│   └── config_loader.py    Configuration management
├── config/
│   ├── defaults.yaml       Default configuration values
│   ├── datasources.yaml    External data source definitions
│   └── alerts.yaml         Alert rules and thresholds
├── docs/
│   ├── getting-started.md
│   ├── configuration.md
│   └── api-reference.md
├── examples/
│   ├── basic_scan.py
│   └── custom_reporter.py
└── tests/
    ├── conftest.py
    └── test_scanner.py
```

---

## Configuration

PulseTrack uses YAML configuration files. See `docs/configuration.md` for full reference.

Minimal working config:

```yaml
pulsetrack:
  version: "2.4"
  scan_interval: 3600
  output_dir: ./reports

targets:
  - name: "internal_network"
    cidr: "10.0.0.0/24"
    ports: [22, 80, 443, 8080, 8443]

reporting:
  format: pdf
  template: default
```

---

## Data Sources

External integrations are defined in `config/datasources.yaml`. PulseTrack supports REST endpoints, MQTT brokers and internal dashboards. See `docs/configuration.md#data-sources` for the full list of supported connector types.

---

## Team

| Role | Name |
|------|------|
| Lead Developer | A. Moreno |
| Security Architect | L. Gil |
| QA & Testing | C. Ruiz |
| Documentation | M. García |

---

## Changelog

See `CHANGELOG.md`
