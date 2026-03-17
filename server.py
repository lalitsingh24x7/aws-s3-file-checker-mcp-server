"""AWS S3 File Checker MCP Server.

Provides an MCP tool to check whether a file (object) exists in an AWS S3 bucket.
"""

import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ParamValidationError
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="aws-s3-file-checker",
    instructions=(
        "Use this server to check whether files (objects) exist in AWS S3 buckets. "
        "AWS credentials must be configured via environment variables "
        "(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) or an IAM role."
    ),
)


def _get_s3_client():
    """Return a boto3 S3 client, optionally using a custom endpoint."""
    kwargs = {}
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if region:
        kwargs["region_name"] = region
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    return boto3.client("s3", **kwargs)


@mcp.tool(
    name="check_file_exists",
    description=(
        "Check whether a file (object) exists in an AWS S3 bucket. "
        "Returns a message indicating whether the file exists or not."
    ),
)
def check_file_exists(bucket_name: str, file_key: str) -> str:
    """Check if a file exists in an S3 bucket.

    Args:
        bucket_name: The name of the S3 bucket.
        file_key: The key (path) of the file within the bucket.

    Returns:
        A human-readable message indicating whether the file exists.
    """
    if not bucket_name or not bucket_name.strip():
        return "Error: bucket_name must not be empty."
    if not file_key or not file_key.strip():
        return "Error: file_key must not be empty."

    try:
        client = _get_s3_client()
        client.head_object(Bucket=bucket_name, Key=file_key)
        return f"File '{file_key}' exists in bucket '{bucket_name}'."
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchKey"):
            return f"File '{file_key}' does not exist in bucket '{bucket_name}'."
        if error_code in ("403", "AccessDenied"):
            return (
                f"Access denied when checking '{file_key}' in bucket '{bucket_name}'. "
                "Verify that your AWS credentials have the required s3:GetObject / "
                "s3:HeadObject permissions."
            )
        if error_code == "NoSuchBucket":
            return f"Bucket '{bucket_name}' does not exist."
        return f"AWS error ({error_code}): {exc}"
    except NoCredentialsError:
        return (
            "Error: AWS credentials not found. Configure AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY environment variables, or attach an IAM role."
        )
    except ParamValidationError as exc:
        return f"Error: Invalid parameters — {exc}"


if __name__ == "__main__":
    mcp.run()
