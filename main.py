import logging
from pathlib import Path

import boto3
from botocore.config import Config

PROCESSING_BUCKET = "rpmi-processing-us-east-1-production"
STATIC_BUCKET = "rpmi-static-us-east-1"
ARCHIVE_BUCKET = "rpmi-archive-us-east-1-production"
SHORT_TERM_ARCHIVE_BUCKET = "rpmi-short-term-archive-us-east-1-production"
DELIVERABLE_ARCHIVE_BUCKET = "rpmi-deliverable-archive-us-east-1-production"
PCM_ARCHIVE_BUCKET = "rpmi-pcm-archive-us-east-1-production"

config = Config(
    retries={"total_max_attempts": 5, "mode": "adaptive"},
    max_pool_connections=50,
)
session = boto3.session.Session()
s3 = session.client("s3", config=config)


def main() -> None:
    """
    """
    pass


if __name__ == "__main__":
    main()
