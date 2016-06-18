"""Interface with git locally and remotely."""

import re

from subprocess import CalledProcessError, check_output, STDOUT

RE_REMOTE = re.compile(r'^(?P<sha>[0-9a-f]{5,40})\trefs/(?P<kind>\w+)/(?P<name>[\w./-]+)$', re.MULTILINE)


class GitError(Exception):
    """Raised if git exits non-zero."""

    def __init__(self, message, output):
        """Constructor."""
        self.message = message
        self.output = output
        super(GitError, self).__init__(message, output)


def get_root(directory):
    """Get root directory of the local git repo from any subdirectory within it.

    :raise GitError: If git command fails (dir not a git repo?).

    :param str directory: Subdirectory in the local repo.

    :return: Root directory of repository.
    :rtype: str
    """
    command = ['git', 'rev-parse', '--show-toplevel']
    try:
        output = check_output(command, cwd=directory, stderr=STDOUT).decode('ascii')
    except CalledProcessError as exc:
        raise GitError('Git failed to list remote refs.', exc.output.decode('ascii'))
    return output.strip()


def list_remote(local_root):
    """Get remote branch/tag latest SHAs.

    :raise GitError: When git ls-remote fails.

    :param str local_root: Local path to git root directory.

    :return: List of tuples containing strings. Each tuple is sha, name, kind.
    :rtype: list
    """
    command = ['git', 'ls-remote', '-h', '-t']
    try:
        output = check_output(command, cwd=local_root, stderr=STDOUT).decode('ascii')
    except CalledProcessError as exc:
        raise GitError('Git failed to list remote refs.', exc.output.decode('ascii'))

    # Parse output.
    parsed = [m.groupdict() for m in RE_REMOTE.finditer(output)]
    if not parsed:
        return parsed

    return [[i['sha'], i['name'], i['kind']] for i in parsed]
