#! /usr/bin/env python
import argparse
import logging
import os
import re
import subprocess
from typing import Sequence

logger = logging.getLogger('missing')


class Missing:

    def __init__(self, exclude: Sequence[str]):
        if not (isinstance(exclude, list) or isinstance(exclude, tuple)):
            raise TypeError('exclude should be list or tuple')
        for path in exclude:
            if os.path.exists(path) and not os.path.isdir(path):
                raise TypeError(f"exclude should only contain directories, found file {path}")

        files = [os.path.normpath(path) for path in self._list_files()]
        logger.debug(f"{files=}")

        exclude = [os.path.normpath(path) for path in exclude]
        logger.debug(f"{exclude=}")

        files_included = set()
        for file in files:
            if all([not file.startswith(e) for e in exclude]):
                files_included.add(file)
        logger.debug(f"{files_included=}")

        self.files = files_included

    def run(self) -> int:
        """Return 1 if there are missing files, otherwise 0"""
        is_failed = 0

        for file in self.files:
            basedir = os.path.dirname(file)

            if basedir in ('', '.'):
                continue

            init_py = os.path.join(basedir, '__init__.py')
            if not os.path.exists(init_py):
                is_failed = True
                # create the __init__.py
                with open(init_py, 'w'):
                    logger.warning(f'create file: {init_py}')

        return is_failed

    @staticmethod
    def _list_files():
        pattern = re.compile(r'^.*?\.py$')

        files = subprocess.check_output(
            ['git', 'ls-files', '-z'],
            encoding='utf-8',
        ).rstrip('\0').split('\0')

        files += (
            subprocess.check_output(
                ['git', 'ls-files', '-o', '--exclude-standard', '-z'],
                encoding='utf-8',
            )
            .rstrip('\0')
            .split('\0')
        )

        return set(
            os.path.normpath(file)
            for file in files
            if pattern.match(os.path.basename(file))
        )


def main() -> int:
    parser = argparse.ArgumentParser(description='Find the missing but necessary files')
    parser.add_argument('-e', '--exclude', nargs='*', help='exclude the file or folder')
    parser.add_argument(
        '-q', '--quite', action='store_true', default=False, help='disable all log'
    )

    args = parser.parse_args()

    if args.quite:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            logger.addHandler(handler)

    missing = Missing(args.exclude or [])
    return missing.run()


if __name__ == '__main__':
    exit(main())
