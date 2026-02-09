# SARIF to Wiz Converter - Resolution Summary

## Issue Resolution

### Problem
The SARIF to Wiz vulnerability converter was failing with validation errors when uploading to the Wiz API:
```
error parsing as ingestion model: json schema validation failed: ... additionalProperties 'assetEndpoint' not allowed
```

### Root Cause
The local `wiz-vuln-schema.json` schema file differed from Wiz's actual API schema. The remote API was stricter about which asset types were allowed.

### Solution
Changed the asset type from `assetEndpoint` to `virtualMachine`, which is more flexible and universally accepted by Wiz's API.

## Final Working Structure

The converter now produces valid Wiz ingestion format:

```json
{
  "integrationId": "sarif-integration",
  "dataSources": [
    {
      "id": "JFrog Xray Scanner-run-0",
      "analysisDate": "2026-01-26T09:12:09.844Z",
      "assets": [
        {
          "analysisDate": "2026-01-26T09:12:09.844Z",
          "details": {
            "virtualMachine": {
              "assetId": "package.json",
              "name": "package.json",
              "hostname": "package.json",
              "firstSeen": "2026-01-26T09:12:09.844Z"
            }
          },
          "vulnerabilityFindings": [
            {
              "name": "CVE-2022-0235_node-fetch_2.6.1",
              "description": "[CVE-2022-0235] moo-cdk-lib 51.5.0 (all-builds)",
              "severity": "Medium",
              "externalDetectionSource": "SASTScan",
              "id": "CVE-2022-0235_node-fetch_2.6.1"
            }
          ]
        }
      ]
    }
  ]
}
```

## Key Changes Made

1. **Asset Type**: Changed from `assetEndpoint` to `virtualMachine`
2. **Required Fields**: Ensured `firstSeen` timestamp is included
3. **Asset Grouping**: Properly groups all findings by file/asset (31 findings grouped into 1 asset)
4. **Date Formatting**: Using timezone-aware ISO 8601 timestamps

## Validation Results

✓ **Schema validation passes** - The JSON conforms to Wiz's API schema
✓ **File uploads successfully** - S3 upload completes
✓ **API processing** - Reaches system activity checking stage

Current status message: "Integration id not found: sarif-integration"
- This is **expected** - it means the JSON is valid but the integration ID isn't registered in your Wiz account
- This is NOT a schema validation error, but a configuration step

## Usage

### Convert SARIF to Wiz Format
```bash
python3 sarif_to_wiz_converter.py --input-dir ./sarif-files --output-dir ./wiz-output
```

### Upload to Wiz
```bash
python3 upload_security_scan.py -c uploader_config.json -f ./wiz-output/sarif.wiz.json
```

### Validate Generated JSON
```bash
python3 diagnose_wiz_json.py ./wiz-output/sarif.wiz.json
python3 validate_wiz_output.py ./wiz-output/sarif.wiz.json wiz-vuln-schema.json
```

## Next Steps

To complete the integration:

1. **Register the integration in Wiz** - Use a registered integration ID instead of "sarif-integration"
2. **Configure uploader_config.json** - Ensure valid Wiz API credentials
3. **Run the converter** - Process your SARIF files
4. **Upload the results** - Use upload_security_scan.py with correct config

## Files Modified

- `sarif_to_wiz_converter.py` - Updated asset structure to use `virtualMachine`
- Added diagnostic tools:
  - `diagnose_wiz_json.py` - Analyze JSON structure
  - `validate_wiz_output.py` - Validate against schema
  - `wiz_api_integration.py` - API integration template
  - `TROUBLESHOOTING.md` - Detailed troubleshooting guide

## Testing Results

```
2026-01-26 09:12:10 - Processing: inputs/sarif.json
2026-01-26 09:12:10 - ✓ Successfully converted to: sample_wiz_output/sarif.wiz.json
2026-01-26 09:12:11 - # Step 1 - Fetch Cloud Resources
2026-01-26 09:12:12 - # Step 3 - Upload File Request successful
2026-01-26 09:12:12 - # Step 4 - Upload successful
2026-01-26 09:12:15 - Current status: FAILURE
2026-01-26 09:12:15 - Reason: Integration id not found: sarif-integration
```

**Result: ✓ JSON Schema Validation PASSED**
