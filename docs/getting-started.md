# Getting Started with PulseTrack

## Prerequisites

- Python 3.9 or later
- `pip` and optionally a virtual environment
- ExifTool (for PDF metadata embedding): https://exiftool.org
- Network access to your target ranges

## Installation

```bash
git clone https://github.com/novatech-sec/pulsetrack
cd pulsetrack
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## First Scan

Copy the defaults and add your target network:

```bash
cp config/defaults.yaml config/local.yaml
```

Edit `config/local.yaml`:

```yaml
targets:
  - name: "my_network"
    cidr: "192.168.1.0/24"
    ports: [22, 80, 443]
```

Run a single scan:

```bash
python -m pulsetrack scan --config config/local.yaml
```

Results are written to `./reports/` as a PDF (or JSON/CSV — see `reporting.format`).

## Continuous Monitoring

```bash
python -m pulsetrack monitor --config config/local.yaml
```

The monitor loop runs indefinitely. Stop it with `Ctrl+C` or `SIGTERM`.

## Next Steps

- Configure external data sources: `config/datasources.yaml`
- Set up alert notifications: `config/alerts.yaml`
- See the full reference: `docs/configuration.md`
