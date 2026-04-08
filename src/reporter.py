"""
PulseTrack — Reporter
Generates scan reports in JSON, CSV and PDF formats.
ExifTool is used to embed metadata into PDF exports.
"""

import json
import csv
import logging
import subprocess
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportMetadata:
    """Metadata to embed in generated reports."""

    def __init__(self, author: str, organization: str, classification: str = "INTERNAL"):
        self.author = author
        self.organization = organization
        self.classification = classification
        self.generated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "author": self.author,
            "organization": self.organization,
            "classification": self.classification,
            "generated_at": self.generated_at,
        }


class BaseReporter:
    def __init__(self, output_dir: str, metadata: Optional[ReportMetadata] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = metadata

    def generate(self, results: List[Dict], filename: str) -> Path:
        raise NotImplementedError


class JSONReporter(BaseReporter):
    def generate(self, results: List[Dict], filename: str) -> Path:
        path = self.output_dir / f"{filename}.json"
        payload = {
            "metadata": self.metadata.to_dict() if self.metadata else {},
            "results": results,
            "total": len(results),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        logger.info(f"JSON report written: {path}")
        return path


class CSVReporter(BaseReporter):
    def generate(self, results: List[Dict], filename: str) -> Path:
        path = self.output_dir / f"{filename}.csv"
        if not results:
            logger.warning("No results to write to CSV")
            return path
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        logger.info(f"CSV report written: {path}")
        return path


class PDFReporter(BaseReporter):
    """
    PDF report generator. Uses ReportLab for layout and ExifTool to embed
    author metadata into the output file.

    ExifTool integration:
        After the PDF is generated, `_embed_metadata()` calls exiftool to set
        the Author, Title and Subject fields in the PDF metadata. This ensures
        audit trail compliance with the NovaTech document classification policy.
    """

    def generate(self, results: List[Dict], filename: str) -> Path:
        path = self.output_dir / f"{filename}.pdf"
        self._render_pdf(results, path)
        if self.metadata:
            self._embed_metadata(path)
        return path

    def _render_pdf(self, results: List[Dict], path: Path):
        # Simplified stub — full ReportLab template in internal confluence page
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet

            doc = SimpleDocTemplate(str(path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = [Paragraph("PulseTrack Security Report", styles["Title"])]

            if results:
                headers = list(results[0].keys())
                data = [headers] + [[str(r.get(k, "")) for k in headers] for r in results]
                table = Table(data)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                story.append(table)

            doc.build(story)
            logger.info(f"PDF rendered: {path}")
        except ImportError:
            logger.warning("ReportLab not available — writing placeholder PDF")
            path.write_bytes(b"%PDF-1.4 placeholder")

    def _embed_metadata(self, path: Path):
        """Embed author metadata using ExifTool."""
        if not self.metadata:
            return
        cmd = [
            "exiftool", "-overwrite_original",
            f"-Author={self.metadata.author}",
            f"-Title=PulseTrack Security Report",
            f"-Subject={self.metadata.classification} — {self.metadata.organization}",
            str(path),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Metadata embedded via ExifTool: {path}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"ExifTool not available or failed: {e}")


def get_reporter(fmt: str, output_dir: str, metadata: Optional[ReportMetadata] = None) -> BaseReporter:
    mapping = {
        "json": JSONReporter,
        "csv": CSVReporter,
        "pdf": PDFReporter,
    }
    cls = mapping.get(fmt.lower())
    if not cls:
        raise ValueError(f"Unknown report format: {fmt!r}. Options: {list(mapping)}")
    return cls(output_dir=output_dir, metadata=metadata)
