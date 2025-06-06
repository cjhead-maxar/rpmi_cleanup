import argparse
import logging
import shutil
import tarfile
from enum import Enum
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


LOG_FILE = Path("logs/cleanup.log")

class Bucket(Enum):
    # PROCESSING = "rpmi-processing-us-east-1-production"
    # STATIC = "rpmi-static-us-east-1"
    ARCHIVE = "rpmi-archive-us-east-1-production"
    SHORT_TERM_ARCHIVE = "rpmi-short-term-archive-us-east-1-production"
    DELIVERABLE_ARCHIVE = "rpmi-deliverable-archive-us-east-1-production"
    PCM_ARCHIVE = "rpmi-pcm-archive-us-east-1-production"


LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

config = Config(
    retries={"total_max_attempts": 5, "mode": "adaptive"},
    max_pool_connections=50,
)
session = boto3.session.Session()
s3 = session.client("s3", config=config)


def download_granule_from_aws(bucket: Bucket, prefix: str, dest: Path) -> None:
    """
    Downloads granule specific files from AWS bucket.

    Parameters
    ---------
    bucket : Bucket
        AWS bucket
    granule : string
        The granule for which to download files from AWS.
    """
    bucket = bucket.value
    res = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    try:
        for item in res["Contents"]:
            key = item["Key"]
            filename = dest / key
            if filename.exists():
                continue

            parent = filename.parents[0]
            if not parent.exists():
                parent.mkdir(parents=True)

            try:
                logger.info(f"Downloading {bucket}/{key}")
                s3.download_file(Bucket=bucket, Key=key, Filename=filename)

            except ClientError as e:
                if e.response["Error"]["Code"] == "InvalidObjectState":
                    logger.error(
                        f"Cannot access {key}: "
                        f"Object is in {item['StorageClass']}"
                    )
                else:
                    raise

    except KeyError:
        logger.warning(f"{prefix} can't be found in {bucket}")


def tar_archive(dest: Path, granule: str) -> None:
    """
    Creates a tar file with the selected granule's archive files.

    Parameters
    ----------
    dest : Path
        The top level destination directory for the archived files.
    granule : string
        The granule for which to download files from AWS.
    """
    tar_dir = dest / granule
    tar_file = tar_dir.with_suffix(".tar")

    logger.info(f"Tarring {granule}...")
    with tarfile.open(tar_file, "w") as tar:
        tar.add(tar_dir, recursive=True)

    logger.info(f"Tar finished. Cleaning up {granule} directory...")
    shutil.rmtree(tar_dir)


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
        dest = Path(args.dest)
    if args.granules:
        granules.extend(args.granules)
    if args.granule_list:
        with args.granule_list as granule_list:
            granules.extend(granule_list.read().splitlines())

    for granule in granules:
        try:
            for bucket in Bucket:
                download_granule_from_aws(
                    bucket, f"{granule}/", dest,
                )
            tar_archive(dest, granule)
        except ClientError as e:
            logger.error(
                "Botocore client error. "
                "Try updating AWS credentials and try again"
            )
            print(e)

if __name__ == "__main__":
    main()
