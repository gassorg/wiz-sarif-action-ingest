# Field Mapping System - Implementation Summary

## What Was Added

A complete, flexible field mapping system that allows you to control SARIF → Wiz field mappings without modifying code.

### New Files

1. **`field_mappings.json`** - Configuration file defining all field mappings
2. **`mapping_engine.py`** - Mapping engine that processes the configuration
3. **`example_mapping_usage.py`** - Examples showing how to use the mapping system
4. **`FIELD_MAPPING_GUIDE.md`** - Comprehensive documentation

### Modified Files

1. **`sarif_to_wiz_converter.py`** - Updated to use mapping engine (backward compatible)

## Key Features

### 1. **Declarative Configuration**
Define mappings in JSON, not code:
```json
{
  "wiz_field": "name",
  "source": "sarif_result",
  "sarif_path": "ruleId",
  "enabled": true
}
```

### 2. **Easy to Understand**
- Clear field-to-field mappings
- Human-readable descriptions
- Sections for different mapping types

### 3. **Easy to Update**
- Edit JSON to enable/disable fields
- Change extraction paths
- Add custom transformations
- No code recompilation needed

### 4. **Portable**
- No external dependencies (uses only standard library)
- Single JSON file to configure
- Works in any environment

### 5. **Backward Compatible**
- Converter works with or without mapping config
- Fallback to hardcoded logic if config unavailable
- Existing workflows unaffected

## Mapping Sections

### `finding_level` (Required)
Core fields in every finding:
- `name` - Vulnerability identifier
- `description` - Description text
- `severity` - Severity level
- `id` - Unique ID
- `externalDetectionSource` - Detection source

### `target_component` (Core)
Library/component information:
- `targetComponent.library.filePath` - File location
- `targetComponent.library.name` - Component name
- `targetComponent.library.fixedVersion` - Fix version

### `optional_fields` (Extensible)
Additional fields (disabled by default):
- `remediation` - Fix guidance
- `cweId` - CWE identifier
- `cvssScore` - CVSS score
- Easily add new optional fields

### `metadata` (Debug)
Additional information:
- `originalObject` - Original SARIF data for debugging

## Configuration Examples

### Enable Remediation Field

Edit `field_mappings.json`:
```json
{
  "wiz_field": "remediation",
  "enabled": true  // Change from false
}
```

### Change Extraction Path

```json
{
  "wiz_field": "description",
  "sarif_path": "properties.customMessage"  // New path
}
```

### Add Constant Value

```json
{
  "wiz_field": "source",
  "source": "constant",
  "value": "custom-tool"
}
```

## Usage Examples

### Via Command Line
```bash
# Use default mappings
python3 sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json

# Use custom mappings
python3 sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json \
  --mapping-config custom_mappings.json
```

### Programmatically
```python
from mapping_engine import MappingEngine
from pathlib import Path

engine = MappingEngine(Path("field_mappings.json"))

# Get all enabled mappings
all_mappings = engine.get_all_enabled_mappings()

# Extract value from SARIF
value = engine.extract_value(sarif_result, "message.text")

# Apply transformation
field, value = engine.apply_mapping(sarif_result, mapping_config)
```

## Path Syntax Supported

```
ruleId                                    - Direct field
message.text                              - Nested objects
locations[0].physicalLocation             - Array access
properties.fixedVersion                   - Nested in object
locations[0].physicalLocation.region.line - Deep nesting
```

## Transformation Functions

### Built-in Transformations

1. **`map_severity`** - Maps SARIF levels to Wiz severities
   - none → None
   - note → Low
   - warning → Medium
   - error → High

2. **`clean_fixed_version`** - Handles "no fix available"
   - Returns empty string if value is "no fix available"
   - Otherwise returns the value

3. **`format_remediation`** - Formats fix version
   - Template: "Update to version: {value}"

### Adding Custom Transformations

1. Add definition to `field_mappings.json`:
```json
"transformations": {
  "my_transform": {
    "description": "My custom transformation",
    "config_key": "config_value"
  }
}
```

2. Implement in `mapping_engine.py`:
```python
@staticmethod
def _transform_my_transform(value: str, config: Dict) -> str:
    # Your logic here
    return transformed_value
```

3. Use in mapping:
```json
{
  "wiz_field": "field",
  "transform": "my_transform"
}
```

## API Reference

### MappingEngine Class

```python
class MappingEngine:
    # Initialize
    __init__(config_path: Path)
    
    # Get mappings
    get_field_mappings(section: str) -> List[Dict]
    get_all_enabled_mappings() -> Dict[str, List[Dict]]
    
    # Extract values
    extract_value(obj: Dict, path: str) -> Any
    
    # Apply mapping
    apply_mapping(sarif_result: Dict, mapping: Dict) -> (str, Any)
    
    # Set values
    set_nested_field(obj: Dict, path: str, value: Any)
    
    # Management
    enable_mapping(section: str, field: str, enabled: bool)
    get_mapping_summary() -> str
```

## Benefits

| Benefit | Details |
|---------|---------|
| **No Code Changes** | Modify mappings by editing JSON |
| **Extensible** | Add new fields/transformations easily |
| **Version Control** | Track mapping changes in git |
| **Documentation** | Each mapping is self-documented |
| **Reusable** | Share mapping configs across projects |
| **Testing** | Test different configs without rebuilding |
| **Production Ready** | Backward compatible with existing code |

## Testing

All existing tests pass unchanged:
```bash
python3 tests/test_repository_feature.py
✅ ALL TESTS PASSED
```

The mapping system is transparent to tests and doesn't change behavior.

## Best Practices

1. **Version your mappings** - Commit `field_mappings.json` to git
2. **Document custom fields** - Update descriptions when you customize
3. **Test changes** - Run tests after modifying mappings
4. **Use comments** - Add `description` field for clarity
5. **Provide defaults** - Set fallback values for optional fields
6. **Keep it simple** - Use configuration approach before coding transformations

## Migration Path

For users upgrading to this version:

1. ✅ System is automatic - no changes required
2. ✅ Existing workflows continue working
3. ✅ Optional - customize `field_mappings.json` if needed
4. ✅ Future-proof - extend with custom transformations

## Next Steps

1. Review `field_mappings.json` for your use cases
2. Customize enabled fields based on needs
3. Test with your SARIF files
4. Share mapping configs across teams
5. Version control the mappings file

## Files Overview

```
├── field_mappings.json          # Configuration (JSON)
├── mapping_engine.py            # Engine implementation
├── sarif_to_wiz_converter.py    # Converter (updated)
├── example_mapping_usage.py     # Usage examples
├── FIELD_MAPPING_GUIDE.md       # Detailed documentation
└── README.md                    # This file
```

## Questions?

See `FIELD_MAPPING_GUIDE.md` for comprehensive documentation on:
- Configuration options
- Customization examples
- Troubleshooting
- Advanced usage
