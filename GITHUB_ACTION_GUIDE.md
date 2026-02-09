# GitHub Action: SARIF to Wiz Batch Convert & Upload

This GitHub Action automates the conversion of SARIF security scan files to Wiz vulnerability ingestion format and uploads them to the Wiz platform.

## Workflow Features

✓ **Batch Conversion** - Converts multiple SARIF files in a single run  
✓ **Flexible Input** - Supports directory-based input or manual parameter override  
✓ **Wiz Integration** - Automatically uploads converted files to Wiz platform  
✓ **Repository Context** - Optional repository and branch information for asset tracking  
✓ **CVE Filtering** - Optional CVE-only mode to filter non-CVE findings  
✓ **Reporting** - Generates summary report in GitHub Actions workflow summary  
✓ **Artifact Storage** - Saves converted files as workflow artifacts  

## Setup Requirements

### 1. Wiz API Credentials

Create `uploader_config.json` in your repository root:

```json
{
  "CLIENT_ID": "your-wiz-client-id",
  "CLIENT_SECRET": "your-wiz-client-secret",
  "TOKEN_URL": "https://auth.app.wiz.io/oauth/token",
  "API_ENDPOINT_URL": "https://api.us17.app.wiz.io/graphql"
}
```

**Important**: Add `uploader_config.json` to `.gitignore` to prevent credential leaks:

```
uploader_config.json
```

Alternatively, use GitHub Secrets:
```yaml
# In your workflow, set environment variables from secrets
env:
  WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
  WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
  WIZ_TOKEN_URL: ${{ secrets.WIZ_TOKEN_URL }}
  WIZ_API_ENDPOINT: ${{ secrets.WIZ_API_ENDPOINT }}
```

### 2. SARIF Input Files

Place SARIF files in a directory (default: `.sarif-reports/`):

```
your-repo/
├── .sarif-reports/
│   ├── semgrep-results.sarif
│   ├── snyk-results.sarif
│   └── checkmarx-results.sarif
├── .github/workflows/sarif-to-wiz-batch-upload.yml
└── uploader_config.json
```

## Usage

### Trigger via Workflow Dispatch (Manual)

1. Go to **Actions** tab in your GitHub repository
2. Select **SARIF to Wiz - Batch Convert & Upload** workflow
3. Click **Run workflow**
4. Configure parameters:
   - **SARIF Input Directory**: `.sarif-reports` (or your custom path)
   - **Repository Name**: (optional) Your repository name
   - **Repository URL**: (optional) Your repository URL
   - **Branch Name**: (optional) Branch being scanned
   - **CVE Only**: (optional) Enable to filter non-CVE findings
   - **API Config Path**: `uploader_config.json` (or custom path)

### Automatic Trigger on Push

The workflow automatically triggers when SARIF files are committed:

```yaml
on:
  push:
    paths:
      - '**.sarif'
      - '**.json'
```

### Programmatic Trigger

Trigger via GitHub CLI:

```bash
gh workflow run sarif-to-wiz-batch-upload.yml \
  -f sarif_input_dir=".sarif-reports" \
  -f repository_name="my-repo" \
  -f repository_url="https://github.com/org/my-repo" \
  -f branch_name="main"
```

## Workflow Steps

### 1. Checkout Code
Clones your repository with full history

### 2. Setup Python
Installs Python 3.11 and dependencies

### 3. Convert SARIF Files
Runs batch conversion with optional parameters:

```bash
python3 sarif_to_wiz_converter.py \
  --input-dir <sarif_directory> \
  --output-dir ./wiz-scan-results \
  --repository-name <optional> \
  --repository-url <optional> \
  --branch-name <optional> \
  --cve-only <optional> \
  --verbose
```

### 4. Verify Conversion
Ensures `.wiz.json` files were successfully created

### 5. Upload to Wiz
Uploads each converted file using the Wiz API:

```bash
python3 upload_security_scan.py \
  -c uploader_config.json \
  -f <wiz_json_file>
```

### 6. Generate Report
Creates a summary in the GitHub Actions workflow summary

### 7. Store Artifacts
Saves converted files as artifacts for 30 days

