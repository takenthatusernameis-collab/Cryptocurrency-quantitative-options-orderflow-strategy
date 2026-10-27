#!/usr/bin/env python3
import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description='Check controller progress')
    parser.add_argument('--base-sha', required=True)
    parser.add_argument('--head-sha', required=True)
    parser.add_argument('--verified-remote-sha', required=False)
    args = parser.parse_args()
    
    # Check if there are any file changes excluding .github/workflows
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', args.base_sha, args.head_sha],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).stdout.decode().strip()
        )
        changed_files = result.stdout.decode().strip().split('\n')
        changed_files = [f for f in changed_files if f and not f.startswith('.github/workflows/')]
        if changed_files:
            sys.exit(0)  # Has progress
        sys.exit(1)  # No meaningful progress
    except Exception as e:
        # If we can't determine, assume no progress
        sys.exit(1)


if __name__ == '__main__':
    main()
