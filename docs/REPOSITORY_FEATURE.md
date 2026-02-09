# Repository Feature Update

## Overview

The SARIF to Wiz converter has been updated to support repository information as input parameters. When repository details are provided, the converter generates `repositoryBranch` assets instead of the default `virtualMachine` assets.

## New Flags

### `--repository-name`
- **Type**: String
- **Description**: Repository name (e.g., 'my-app')
- **Required**: Only if `--repository-url` is specified
- **Example**: `--repository-name "my-app"`

### `--repository-url`
- **Type**: String  
- **Description**: Repository URL (e.g., 'https://github.com/org/my-app')
- **Required**: Only if `--repository-name` is specified
- **Example**: `--repository-url "https://github.com/org/my-app"`

## Usage

### Default Mode (virtualMachine)
When repository parameters are omitted, assets are created as `virtualMachine` type:

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json
```

**Output Asset Structure:**
```json
{
  "details": {
    "virtualMachine": {
      "assetId": "package.json",
      "name": "package.json",
      "hostname": "package.json",
      "firstSeen": "2026-01-26T20:37:48Z"
    }
  }
}
```

### Repository Mode (repositoryBranch)
When both repository parameters are provided, assets are created as `repositoryBranch` type:

```bash
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --repository-name "my-app" \
  --repository-url "https://github.com/org/my-app"
```

**Output Asset Structure:**
```json
{
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
}
```

## Validation

Both asset types are validated against the Wiz schema and pass schema validation:

```bash
# Test virtualMachine mode
python sarif_to_wiz_converter.py --input scan.sarif --output vm.wiz.json
python validate_wiz_output.py vm.wiz.json wiz-vuln-schema.json
# Output: ✓ JSON is VALID against schema

# Test repositoryBranch mode
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output repo.wiz.json \
  --repository-name "app" \
  --repository-url "https://github.com/org/app"
python validate_wiz_output.py repo.wiz.json wiz-vuln-schema.json
# Output: ✓ JSON is VALID against schema
```

## Error Handling

The converter validates that both repository parameters are specified together. If only one is provided, it will error:

```bash
# ❌ This will fail
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --repository-name "my-app"
# Error: Both --repository-name and --repository-url must be specified together

# ✅ This will succeed
python sarif_to_wiz_converter.py \
  --input scan.sarif \
  --output scan.wiz.json \
  --repository-name "my-app" \
  --repository-url "https://github.com/org/my-app"
```

## CI/CD Integration Example

### GitHub Actions
```yaml
- name: Convert SARIF results with repository info
  run: |
    python sarif_to_wiz_converter.py \
      --input-dir ./sarif-results \
      --output-dir ./wiz-results \
      --integration-id github-actions-scan \
      --repository-name ${{ github.repository }} \
      --repository-url ${{ github.server_url }}/${{ github.repository }}
```

## Implementation Details

### Code Changes

1. **SARIFtoWizConverter class** (`sarif_to_wiz_converter.py` lines 73-82)
   - Added `repository_name` and `repository_url` parameters
   - Stored as instance variables

2. **_extract_asset_details method** (`sarif_to_wiz_converter.py` lines 199-236)
   - Checks if repository parameters are provided
   - Creates `repositoryBranch` asset if both parameters exist
   - Creates `virtualMachine` asset (default) otherwise
   - Automatically sets `branchName` to "main" and `vcs` to "GitHub"

3. **PipelineProcessor class** (`sarif_to_wiz_converter.py` lines 301-318)
   - Updated constructor to accept and pass repository parameters

4. **CLI Argument Parser** (`sarif_to_wiz_converter.py` lines 435-462)
   - Added `--repository-name` flag
   - Added `--repository-url` flag
   - Added validation to require both or neither

5. **Documentation** (`README_CONVERTER.md`)
   - Added "Asset Types" section
   - Added usage examples for repository mode
   - Updated GitHub Actions CI/CD example

## Backward Compatibility

✅ **Fully backward compatible**
- Existing scripts without repository parameters continue to work
- Default behavior (virtualMachine) unchanged
- All existing test files pass validation

## Testing

All conversions pass schema validation:
- virtualMachine assets: ✓ Valid
- repositoryBranch assets: ✓ Valid
- Both modes with 31 findings: ✓ Valid
- Schema compatibility: ✓ Verified with wiz-vuln-schema.json
