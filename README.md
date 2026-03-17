# S3 File Checker MCP Server

A simple MCP server that checks if a file exists in an AWS S3 bucket.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure AWS credentials (one of these methods):
   - Set environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
   - Use AWS CLI: `aws configure`
   - Use IAM roles (for EC2/Lambda)

## Running the Server

```bash
python server.py
```

## MCP Configuration

Add this to your MCP client configuration (e.g., VS Code settings):

```json
{
  "mcpServers": {
    "s3-file-checker": {
      "command": "python",
      "args": ["path/to/server.py"]
    }
  }
}
```

## Tool

### check_file_exists

Checks if a file exists in an S3 bucket.

**Parameters:**
- `bucket_name` (string): The name of the S3 bucket
- `file_path` (string): The path/key of the file in the bucket

**Returns:**
- `true` if the file exists
- `false` if the file does not exist
