# Field Mapping Configuration Guide

## Overview

The SARIF to Wiz converter now includes a flexible, configurable field mapping system. This allows you to:

- **Control which fields** are extracted from SARIF input
- **Transform values** before they're added to Wiz output
- **Enable/disable** specific field mappings
- **Extend functionality** with new transformations

All without modifying the converter code!

## How It Works

### 1. Configuration File

The `field_mappings.json` file defines all field mappings in a declarative, easy-to-understand format:

```json
{
  "wiz_field": "name",           // Target field in Wiz output
  "source": "sarif_result",      // Source: sarif_result, constant, or other
  "sarif_path": "ruleId",        // Path in SARIF result (dot notation)
  "default": "unnamed-finding",  // Default if not found
  "transform": "map_severity",   // Optional: transformation function
  "enabled": true,               // Enable/disable this mapping
  "description": "..."           // Human-readable description
}
```

### 2. Mapping Engine

The `MappingEngine` class (`mapping_engine.py`) processes the configuration:

- **Loads** the mapping configuration
- **Extracts** values from SARIF using configurable paths
- **Transforms** values using transformation functions
- **Applies** mappings to build the Wiz output

### 3. Converter Integration

The converter uses the mapping engine automatically when available:

```python
# With mapping config (recommended)
python sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json

# Or specify custom mapping config
python sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json \
  --mapping-config custom_mappings.json

# Without mapping config (uses hardcoded fallback)
python sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json \
  --mapping-config /dev/null  # Disables mapping engine
```

## Configuration Sections

### 1. `finding_level`

Core finding fields that appear in all findings:

- `name` - Vulnerability identifier (from ruleId)
- `description` - Vulnerability description
- `severity` - Severity level (mapped from SARIF level)
- `id` - Unique identifier
- `externalDetectionSource` - Always "ThirdPartyAgent"

### 2. `target_component`

The library component containing the vulnerability:

- `targetComponent.library.filePath` - File where vulnerability was found
- `targetComponent.library.name` - Component name
- `targetComponent.library.fixedVersion` - Available fix version

### 3. `optional_fields`

Additional fields (disabled by default, enable as needed):

- `remediation` - Remediation guidance text
- `cweId` - CWE identifier
- `cvssScore` - CVSS score

### 4. `metadata`

Metadata and debug information:

- `originalObject` - Original SARIF location and rule index

## Transformation Functions

Transformations are applied when extracting values:

### `map_severity`

Maps SARIF severity levels to Wiz severities:

```
none     → None
note     → Low
warning  → Medium
error    → High
```

### `clean_fixed_version`

Returns empty string if value is "no fix available", otherwise returns the value.

### `format_remediation`

Formats fixed version into a remediation string:

```
"2.6.7" → "Update to version: 2.6.7"
```

## Customizing Mappings

### Enable an Optional Field

Edit `field_mappings.json`:

```json
{
  "wiz_field": "remediation",
  "source": "sarif_result",
  "sarif_path": "properties.fixedVersion",
  "transform": "format_remediation",
  "enabled": true,  // Change from false to true
  "description": "Remediation guidance"
}
```

### Change a Mapping Path

To extract from a different SARIF field:

```json
{
  "wiz_field": "description",
  "source": "sarif_result",
  "sarif_path": "properties.customMessage",  // Changed path
  "default": "",
  "enabled": true
}
```

### Add a New Constant Value

```json
{
  "wiz_field": "customField",
  "source": "constant",
  "value": "my-custom-value",
  "enabled": true,
  "description": "Custom constant value"
}
```

### Create a Custom Transformation

1. Add transformation definition in `field_mappings.json`:

```json
"transformations": {
  "my_custom_transform": {
    "description": "Does something special",
    "some_config": "value"
  }
}
```

2. Implement in `mapping_engine.py`:

```python
def _compile_transformations(self):
    return {
        "my_custom_transform": self._transform_custom,
        # ... other transformations
    }

@staticmethod
def _transform_custom(value: str, transform_config: Dict) -> str:
    # Implementation here
    return transformed_value
```

3. Use in mapping:

```json
{
  "wiz_field": "customField",
  "source": "sarif_result",
  "sarif_path": "properties.someValue",
  "transform": "my_custom_transform",
  "enabled": true
}
```

## Path Syntax

The `sarif_path` supports several notations:

```
"ruleId"                                     → Direct field
"message.text"                               → Nested objects (dot notation)
"locations[0].physicalLocation"              → Array access and nesting
"properties.fixedVersion"                    → Nested properties
"locations[0].physicalLocation.region.line"  → Deep nesting
```

## Programmatic Usage

You can also use the mapping engine programmatically:

```python
from mapping_engine import MappingEngine
from pathlib import Path

# Initialize
engine = MappingEngine(Path("field_mappings.json"))

# Get enabled mappings for a section
finding_mappings = engine.get_field_mappings("finding_level")

# Extract and transform a value
wiz_field, value = engine.apply_mapping(sarif_result, mapping_config)

# Set nested field in output
engine.set_nested_field(output, "targetComponent.library.filePath", value)

# Get summary
print(engine.get_mapping_summary())

# Enable/disable mappings at runtime
engine.enable_mapping("optional_fields", "remediation", True)
```

## Best Practices

1. **Version your mappings** - Track changes to field_mappings.json in git
2. **Document custom transformations** - Add descriptions to the mapping config
3. **Test after changes** - Run the test suite after modifying mappings
4. **Keep it simple** - Use the configuration approach first before coding transformations
5. **Fallback values** - Always provide defaults for optional fields
6. **Path validation** - Test paths on sample SARIF data before deploying

## Troubleshooting

### Mapping not applied

Check that:
- Field is enabled: `"enabled": true`
- Source type is correct: `sarif_result`, `constant`, etc.
- Path is valid for your SARIF data

### Transformation not working

Verify:
- Transformation name exists in `transformations` section
- Function is implemented in `mapping_engine.py`
- Configuration is correct for the transformation

### Values always empty

Check:
- SARIF path exists in source data
- Default value is set if needed
- Source type matches the data location

## Migration from Hardcoded Mappings

The converter maintains backward compatibility. If mapping config is unavailable or disabled, it falls back to hardcoded extraction. This ensures existing workflows continue to work.

To migrate to the mapping system:

1. Review `field_mappings.json` to ensure it matches your needs
2. Run tests to verify identical output
3. Optionally customize the mappings
4. Commit `field_mappings.json` to version control
