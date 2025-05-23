import logging
from enum import Enum
from pathlib import Path

import boto3
from botocore.config import Config


class Bucket(Enum):
    PROCESSING = "rpmi-processing-us-east-1-production"
    STATIC = "rpmi-static-us-east-1"
    ARCHIVE = "rpmi-archive-us-east-1-production"
    SHORT_TERM_ARCHIVE = "rpmi-short-term-archive-us-east-1-production"
    DELIVERABLE_ARCHIVE = "rpmi-deliverable-archive-us-east-1-production"
    PCM_ARCHIVE = "rpmi-pcm-archive-us-east-1-production"


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
