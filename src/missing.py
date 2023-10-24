#! /usr/bin/env python
import argparse
import logging
import os
import re
import subprocess
from functools import lru_cache
from typing import Optional

logger = logging.getLogger('missing')


class Missing:
    RE_TEST_PY = re.compile(r'^.*?\.py$')

    def __init__(self, exclude):
        if not (isinstance(exclude, list) or isinstance(exclude, tuple)):
            raise TypeError('exclude should be list or tuple')

        self._tracked_files = self._list_files_obey_gitignore()
        logger.debug('Tracked files: %r', self._tracked_files)

        # append .git to exclude folder
        exclude = {'.git', *exclude}

        # normalize a pathname by collapsing redundant separators
        self._exclude = [os.path.normpath(path) for path in exclude]

    def run(self) -> int:
        return int(self._find_for_unittest())

    @lru_cache(maxsize=None)
    def _check_init_py_exists(self, path: str) -> bool:
        """check the __init__.py exists on the current path and parent path"""
        basedir = os.path.dirname(path)

        if basedir in ('', '.'):
            return False

        # check the parent folder
        fail = self._check_init_py_exists(basedir)

        # check the current __init__ exists or not
        init_py = f'{basedir}/__init__.py'
        if not os.path.exists(init_py):
            fail = True

            # create the __init__.py
            with open(init_py, 'w'):
                logger.warning('create file: {}'.format(init_py))
        return fail

    def _find_for_unittest(self, basedir: Optional[str] = None) -> bool:
        """the unittest find the test*.py only for the regular package"""
        fail = False
        init_run = False

        if basedir is None:
            basedir = '.'
            init_run = True

        for filename in os.listdir(basedir):
            path = os.path.normpath(f'{basedir}/{filename}')
            if path in self._exclude:
                # skip the explicitly excluded path
                logger.debug('exclude: %r', path)
                continue

            if os.path.isdir(path):
                if self._find_for_unittest(path):
                    fail = True
            elif self.RE_TEST_PY.match(filename):
                if self._is_tracked(path):
                    logger.debug('check: %r', path)
                    if self._check_init_py_exists(path):
                        fail = True
                else:
                    logger.debug('untracked: %r', path)
            else:
                logger.debug('no_match: %r', path)

        if init_run and fail:
            logger.warning('found missing __init__.py for unittest')

        return fail

    def _is_tracked(self, path):
        if self._tracked_files is None:
            return True
        return path in self._tracked_files

    def _list_files_obey_gitignore(self):
        # list committed files
        tracked_files = (
            subprocess.check_output(
                ['git', 'ls-files', '-z'],
                encoding='utf-8',
            )
            .rstrip('\0')
            .split('\0')
        )

        # list untracked files
        tracked_files += (
            subprocess.check_output(
                ['git', 'ls-files', '-o', '--exclude-standard', '-z'],
                encoding='utf-8',
            )
            .rstrip('\0')
            .split('\0')
        )
        return set(
            [
                os.path.normpath(tracked_file)
                for tracked_file in tracked_files
                if self.RE_TEST_PY.match(os.path.basename(tracked_file))
            ]
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
