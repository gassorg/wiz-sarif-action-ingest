#!/usr/bin/env python3
"""
Example: Using the Field Mapping Engine Programmatically

This demonstrates how to work with the mapping engine directly,
without the command-line converter.
"""

from pathlib import Path
from mapping_engine import MappingEngine
import json


def example_basic_usage():
    """Basic usage: Load mappings and get summary."""
    engine = MappingEngine(Path("field_mappings.json"))
    
    print("=" * 60)
    print("ENABLED FIELD MAPPINGS")
    print("=" * 60)
    print(engine.get_mapping_summary())


def example_extract_value():
    """Example: Extract values from SARIF using mapping engine."""
    engine = MappingEngine(Path("field_mappings.json"))
    
    # Sample SARIF result
    sarif_result = {
        "ruleId": "CVE-2022-0235",
        "level": "warning",
        "message": {
            "text": "Found vulnerable dependency"
        },
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": "package.json"
                    }
                }
            }
        ],
        "properties": {
            "fixedVersion": "[2.6.7]"
        }
    }
    
    print("\n" + "=" * 60)
    print("EXTRACT VALUES FROM SARIF")
    print("=" * 60)
    
    # Extract each finding-level field
    for mapping in engine.get_field_mappings("finding_level"):
        field_path, value = engine.apply_mapping(sarif_result, mapping)
        print(f"{field_path:40} = {value}")
    
    # Extract target component fields
    print("\nTarget Component Fields:")
    for mapping in engine.get_field_mappings("target_component"):
        field_path, value = engine.apply_mapping(sarif_result, mapping)
        if value:
            print(f"{field_path:40} = {value}")


def example_custom_mapping():
    """Example: Customize mappings at runtime."""
    engine = MappingEngine(Path("field_mappings.json"))
    
    print("\n" + "=" * 60)
    print("CUSTOMIZE MAPPINGS AT RUNTIME")
    print("=" * 60)
    
    # Enable optional field
    print("\nEnabling remediation field...")
    engine.enable_mapping("optional_fields", "remediation", True)
    
    # Show updated summary
    print(engine.get_mapping_summary())


def example_build_finding():
    """Example: Build a complete finding using mappings."""
    engine = MappingEngine(Path("field_mappings.json"))
    
    sarif_result = {
        "ruleId": "CVE-2022-0235_node-fetch",
        "level": "error",
        "message": {
            "text": "[CVE-2022-0235] node-fetch vulnerable to SSRF"
        },
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": "package.json"
                    },
                    "region": {
                        "startLine": 1,
                        "endLine": 1
                    }
                }
            }
        ],
        "ruleIndex": -1,
        "properties": {
            "fixedVersion": "[2.6.7], [3.1.1]",
            "policies": "Medium_Vulnerabilities"
        }
    }
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE FINDING FROM SARIF")
    print("=" * 60)
    
    finding = {}
    
    # Apply finding-level mappings
    for mapping in engine.get_field_mappings("finding_level"):
        field_path, value = engine.apply_mapping(sarif_result, mapping)
        if value is not None:
            engine.set_nested_field(finding, field_path, value)
    
    # Apply target component mappings
    for mapping in engine.get_field_mappings("target_component"):
        field_path, value = engine.apply_mapping(sarif_result, mapping)
        if value is not None:
            engine.set_nested_field(finding, field_path, value)
    
    print(json.dumps(finding, indent=2))


def example_path_extraction():
    """Example: Demonstrate different path notations."""
    engine = MappingEngine(Path("field_mappings.json"))
    
    data = {
        "simple": "value",
        "nested": {
            "level1": {
                "level2": "deep_value"
            },
            "items": ["first", "second", "third"]
        },
        "array": [
            {"id": 0, "name": "first"},
            {"id": 1, "name": "second"}
        ]
    }
    
    print("\n" + "=" * 60)
    print("PATH EXTRACTION EXAMPLES")
    print("=" * 60)
    
    paths = [
        "simple",
        "nested.level1.level2",
        "nested.items[0]",
        "array[0].name",
        "array[1].id"
    ]
    
    for path in paths:
        value = engine.extract_value(data, path)
        print(f"{path:35} → {value}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + "Field Mapping Engine Examples".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    example_basic_usage()
    example_extract_value()
    example_custom_mapping()
    example_build_finding()
    example_path_extraction()
    
    print("\n")
