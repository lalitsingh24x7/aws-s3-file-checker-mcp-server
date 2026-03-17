# aws-s3-file-checker-mcp-server

A simple [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that checks whether a file (object) exists in an AWS S3 bucket.

## Features

- **`check_file_exists`** tool – given a bucket name and a file key, reports whether the object is present in S3.
- Friendly, human-readable error messages for common failure modes (missing credentials, access denied, non-existent bucket, etc.).
- Supports a custom `AWS_ENDPOINT_URL` for local testing with [LocalStack](https://localstack.cloud/) or [MinIO](https://min.io/).

## Requirements

- Python 3.10+
- AWS credentials with at minimum the `s3:HeadObject` (or `s3:GetObject`) permission on the target bucket.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure AWS credentials

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Alternatively, export the variables directly or rely on an IAM role attached to your compute environment:

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_REGION=us-east-1          # optional; boto3 will use its default region when not set
```

### 3. Run the server

```bash
python server.py
```

The server communicates over **stdio** by default (compatible with Claude Desktop, Cursor, and other MCP-aware clients).

## MCP Client Configuration

Add the following to your MCP client's configuration (e.g. `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aws-s3-file-checker": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "AWS_ACCESS_KEY_ID": "your_access_key_id",
        "AWS_SECRET_ACCESS_KEY": "your_secret_access_key",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

## Available Tool

### `check_file_exists`

| Parameter     | Type   | Description                                    |
|---------------|--------|------------------------------------------------|
| `bucket_name` | string | The name of the S3 bucket                      |
| `file_key`    | string | The key (path) of the object within the bucket |

**Example response (file exists):**

```
File 'reports/2024-01.csv' exists in bucket 'my-data-bucket'.
```

**Example response (file not found):**

```
File 'reports/2024-01.csv' does not exist in bucket 'my-data-bucket'.
```

## Development

### Running tests

```bash
pip install -r requirements.txt
pip install "moto[s3]>=5.0.0" pytest pytest-asyncio
pytest tests/ -v
```

### Local S3 with LocalStack

```bash
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
python server.py
```