## Input Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `sarif_input_dir` | No | `.sarif-reports` | Directory containing SARIF files |
| `repository_name` | No | - | Repository name (creates repositoryBranch assets) |
| `repository_url` | No | - | Repository URL (required if repository_name provided) |
| `branch_name` | No | - | Branch being scanned (e.g., `main`, `develop`) |
| `cve_only` | No | false | Enable CVE-only filtering mode |
| `wiz_api_config` | No | `uploader_config.json` | Path to Wiz API configuration |

## Output

### Converted Files
- Location: `./wiz-scan-results/`
- Format: `*.wiz.json`
- Uploaded to: Wiz platform via API

### Artifacts
- Workflow artifacts: Stored for 30 days
- GitHub Actions summary: Conversion report with file counts

### Logs
- GitHub Actions logs show:
  - Files converted
  - Upload status for each file
  - Any errors or warnings

## Example Configurations

### Basic Batch Conversion & Upload

```yaml
on: workflow_dispatch

jobs:
  convert-upload:
    runs-on: ubuntu-latest
    steps:
      # ... (workflow file handles this automatically)
```

### With Repository Context

**Inputs:**
- Repository Name: `my-app`
- Repository URL: `https://github.com/org/my-app`
- Branch Name: `main`

**Result:**
- Assets created as `repositoryBranch` type
- Data source ID: `my-app/main`

### CVE-Only Mode

**Inputs:**
- CVE Only: `true`

**Result:**
- Only CVE-YYYY-NNNNN format findings included
- Finding names simplified to CVE identifier
- Non-CVE findings filtered out

## Error Handling

The workflow implements graceful error handling:

- **Conversion Failure**: Stops workflow and reports error
- **Upload Failure**: Logs warning and continues with next file
- **Missing Files**: Reports and exits with error code
- **Invalid Config**: Clear error messages with path info

## Environment Variables

Optional: Set Wiz credentials via GitHub Secrets:

```yaml
env:
  WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
  WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
  WIZ_TOKEN_URL: ${{ secrets.WIZ_TOKEN_URL }}
  WIZ_API_ENDPOINT: ${{ secrets.WIZ_API_ENDPOINT }}
```

Then update `uploader_config.json` to reference these variables.

## Troubleshooting

### Conversion Fails
- Check SARIF file format validity
- Verify `--verbose` flag shows detailed errors
- Check logs for schema validation failures

### Upload Fails
- Verify Wiz API credentials in `uploader_config.json`
- Check API endpoint is correct for your Wiz region
- Ensure client has permissions to ingest vulnerabilities

### No Files Converted
- Verify SARIF directory path is correct
- Check SARIF files have `.sarif` or `.json` extension
- Review conversion logs for schema errors

### Missing Artifacts
- Check workflow completed successfully
- Verify artifact retention period not exceeded
- Check storage limits on GitHub account

## Best Practices

1. **Secure Credentials**
   - Use GitHub Secrets for API credentials
   - Never commit `uploader_config.json` with real credentials
   - Rotate credentials periodically

2. **Repository Context**
   - Always provide repository name and URL for tracking
   - Use branch name to identify which branch was scanned
   - Enables accurate asset identification in Wiz

3. **CVE Filtering**
   - Enable CVE-only mode for vulnerability scanning tools
   - Disable for compliance/configuration scanning

4. **File Organization**
   - Keep SARIF files in dedicated directory (e.g., `.sarif-reports/`)
   - Use clear naming conventions for source tools
   - Archive old results regularly

5. **Monitoring**
   - Review workflow summary reports
   - Check Wiz platform for successful findings ingestion
   - Set up GitHub Actions notifications for failures

## Integration Examples

### With Semgrep

```yaml
- name: Semgrep Scan
  uses: returntocorp/semgrep-action@v1
  with:
    sarif: results.sarif
    
- name: Move SARIF to reports
  run: mv results.sarif .sarif-reports/
  
- name: Trigger SARIF to Wiz workflow
  run: gh workflow run sarif-to-wiz-batch-upload.yml
```

### With Snyk

```yaml
- name: Snyk Scan
  uses: snyk/actions/python-3.11@master
  with:
    args: --sarif-file-output=snyk.sarif
    
- name: Move SARIF to reports
  run: mv snyk.sarif .sarif-reports/
  
- name: Trigger SARIF to Wiz workflow
  run: gh workflow run sarif-to-wiz-batch-upload.yml
```

## See Also

- [SARIF to Wiz Converter Documentation](README.md)
- [Wiz API Documentation](https://docs.wiz.io/dev/api-overview)
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
