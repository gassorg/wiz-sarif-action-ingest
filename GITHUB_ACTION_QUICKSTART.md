# Quick Start: GitHub Action for SARIF to Wiz

## 5-Minute Setup

### Step 1: Add Wiz Credentials
Create `.gitignore` entry (if not exists):
```
uploader_config.json
```

Create `uploader_config.json` in repo root:
```json
{
  "CLIENT_ID": "your-wiz-client-id",
  "CLIENT_SECRET": "your-wiz-client-secret",
  "TOKEN_URL": "https://auth.app.wiz.io/oauth/token", #find this under tenant info > authentication url
  "API_ENDPOINT_URL": "https://api.us17.app.wiz.io/graphql" #find this under tenant info > api endpoint url
}
```

### Step 2: Create SARIF Directory
```bash
mkdir -p .sarif-reports
```

Place SARIF files in `.sarif-reports/`

### Step 3: Workflow Is Ready
The action file is already in `.github/workflows/sarif-to-wiz-batch-upload.yml`

## Usage

### Manual Trigger
1. Go to **Actions** tab
2. Select **SARIF to Wiz - Batch Convert & Upload**
3. Click **Run workflow**
4. (Optional) Set parameters
5. Click **Run workflow**

### Automatic Trigger
Just commit SARIF files:
```bash
git add .sarif-reports/your-scan.sarif
git commit -m "Add security scan results"
git push
```

## Common Commands

### Via GitHub CLI
```bash
# Basic batch conversion
gh workflow run sarif-to-wiz-batch-upload.yml

# With repository context
gh workflow run sarif-to-wiz-batch-upload.yml \
  -f repository_name="my-app" \
  -f repository_url="https://github.com/org/my-app" \
  -f branch_name="main"

# CVE-only mode
gh workflow run sarif-to-wiz-batch-upload.yml \
  -f cve_only=true
```

## What It Does

1. ✅ Converts all SARIF files in `.sarif-reports/`
2. ✅ Creates `.wiz.json` files in `./wiz-scan-results/`
3. ✅ Uploads to Wiz platform using credentials
4. ✅ Generates summary report
5. ✅ Saves results as artifacts

## Parameters

| Parameter | Type | Example |
|-----------|------|---------|
| `sarif_input_dir` | text | `.sarif-reports` |
| `repository_name` | text | `my-app` |
| `repository_url` | text | `https://github.com/org/my-app` |
| `branch_name` | text | `main` |
| `cve_only` | boolean | `true/false` |
| `wiz_api_config` | text | `uploader_config.json` |

## Troubleshooting

**Q: "Config file not found"**
- A: Ensure `uploader_config.json` exists in repo root and is committed

**Q: "No SARIF files found"**
- A: Check SARIF files are in `.sarif-reports/` directory

**Q: "Upload failed"**
- A: Verify Wiz credentials in `uploader_config.json` are correct

**Q: "Files not visible in artifacts"**
- A: Check workflow completed successfully (green checkmark)

## Full Documentation
See [GITHUB_ACTION_GUIDE.md](GITHUB_ACTION_GUIDE.md) for complete reference.
