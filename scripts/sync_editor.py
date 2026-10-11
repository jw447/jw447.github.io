"""Synchronize a clean review checkout with GitHub and main before editing."""
from pathlib import Path
import subprocess
import re

BRANCH = 'website-redesign'

def synchronize(root):
    def git(*args, check=True):
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, timeout=60)
        if check and result.returncode:
            raise RuntimeError('Git sync failed: ' + result.stderr.strip())
        return result
    if Path(git('rev-parse', '--show-toplevel').stdout.strip()).resolve() != root.resolve():
        raise RuntimeError('Run the editor from the website repository.')
    remote = git('remote', 'get-url', 'origin').stdout.strip()
    if not re.fullmatch(r'(?:https://github\.com/|git@github\.com:)[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?', remote):
        raise RuntimeError('Set origin to your GitHub repository before opening the editor.')
    if git('status', '--porcelain').stdout.strip():
        raise RuntimeError('Commit or save your local changes before startup can pull. Nothing was overwritten.')
    git('fetch', 'origin', '--prune')
    if git('show-ref', '--verify', '--quiet', 'refs/heads/' + BRANCH, check=False).returncode == 0:
        git('switch', BRANCH)
        if git('show-ref', '--verify', '--quiet', 'refs/remotes/origin/' + BRANCH, check=False).returncode == 0:
            git('merge', '--ff-only', 'origin/' + BRANCH)
    elif git('show-ref', '--verify', '--quiet', 'refs/remotes/origin/' + BRANCH, check=False).returncode == 0:
        git('switch', '--track', '-c', BRANCH, 'origin/' + BRANCH)
    else:
        git('switch', '-c', BRANCH, 'origin/main')
    result = git('merge', '--no-edit', 'origin/main', check=False)
    if result.returncode:
        if git('rev-parse', '--verify', 'MERGE_HEAD', check=False).returncode == 0:
            git('merge', '--abort')
        raise RuntimeError('Could not merge the latest main into website-redesign. Resolve the branch differences manually, then reopen the editor. ' + result.stderr.strip())
    return 'Latest main and website-redesign loaded. Publishing targets website-redesign.'

if __name__ == '__main__':
    import sys
    try: print(synchronize(Path(__file__).resolve().parents[1]), flush=True)
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr); raise SystemExit(1)
