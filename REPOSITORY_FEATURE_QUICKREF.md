# Quick Reference: Repository Feature

## TL;DR

The converter now accepts repository information to populate repository branch fields in the output.

### Two Modes

**Mode 1: Default (virtualMachine)**
```bash
python sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json
```

**Mode 2: Repository (repositoryBranch)**
```bash
python sarif_to_wiz_converter.py --input scan.sarif --output scan.wiz.json \
  --repository-name "my-app" \
  --repository-url "https://github.com/org/my-app"
```

## Key Points

✅ Both `--repository-name` AND `--repository-url` must be specified together  
✅ Both modes pass Wiz schema validation  
✅ Fully backward compatible - no breaking changes  
✅ Works with batch processing (`--input-dir` and `--output-dir`)  

## Asset Type Differences

### virtualMachine (Default)
- Used when no repository parameters provided
- Simpler structure with basic VM fields
- Best for: Non-repository findings (packages, services, etc.)

### repositoryBranch
- Used when both repository parameters provided  
- Includes repository details and VCS information
- Best for: Code repository scanning findings

## Example Output Structures

### virtualMachine
```json
"details": {
  "virtualMachine": {
    "assetId": "package.json",
    "name": "package.json",
    "hostname": "package.json",
    "firstSeen": "2026-01-26T20:37:48Z"
  }
}
```

### repositoryBranch
```json
"details": {
  "repositoryBranch": {
    "assetId": "package.json",
    "assetName": "package.json",
    "branchName": "main",
    "repository": {
      "name": "my-app",
      "url": "https://github.com/org/my-app"
    },
    "vcs": "GitHub",
    "firstSeen": "2026-01-26T20:38:05Z"
  }
}
```

## Error Cases

❌ Only `--repository-name` provided
```
ERROR: Both --repository-name and --repository-url must be specified together
```

❌ Only `--repository-url` provided  
```
ERROR: Both --repository-name and --repository-url must be specified together
```

✅ Both provided together → Works!  
✅ Neither provided → Works! (uses default virtualMachine)

## Files Modified

1. `sarif_to_wiz_converter.py` - Core converter logic with new parameters
2. `README_CONVERTER.md` - Updated usage guide with examples and asset type documentation
3. `REPOSITORY_FEATURE.md` - Comprehensive feature documentation

## Testing

All conversions validated:
- ✓ Default mode (virtualMachine) passes schema validation
- ✓ Repository mode (repositoryBranch) passes schema validation  
- ✓ Both modes with 31 findings pass validation
- ✓ Error handling validates parameter pairs
