#!/usr/bin/env python3
"""
Validate Wiz output JSON against the schema and show detailed structure.
"""

import json
import sys
from pathlib import Path

import jsonschema
from jsonschema import Draft4Validator, ValidationError


def load_json(path):
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def load_schema(path):
    """Load JSON schema."""
    with open(path, 'r') as f:
        return json.load(f)


def validate_and_report(json_file, schema_file):
    """Validate JSON against schema and report detailed issues."""
    try:
        json_doc = load_json(json_file)
        schema = load_schema(schema_file)

        validator = Draft4Validator(schema)

        print(f"\n{'='*70}")
        print(f"Validating: {json_file}")
        print(f"Schema: {schema_file}")
        print(f"{'='*70}\n")

        # Get all validation errors
        errors = list(validator.iter_errors(json_doc))

        if not errors:
            print("✓ JSON is VALID against schema\n")
            print("Document structure:")
            print(f"  - Integration ID: {json_doc.get('integrationId')}")
            print(f"  - Data Sources: {len(json_doc.get('dataSources', []))}")
            for ds_idx, ds in enumerate(json_doc.get('dataSources', [])):
                print(f"    [{ds_idx}] ID: {ds.get('id')}")
                print(f"        Assets: {len(ds.get('assets', []))}")
                for asset_idx, asset in enumerate(ds.get('assets', [])):
                    findings = asset.get('vulnerabilityFindings', [])
                    print(f"          [{asset_idx}] Findings: {len(findings)}")
                    if asset.get('details'):
                        details = asset['details']
                        if 'assetEndpoint' in details:
                            print(f"              Type: assetEndpoint")
                            print(f"              Name: {details['assetEndpoint'].get('assetName')}")
                        elif 'virtualMachine' in details:
                            print(f"              Type: virtualMachine")
                        elif 'networkAddress' in details:
                            print(f"              Type: networkAddress")
            return True

        else:
            print(f"✗ JSON has {len(errors)} validation error(s):\n")
            for idx, error in enumerate(errors, 1):
                print(f"Error {idx}:")
                print(f"  Message: {error.message}")
                print(f"  Path: {' -> '.join(str(p) for p in error.path)}")
                print(f"  Schema Path: {' -> '.join(str(p) for p in error.schema_path)}")
                print(f"  Validator: {error.validator}")
                if error.validator_value:
                    print(f"  Expected: {error.validator_value}")
                print()

            return False

    except FileNotFoundError as e:
        print(f"✗ File not found: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_wiz_output.py <wiz_json_file> [schema_file]")
        print("\nExample:")
        print("  python validate_wiz_output.py ./sample_wiz_output/sarif.wiz.json wiz-vuln-schema.json")
        return 1

    json_file = Path(sys.argv[1])
    schema_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("wiz-vuln-schema.json")

    if not json_file.exists():
        print(f"✗ JSON file not found: {json_file}")
        return 1

    if not schema_file.exists():
        print(f"✗ Schema file not found: {schema_file}")
        return 1

    success = validate_and_report(json_file, schema_file)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
