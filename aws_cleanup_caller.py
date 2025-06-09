import argparse
import concurrent.futures
import logging
import subprocess
from pathlib import Path

LOG_FILE = Path("logs/aws_cleanup.log")

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def run_shell_script(granule: str) -> None:
    """
    Runs the aws_granule_cleanup shell script.

    Parameters
    ----------
    granule : str
        The granule to be cleaned.
    """
    try:
        result = subprocess.run(
            ["./aws_granule_cleanup.sh", granule],
        )
        logger.info(result)
    except subprocess.CalledProcessError as e:
        logger.error(f"Outut for {granule}:\n{result.stdout}")


def main() -> None:
    granules = []

    parser = argparse.ArgumentParser()
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
    if args.granules:
        granules.extend(args.granules)
    if args.granule_list:
        with args.granule_list as granule_list:
            granules.extend(granule_list.read().splitlines())

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(run_shell_script, granules)


if __name__ == "__main__":
    main()
