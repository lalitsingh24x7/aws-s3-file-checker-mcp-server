"""
Simple MCP Server for checking S3 file existence.
"""

import boto3
from botocore.exceptions import ClientError
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("s3-file-checker")


@mcp.tool()
def check_file_exists(bucket_name: str, file_path: str) -> bool:
    """
    Check if a file exists in an S3 bucket.
    
    Args:
        bucket_name: The name of the S3 bucket
        file_path: The path/key of the file in the bucket (e.g., "folder/subfolder/file.txt")
    
    Returns:
        True if the file exists, False otherwise
    """
    s3_client = boto3.client('s3')
    
    try:
        s3_client.head_object(Bucket=bucket_name, Key=file_path)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        # Re-raise for other errors (permissions, etc.)
        raise


if __name__ == "__main__":
    mcp.run()
