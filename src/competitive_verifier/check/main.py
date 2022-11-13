import argparse
import pathlib
import sys
from collections import Counter
from functools import reduce
from logging import getLogger
from typing import Iterable, Optional

from competitive_verifier.arg import add_result_json_argument
from competitive_verifier.log import configure_stderr_logging
from competitive_verifier.models import ResultStatus, VerifyCommandResult

logger = getLogger(__name__)


def merge(results: Iterable[VerifyCommandResult]) -> VerifyCommandResult:
    return reduce(lambda a, b: a.merge(b), results)


def run_impl(*result_json: pathlib.Path) -> bool:
    configure_stderr_logging()

    result = merge(map(VerifyCommandResult.parse_file, result_json))

    counter = Counter(
        r.status for fr in result.files.values() for r in fr.verifications
    )
    failure_count = counter.get(ResultStatus.FAILURE, 0)
    if failure_count > 0:
        logger.error("Failure test count: %d", failure_count)
        return False
    return True


def run(args: argparse.Namespace) -> bool:
    return run_impl(*args.result_json)


def argument(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    add_result_json_argument(parser)
    return parser


def main(args: Optional[list[str]] = None) -> None:
    try:
        parsed = argument(argparse.ArgumentParser()).parse_args(args)
        if not run(parsed):
            sys.exit(1)
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(2)


if __name__ == "__main__":
    main()