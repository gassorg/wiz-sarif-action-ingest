#!/usr/bin/env python3
"""
SARIF to Wiz Vulnerability Schema Converter

This script converts SARIF format security findings to Wiz vulnerability ingestion schema.
It validates input against sarif-schema.json and output against wiz-vuln-schema.json.

Usage:
    python sarif_to_wiz_converter.py --input <sarif_file> --output <wiz_file> [--integration-id <id>]
    python sarif_to_wiz_converter.py --input-dir <dir> --output-dir <dir> [--integration-id <id>]
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import jsonschema
from jsonschema import Draft4Validator, ValidationError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validates JSON documents against JSON schemas."""

    def __init__(self, schema_path: Path):
        """Initialize validator with a schema file."""
        self.schema_path = schema_path
        self.schema = self._load_schema(schema_path)
        self.validator = Draft4Validator(self.schema)

    @staticmethod
    def _load_schema(schema_path: Path) -> Dict[str, Any]:
        """Load JSON schema from file."""
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Schema file not found: {schema_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file {schema_path}: {e}")
            raise

    def validate(self, document: Dict[str, Any], name: str = "document") -> bool:
        """
        Validate document against schema.
        
        Args:
            document: Document to validate
            name: Name for logging purposes
            
        Returns:
            True if valid, raises ValidationError if not
        """
        try:
            self.validator.validate(document)
            logger.debug(f"✓ {name} is valid")
            return True
        except ValidationError as e:
            logger.error(f"✗ {name} validation failed: {e.message}")
            logger.error(f"  Path: {list(e.path)}")
            raise


class SARIFtoWizConverter:
    """Converts SARIF findings to Wiz vulnerability ingestion format."""

    def __init__(
        self,
        sarif_schema: SchemaValidator,
        wiz_schema: SchemaValidator,
        integration_id: str = "sarif-integration",
        repository_name: Optional[str] = None,
        repository_url: Optional[str] = None
    ):
        """Initialize converter with schema validators."""
        self.sarif_validator = sarif_schema
        self.wiz_validator = wiz_schema
        self.integration_id = integration_id
        self.repository_name = repository_name
        self.repository_url = repository_url

    def convert(self, sarif_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert SARIF document to Wiz vulnerability schema.
        
        Args:
            sarif_doc: Validated SARIF document
            
        Returns:
            Document conforming to wiz-vuln-schema.json
        """
        # Validate SARIF input
        self.sarif_validator.validate(sarif_doc, "SARIF input")

        wiz_doc = {
            "integrationId": self.integration_id,
            "dataSources": []
        }

        # Process each run in SARIF
        for run_idx, run in enumerate(sarif_doc.get("runs", [])):
            data_source = self._convert_run(run, run_idx)
            if data_source:
                wiz_doc["dataSources"].append(data_source)

        # Validate output
        self.wiz_validator.validate(wiz_doc, "Wiz output")

        return wiz_doc

    def _convert_run(self, run: Dict[str, Any], run_idx: int) -> Optional[Dict[str, Any]]:
        """
        Convert a SARIF run to a Wiz data source.
        
        Args:
            run: SARIF run object
            run_idx: Index of the run
            
        Returns:
            Wiz data source or None if no results
        """
        results = run.get("results", [])
        if not results:
            logger.debug(f"Run {run_idx} has no results")
            return None

        tool_name = run.get("tool", {}).get("driver", {}).get("name", "unknown-tool")

        data_source = {
            "id": f"{tool_name}-run-{run_idx}",
            "analysisDate": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "assets": []
        }

        # Group results by asset (file/URI)
        assets_map: Dict[str, Dict[str, Any]] = {}

        for result_idx, result in enumerate(results):
            asset_id, asset_details, finding = self._convert_result(
                result, result_idx, tool_name
            )

            if asset_id not in assets_map:
                assets_map[asset_id] = {
                    "analysisDate": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "details": asset_details,
                    "vulnerabilityFindings": []
                }

            assets_map[asset_id]["vulnerabilityFindings"].append(finding)

        data_source["assets"] = list(assets_map.values())
        return data_source

    def _convert_result(
        self, result: Dict[str, Any], result_idx: int, tool_name: str
    ) -> tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Convert a SARIF result to a Wiz asset and vulnerability finding.
        
        Args:
            result: SARIF result object
            result_idx: Index of the result
            tool_name: Name of the analysis tool
            
        Returns:
            Tuple of (asset_id, asset_details, vulnerability_finding)
        """
        # Extract asset information from locations
        locations = result.get("locations", [])
        physical_location = None
        
        if locations:
            physical_location = locations[0].get("physicalLocation", {})

        # Generate asset based on available location info
        asset_id, asset_details = self._extract_asset_details(
            physical_location, tool_name, result_idx
        )

        # Extract vulnerability finding information
        finding = self._extract_vulnerability_finding(result, result_idx)

        return asset_id, asset_details, finding

    def _extract_asset_details(
        self, physical_location: Dict[str, Any], tool_name: str, result_idx: int
    ) -> tuple[str, Dict[str, Any]]:
        """
        Extract asset details from SARIF location.
        
        Returns:
            Tuple of (asset_id, asset_details)
        """
        # Extract artifact information
        artifact_location = physical_location.get("artifactLocation", {})
        uri = artifact_location.get("uri", f"unknown-{result_idx}")

        # Use URI as asset ID (unique per file)
        asset_id = uri

        # If repository name and URL are provided, use repositoryBranch asset type
        if self.repository_name and self.repository_url:
            asset_details = {
                "repositoryBranch": {
                    "assetId": asset_id,
                    "assetName": uri,
                    "branchName": "main",
                    "repository": {
                        "name": self.repository_name,
                        "url": self.repository_url
                    },
                    "vcs": "GitHub",
                    "firstSeen": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                }
            }
        else:
            # Create virtualMachine as the asset type - most flexible and general-purpose
            # Works for any type of finding source (files, packages, services, etc.)
            asset_details = {
                "virtualMachine": {
                    "assetId": asset_id,
                    "name": uri,
                    "hostname": uri,
                    "firstSeen": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                }
            }

        return asset_id, asset_details

    def _extract_vulnerability_finding(
        self, result: Dict[str, Any], result_idx: int
    ) -> Dict[str, Any]:
        """Extract vulnerability finding from SARIF result."""
        message = result.get("message", {})
        message_text = message.get("text", "")

        # Extract rule information
        rule_id = result.get("ruleId", f"rule-{result_idx}")
        rule_index = result.get("ruleIndex", -1)

        # Map SARIF level to Wiz severity
        level = result.get("level", "warning")
        severity = self._map_severity(level)

        finding = {
            "name": f"{rule_id}",
            "description": message_text,
            "severity": severity,
            "externalDetectionSource": "ThirdPartyAgent"
        }

        # Add rule reference if available
        if rule_id:
            finding["id"] = rule_id

        # Extract target component from URI in locations
        locations = result.get("locations", [])
        if locations:
            physical_location = locations[0].get("physicalLocation", {})
            artifact_location = physical_location.get("artifactLocation", {})
            uri = artifact_location.get("uri")
            if uri:
                # Create targetComponent as a library object with filePath
                finding["targetComponent"] = {
                    "library": {
                        "filePath": uri
                    }
                }

        # Add any additional info
        if result.get("locations"):
            locations_str = json.dumps(result["locations"])
            finding["originalObject"] = {
                "locations": result["locations"],
                "ruleIndex": rule_index
            }

        return finding

    @staticmethod
    def _map_severity(sarif_level: str) -> str:
        """
        Map SARIF result level to Wiz severity.
        
        SARIF levels: 'none', 'note', 'warning', 'error'
        Wiz severities: 'None', 'Low', 'Medium', 'High', 'Critical'
        """
        mapping = {
            "none": "None",
            "note": "Low",
            "warning": "Medium",
            "error": "High"
        }
        return mapping.get(sarif_level.lower(), "Medium")


class PipelineProcessor:
    """Processes SARIF files for CI pipeline execution."""

    def __init__(
        self,
        sarif_schema_path: Path,
        wiz_schema_path: Path,
        integration_id: str = "sarif-integration",
        repository_name: Optional[str] = None,
        repository_url: Optional[str] = None
    ):
        """Initialize processor with schema validators."""
        self.sarif_validator = SchemaValidator(sarif_schema_path)
        self.wiz_validator = SchemaValidator(wiz_schema_path)
        self.converter = SARIFtoWizConverter(
            self.sarif_validator,
            self.wiz_validator,
            integration_id,
            repository_name,
            repository_url
        )

    def process_file(self, input_path: Path, output_path: Path) -> bool:
        """
        Process a single SARIF file.
        
        Args:
            input_path: Path to SARIF file
            output_path: Path to write Wiz file
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Processing: {input_path}")

            # Load SARIF
            with open(input_path, 'r') as f:
                sarif_doc = json.load(f)

            # Convert
            wiz_doc = self.converter.convert(sarif_doc)

            # Write output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(wiz_doc, f, indent=2)

            logger.info(f"✓ Successfully converted to: {output_path}")
            return True

        except FileNotFoundError as e:
            logger.error(f"✗ File not found: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"✗ Invalid JSON in {input_path}: {e}")
            return False
        except ValidationError as e:
            logger.error(f"✗ Validation error: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error processing {input_path}: {e}")
            if logger.level == logging.DEBUG:
                import traceback
                traceback.print_exc()
            return False

    def process_directory(self, input_dir: Path, output_dir: Path) -> int:
        """
        Process all SARIF files in a directory.
        
        Args:
            input_dir: Directory containing SARIF files
            output_dir: Directory to write Wiz files
            
        Returns:
            Number of successfully processed files
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return 0

        sarif_files = list(input_dir.glob("**/*.sarif")) + list(
            input_dir.glob("**/*.json")
        )

        if not sarif_files:
            logger.warning(f"No SARIF files found in {input_dir}")
            return 0

        success_count = 0
        for sarif_file in sarif_files:
            # Skip non-SARIF files
            if sarif_file.name.startswith("."):
                continue

            output_file = output_dir / sarif_file.relative_to(input_dir).with_suffix(
                ".wiz.json"
            )

            if self.process_file(sarif_file, output_file):
                success_count += 1

        logger.info(f"✓ Processed {success_count}/{len(sarif_files)} files")
        return success_count


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert SARIF files to Wiz vulnerability ingestion format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file
  python sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json

  # Batch convert directory
  python sarif_to_wiz_converter.py --input-dir ./results --output-dir ./wiz-results

  # With custom integration ID
  python sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json \\
    --integration-id my-org-sarif-scanner

  # With repository information (creates repositoryBranch assets)
  python sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json \\
    --repository-name "my-repo" --repository-url "https://github.com/org/my-repo"
        """
    )

    parser.add_argument(
        "--input",
        type=Path,
        help="Path to single SARIF input file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to Wiz output file"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        help="Directory containing SARIF files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for Wiz output files"
    )
    parser.add_argument(
        "--integration-id",
        type=str,
        default="sarif-integration",
        help="Integration ID for Wiz schema (default: sarif-integration)"
    )
    parser.add_argument(
        "--repository-name",
        type=str,
        default=None,
        help="Repository name for repositoryBranch asset type (e.g., 'my-repo')"
    )
    parser.add_argument(
        "--repository-url",
        type=str,
        default=None,
        help="Repository URL for repositoryBranch asset type (e.g., 'https://github.com/org/my-repo')"
    )
    parser.add_argument(
        "--sarif-schema",
        type=Path,
        default=Path(__file__).parent / "sarif-schema.json",
        help="Path to SARIF schema (default: sarif-schema.json in same dir)"
    )
    parser.add_argument(
        "--wiz-schema",
        type=Path,
        default=Path(__file__).parent / "wiz-vuln-schema.json",
        help="Path to Wiz schema (default: wiz-vuln-schema.json in same dir)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate arguments
    if args.input and args.input_dir:
        logger.error("Cannot specify both --input and --input-dir")
        return 1

    if not args.input and not args.input_dir:
        logger.error("Must specify either --input or --input-dir")
        parser.print_help()
        return 1

    if args.input and not args.output:
        logger.error("--output required when using --input")
        return 1

    if args.input_dir and not args.output_dir:
        logger.error("--output-dir required when using --input-dir")
        return 1

    # Validate repository parameters (both or neither required)
    if (args.repository_name and not args.repository_url) or (args.repository_url and not args.repository_name):
        logger.error("Both --repository-name and --repository-url must be specified together")
        return 1

    # Initialize processor
    try:
        processor = PipelineProcessor(
            args.sarif_schema,
            args.wiz_schema,
            args.integration_id,
            args.repository_name,
            args.repository_url
        )
    except Exception as e:
        logger.error(f"Failed to initialize processor: {e}")
        return 1

    # Process files
    if args.input:
        success = processor.process_file(args.input, args.output)
        return 0 if success else 1
    else:
        success_count = processor.process_directory(args.input_dir, args.output_dir)
        return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
