"""Tests for the AWS S3 File Checker MCP server."""

import sys
import os

import boto3
import pytest
from moto import mock_aws
from unittest.mock import patch

# Ensure the project root is on the path so we can import server.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from server import check_file_exists, _get_s3_client  # noqa: E402


BUCKET = "test-bucket"
EXISTING_KEY = "folder/existing-file.txt"
MISSING_KEY = "folder/missing-file.txt"


@pytest.fixture(autouse=True)
def aws_credentials():
    """Set fake AWS credentials so boto3 does not reach the real AWS."""
    with patch.dict(
        os.environ,
        {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
            "AWS_DEFAULT_REGION": "us-east-1",
        },
    ):
        yield


@pytest.fixture()
def s3_with_bucket():
    """Create a mocked S3 bucket and upload a test object."""
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        client.put_object(Bucket=BUCKET, Key=EXISTING_KEY, Body=b"hello")
        yield client


# ---------------------------------------------------------------------------
# check_file_exists tool tests
# ---------------------------------------------------------------------------

class TestCheckFileExists:
    def test_file_exists(self, s3_with_bucket):
        result = check_file_exists(BUCKET, EXISTING_KEY)
        assert f"'{EXISTING_KEY}' exists in bucket '{BUCKET}'" in result

    def test_file_does_not_exist(self, s3_with_bucket):
        result = check_file_exists(BUCKET, MISSING_KEY)
        assert "does not exist" in result
        assert MISSING_KEY in result

    def test_bucket_does_not_exist(self, s3_with_bucket):
        result = check_file_exists("nonexistent-bucket", EXISTING_KEY)
        assert "does not exist" in result or "NoSuchBucket" in result or "AccessDenied" in result

    def test_empty_bucket_name(self, s3_with_bucket):
        result = check_file_exists("", EXISTING_KEY)
        assert "Error" in result
        assert "bucket_name" in result

    def test_whitespace_bucket_name(self, s3_with_bucket):
        result = check_file_exists("   ", EXISTING_KEY)
        assert "Error" in result
        assert "bucket_name" in result

    def test_empty_file_key(self, s3_with_bucket):
        result = check_file_exists(BUCKET, "")
        assert "Error" in result
        assert "file_key" in result

    def test_whitespace_file_key(self, s3_with_bucket):
        result = check_file_exists(BUCKET, "   ")
        assert "Error" in result
        assert "file_key" in result

    def test_no_credentials(self):
        with patch("server._get_s3_client") as mock_client:
            from botocore.exceptions import NoCredentialsError
            mock_client.side_effect = NoCredentialsError()
            result = check_file_exists(BUCKET, EXISTING_KEY)
        assert "credentials" in result.lower()

    def test_returns_string(self, s3_with_bucket):
        result = check_file_exists(BUCKET, EXISTING_KEY)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# _get_s3_client helper tests
# ---------------------------------------------------------------------------

class TestGetS3Client:
    def test_returns_s3_client(self):
        with mock_aws():
            client = _get_s3_client()
            assert client is not None
            assert client.meta.service_model.service_name == "s3"

    def test_uses_aws_region_env(self):
        with patch.dict(os.environ, {"AWS_REGION": "eu-west-1"}, clear=False):
            with mock_aws():
                client = _get_s3_client()
                assert client.meta.region_name == "eu-west-1"

    def test_uses_endpoint_url(self):
        with patch.dict(
            os.environ,
            {"AWS_ENDPOINT_URL": "http://localhost:4566"},
            clear=False,
        ):
            with mock_aws():
                client = _get_s3_client()
                assert client.meta.endpoint_url == "http://localhost:4566"
