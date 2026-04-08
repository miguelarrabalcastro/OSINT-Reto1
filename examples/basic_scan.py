"""
PulseTrack — Basic scan example
Runs a one-shot scan and writes a PDF report.
"""

from src.scanner import Scanner, ScanTarget
from src.reporter import get_reporter, ReportMetadata
from src.config_loader import load_config

config = load_config("config/local.yaml")

scanner = Scanner(config)
target = ScanTarget(
    name="example_dmz",
    cidr="192.168.1.0/24",
    ports=[22, 80, 443, 8080, 8443],
)

results = scanner.scan_target(target)

metadata = ReportMetadata(
    author=config.get("reporting", {}).get("author", "PulseTrack"),
    organization="NovaTech Solutions",
    classification="INTERNAL",
)
reporter = get_reporter("pdf", output_dir="./reports", metadata=metadata)
report_path = reporter.generate(results, filename="basic_scan")

print(f"Report written to: {report_path}")
print(f"Open ports found: {len(results)}")
