#! /usr/bin/env python
import argparse


class Missing:
    def __init__(self, pattern, exclude=[]):
        self._pattern = pattern
        self._exclude = exclude

    def run(self) -> int:
        fail = 0
        return fail


def main() -> int:
    parser = argparse.ArgumentParser(description='Find the missing but necessary files')
    parser.add_argument(
        '-p',
        '--pattern',
        type=list,
        default=[r'test.*?\.py'],
        help='search the file pattern which should contains __init__.py',
    )
    parser.add_argument('-e', '--exclude', type=list, default=['.git'], help='exclude the file or folder')
    args = parser.parse_args()

    missing = Missing(args.pattern, exclude=args.exclude)
    return missing.run()

if __name__ == '__main__':
    exit(main())
