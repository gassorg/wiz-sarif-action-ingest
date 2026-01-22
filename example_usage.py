#!/usr/bin/env python3
"""
Example/test script showing how to use the SARIF to Wiz converter.

This demonstrates the converter in action with example data.
"""

import json
import tempfile
from pathlib import Path

from sarif_to_wiz_converter import (
    SARIFtoWizConverter,
    SchemaValidator,
    PipelineProcessor,
)


def create_example_sarif() -> dict:
    """Create a minimal valid SARIF 2.1.0 document for testing."""
    return {
        "$schema": "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "CodeScanner",
                        "version": "1.0",
                        "informationUri": "https://example.com",
                    }
                },
                "results": [
                    {
                        "ruleId": "CWE-79",
                        "level": "error",
                        "message": {
                            "text": "Potential cross-site scripting (XSS) vulnerability detected"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "src/handlers/user.js"
                                    },
                                    "region": {
                                        "startLine": 42
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "CWE-89",
                        "level": "warning",
                        "message": {
                            "text": "Potential SQL injection vulnerability"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "src/database/queries.js"
                                    },
                                    "region": {
                                        "startLine": 156
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "CWE-400",
                        "level": "note",
                        "message": {
                            "text": "Uncontrolled resource consumption detected"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "src/middleware/upload.js"
                                    },
                                    "region": {
                                        "startLine": 89
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }


def example_basic_conversion():
    """Example 1: Basic single-file conversion."""
    print("\n" + "="*60)
    print("Example 1: Basic Single-File Conversion")
    print("="*60)

    script_dir = Path(__file__).parent
    sarif_schema = SchemaValidator(script_dir / "sarif-schema.json")
    wiz_schema = SchemaValidator(script_dir / "wiz-vuln-schema.json")

    converter = SARIFtoWizConverter(
        sarif_schema,
        wiz_schema,
        integration_id="example-scanner"
    )

    # Create example SARIF
    sarif_doc = create_example_sarif()
    print("\nInput SARIF document created with 3 findings")
    print(f"  - Tool: {sarif_doc['runs'][0]['tool']['driver']['name']}")
    print(f"  - Results: {len(sarif_doc['runs'][0]['results'])}")

    # Convert
    wiz_doc = converter.convert(sarif_doc)
    print(f"\nConverted to Wiz format:")
    print(f"  - Integration ID: {wiz_doc['integrationId']}")
    print(f"  - Data sources: {len(wiz_doc['dataSources'])}")
    if wiz_doc['dataSources']:
        ds = wiz_doc['dataSources'][0]
        print(f"    - Source ID: {ds['id']}")
        print(f"    - Assets: {len(ds['assets'])}")
        for asset in ds['assets']:
            findings = asset.get('vulnerabilityFindings', [])
            print(f"      - {asset['details']['assetEndpoint']['assetName']}: {len(findings)} finding(s)")

    return wiz_doc


def example_file_processing():
    """Example 2: Process SARIF files using PipelineProcessor."""
    print("\n" + "="*60)
    print("Example 2: Pipeline File Processing")
    print("="*60)

    script_dir = Path(__file__).parent

    # Create temporary directories for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        input_dir = tmpdir / "sarif-input"
        output_dir = tmpdir / "wiz-output"

        input_dir.mkdir()

        # Create example SARIF files
        for i in range(2):
            sarif_file = input_dir / f"scan-{i}.sarif"
            sarif_doc = create_example_sarif()
            # Modify tool name to make them different
            sarif_doc['runs'][0]['tool']['driver']['name'] = f"Scanner-{i}"

            with open(sarif_file, 'w') as f:
                json.dump(sarif_doc, f, indent=2)
            print(f"Created test file: {sarif_file.name}")

        # Process using PipelineProcessor
        processor = PipelineProcessor(
            script_dir / "sarif-schema.json",
            script_dir / "wiz-vuln-schema.json",
            integration_id="pipeline-example"
        )

        print(f"\nProcessing directory: {input_dir}")
        success_count = processor.process_directory(input_dir, output_dir)

        print(f"\nResults:")
        print(f"  - Successfully processed: {success_count} files")
        print(f"  - Output directory: {output_dir}")

        if output_dir.exists():
            output_files = list(output_dir.glob("*.json"))
            for out_file in output_files:
                with open(out_file, 'r') as f:
                    doc = json.load(f)
                print(f"    - {out_file.name}: {len(doc['dataSources'][0]['assets'])} assets")


def example_severity_mapping():
    """Example 3: Demonstrate severity level mapping."""
    print("\n" + "="*60)
    print("Example 3: SARIF to Wiz Severity Mapping")
    print("="*60)

    script_dir = Path(__file__).parent
    sarif_schema = SchemaValidator(script_dir / "sarif-schema.json")
    wiz_schema = SchemaValidator(script_dir / "wiz-vuln-schema.json")

    converter = SARIFtoWizConverter(sarif_schema, wiz_schema)

    # Create SARIF with different severity levels
    sarif_doc = {
        "$schema": "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SeverityDemo",
                        "version": "1.0",
                        "informationUri": "https://example.com",
                    }
                },
                "results": [
                    {
                        "ruleId": "RULE-1",
                        "level": "error",
                        "message": {"text": "Critical issue"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "file1.js"}
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "RULE-2",
                        "level": "warning",
                        "message": {"text": "Warning level"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "file2.js"}
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "RULE-3",
                        "level": "note",
                        "message": {"text": "Informational"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "file3.js"}
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "RULE-4",
                        "level": "none",
                        "message": {"text": "No severity"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "file4.js"}
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }

    wiz_doc = converter.convert(sarif_doc)

    print("\nSARIF Level → Wiz Severity Mapping:")
    print("-" * 40)
    for asset in wiz_doc['dataSources'][0]['assets']:
        finding = asset['vulnerabilityFindings'][0]
        print(f"  {finding['name']:10} → {finding['severity']:10}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("SARIF to Wiz Converter - Usage Examples")
    print("="*60)

    try:
        # Run examples
        wiz_doc = example_basic_conversion()
        example_file_processing()
        example_severity_mapping()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")

        # Print example output
        print("Example converted Wiz document (partial):")
        print("-" * 60)
        print(json.dumps(wiz_doc, indent=2)[:1000] + "\n...\n")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
