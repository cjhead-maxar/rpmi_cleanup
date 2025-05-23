import argparse
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


def main() -> None:
    dest = Path.cwd()
    granules = []

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dest",
        help=(
            "The top level destination directory for the archived files.\n"
            f"Default is {dest}."
        ),
        default=dest,
    )
    parser.add_argument(
        "-g",
        "--granules",
        action="extend",
        nargs="+",
        type=str,
        help="Granule[s] to archive.",
    )
    parser.add_argument(
        "-l",
        "--granule-list",
        type=argparse.FileType("r"),
        help="A text file containing a list of granules to archive.",
    )
    args = parser.parse_args()
    if args.dest:
        dest = args.dest
    if args.granules:
        granules.extend(args.granules)
    if args.granule_list:
        with args.granule_list as granule_list:
            granules.extend(granule_list.read().splitlines())


if __name__ == "__main__":
    main()
