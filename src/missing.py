#! /usr/bin/env python
import argparse
import logging
import os
import re
from typing import Optional

logger = logging.getLogger('missing')

class Missing:
    RE_TEST_PY = re.compile(r'test.*?\.py')

    def __init__(self, exclude):
        # normalize a pathname by collapsing redundant separators
        self._exclude = [os.path.normpath(path) for path in exclude]

    def run(self) -> int:
        fail = 0

        if self._find_for_unittest():
            fail = 1

        return fail

    def _check_init_py_exists(self, path: str) -> bool:
        fail = False
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
            with open(init_py, 'w') as fd:
                logger.info('create file: {}'.format(init_py))

        return fail

    def _find_for_unittest(self, basedir: Optional[str] = None) -> bool:
        '''the unittest find the test*.py only for the regular package'''
        fail = False

        if basedir is None:
            basedir = '.'

        for filename in os.listdir(basedir):
            path = os.path.normpath(f'{basedir}/{filename}')
            if path in self._exclude:
                # skip the explicitly excluded path
                continue

            if os.path.isdir(path):
                if self._find_for_unittest(path):
                    fail = True
            elif self.RE_TEST_PY.match(filename):
                if self._check_init_py_exists(path):
                    fail = True

        return fail


def main() -> int:
    parser = argparse.ArgumentParser(description='Find the missing but necessary files')
    parser.add_argument('-e', '--exclude', type=list, default=['.git'], help='exclude the file or folder')
    args = parser.parse_args()

    missing = Missing(args.exclude)
    return missing.run()

if __name__ == '__main__':
    exit(main())
