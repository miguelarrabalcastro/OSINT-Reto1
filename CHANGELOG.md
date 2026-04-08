# Changelog

All notable changes to PulseTrack are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.4.1] — 2024-03-20

### Fixed
- Fixed null pointer exception in `reporter.py` when scan returns zero assets (#112)
- Corrected YAML parsing edge case for multi-value alert conditions (#108)
- PDF template no longer crashes on Unicode hostnames (#105)

### Changed
- Default scan timeout raised from 30s to 45s for slow environments

---

## [2.4.0] — 2024-02-14

### Added
- New `monitor.py` continuous monitoring loop with configurable heartbeat
- Slack alerting backend (`alerts.yaml` integration)
- `--dry-run` flag for scanner to preview targets without sending packets
- ExifTool integration in reporter for embedding metadata in PDF exports

### Changed
- `config_loader.py` now validates all required fields on startup and exits cleanly
- Scanner engine refactored: parallel scan workers via `concurrent.futures`
- Log format standardised across all modules

### Fixed
- Race condition in monitor loop when two scans overlapped (#98)
- Missing `Content-Type` header on webhook alerts (#94)

---

## [2.3.2] — 2024-01-08

### Fixed
- `datasources.yaml` hot-reload was not picking up new entries without restart (#89)
- Auth token refresh logic for secure endpoint connectors

---

## [2.3.1] — 2023-12-19

### Added
- CSV export format for asset reports
- SNMP v3 data source connector (beta)

### Fixed
- Encoding issue with non-ASCII target descriptions (#81)

---

## [2.3.0] — 2023-11-05

### Added
- Plugin architecture for custom scanner modules
- Secure endpoint connector type in `datasources.yaml` (replaces legacy `internal_api`)
- `pulsetrack audit` subcommand — replays last N scan results from the audit trail

### Changed
- Minimum Python version raised to 3.9
- Configuration schema versioned: add `version: "2.3"` to existing configs

---

## [2.2.0] — 2023-08-22

### Added
- PDF reports via ReportLab (see `docs/configuration.md#reporting`)
- `--since` flag: filter report to assets changed after a given date
- Alert cooldown: prevents duplicate notifications within a configurable window

---

## [2.1.0] — 2023-05-30

### Added
- Multi-target configuration support
- Webhook alerting (Slack, Teams, generic HTTP)

### Fixed
- Scanner would silently skip targets with invalid CIDR notation (#42)

---

## [2.0.0] — 2023-02-14

### Changed
- **Breaking**: Full rewrite of core engine. Configuration format changed from INI to YAML.
- CLI interface redesigned with subcommands (`scan`, `report`, `monitor`, `audit`)

---

## [1.x]

Legacy version. No longer maintained. See internal wiki for migration guide.
