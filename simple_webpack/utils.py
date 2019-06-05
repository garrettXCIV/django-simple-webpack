import json
import os
import subprocess
import sys
from datetime import datetime
from time import sleep

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static

from simple_webpack.exceptions import (
    SimpleWebpackError,
    SimpleWebpackTimeoutError,
    WebpackBundleTrackerError,
)

WEBPACK_STATS_PATH = settings.WEBPACK_STATS_PATH
WS_PATH, WS_FILENAME = os.path.split(WEBPACK_STATS_PATH)
STATICFILES_DIRS = settings.STATICFILES_DIRS


def unixify(path):
    """Convert a DOS style path to Unix style path.

    Args:
        path (str): A windows style path.

    Returns:
        str: A Unix style path.

    """
    return path.replace('\\', '/')


def get_webpack_stats():
    """Get webpack-bundle-tracker output file data.

    Returns:
        dict: The data from webpack-bundle-tracker JSON output file.

    """
    try:
        with open(WEBPACK_STATS_PATH, encoding='utf-8') as ws_file:
            webpack_stats = json.load(ws_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        if isinstance(e, FileNotFoundError):
            err_msg = (
                'The File "{file}" does not exist in the directory:\n'
                '"{path}"\n'
                'Possibly because you haven\'t run Webpack yet,\n'
                'or you don\'t have webpack-bundle-tracker set up in Node.'
            ).format(file=WS_FILENAME, path=WS_PATH)
            raise FileNotFoundError(2, err_msg)
        if isinstance(e, json.decoder.JSONDecodeError):
            err_msg = (
                'The file "{file}" is not a valid JSON file.\n'
                'Try checking that Webpack and webpack-bundle-tracker '
                'are set up in Node\n    and that they run without error.\n'
                '{emsg} at'
            ).format(file=WS_FILENAME, emsg=e.msg)
            raise json.JSONDecodeError(
                err_msg,
                WS_FILENAME,
                e.pos,
            )
    else:
        return webpack_stats


def check_status(webpack_stats, initial_call):
    """Check the status of all webpack bundles.

    Args:
        webpack_stats (dict): The value of get_webpack_stats().
        initial_call (bool): False if check_status() is being called by the
            same function twice in a row, else True.

    Returns:
        bool: True if status == 'done', False if status == 'compiling' and
            initial_call is True.

    """
    status = webpack_stats.get('status')
    if status == 'done':
        return True

    if not status:
        err_msg = (
            '"{file}" is missing top-level member "status"'
        ).format(file=WS_FILENAME)
        raise WebpackBundleTrackerError(err_msg)

    if status == 'error':
        ws_errfile = webpack_stats.get('file', 'Unknown')
        ws_err = webpack_stats.get('error', 'UnknownError')
        ws_errmsg = webpack_stats.get('message', '')
        err_msg = (
            '{error}: {message}\n'
            'File: {file}'
        )
        raise WebpackBundleTrackerError(err_msg.format(
            error=ws_err,
            message=ws_errmsg,
            file=ws_errfile,
        ))

    if status == 'compiling' and initial_call:
        try:
            allow_compiling = settings.WEBPACK_ALLOW_COMPILING
        except AttributeError:
            allow_compiling = False

        if settings.DEBUG and allow_compiling:
            print('Webpack Status: Compiling')
            for i in range(allow_compiling, 0, -1):
                print('Waiting... {}'.format(i), end='\r')
                sleep(1)
            print('Retrying...')
            return False
    if status == 'compiling':
        err_msg = 'Webpack still compiling. Simple Webpack timed out.'
        raise SimpleWebpackTimeoutError(err_msg)

    err_msg = 'Unknown webpack-bundle-tracker status: {}'.format(status)
    raise SimpleWebpackError(err_msg)


def get_all_bundle_paths():
    """Get the paths for all bundles.

    Returns:
        list: The paths of all bundles.

    """
    webpack_stats = get_webpack_stats()
    status_ok = check_status(webpack_stats, True)
    if not status_ok:
        status_ok = check_status(webpack_stats, False)
    if status_ok:
        # Get all bundles.
        bundles = webpack_stats.get('chunks')
        if bundles is None:
            err_msg = 'No bundles found in {file}'.format(file=WS_FILENAME)
            raise SimpleWebpackError(err_msg)
        bundle_paths = []
        for bundle in bundles:
            try:
                # Get the path of the current bundle.
                path = bundles.get(bundle)[0].get('path')
            except IndexError:
                path = False
                bad_bundle = bundle
                break
            else:
                path = unixify(path)
                for dir_ in STATICFILES_DIRS:
                    dir_ = unixify(dir_)
                    if dir_ in path:
                        # Split off the part of path containing
                        # STATICFILES_DIRS then join the resulting list into
                        # a string and prepend STATIC_URL to get the URL path.
                        path = static("".join(path.split(dir_)))
                        # Prepend a forwardslash if there isn't one at the
                        # beginning of the path to make the path relative to
                        # the domain.
                        if path[0] != '/':
                            path = '/' + path

                        bundle_paths.append(path)

        if not path:
            err_msg = (
                'Missing "path" attribute for bundle {bundle}'
            ).format(bundle=bad_bundle)
            raise WebpackBundleTrackerError(err_msg)

        return bundle_paths


def get_bundle_path_by_chunkname(chunk_name):
    """Get the path of a bundle by entry name.

    Args:
        chunk_name (str): The chunk name of a bundle.

    Returns:
        str: A bundle's path.

    """
    webpack_stats = get_webpack_stats()
    status_ok = check_status(webpack_stats, True)
    if not status_ok:
        status_ok = check_status(webpack_stats, False)
    if status_ok:
        bundle = webpack_stats['chunks'].get(chunk_name)[0]
        if bundle is None:
            err_msg = 'Chunk "{chunk_name}" not found in {file}'.format(
                chunk_name=chunk_name,
                file=WS_FILENAME,
            )
            raise SimpleWebpackError(err_msg)
        path = bundle.get('path')
        if path:
            path = unixify(path)
            for dir_ in STATICFILES_DIRS:
                dir_ = unixify(dir_)
                # Split off the part of path containing STATICFILES_DIRS
                # then join the resulting list into string and prepend
                # STATIC_URL to get the URL path.
                if dir_ in path:
                    # Prepend STATIC_URL
                    path = static("".join(path.split(dir_)))
                    # Prepend forwardslash if there isn't one at the
                    # beginning of the path to make it relative to the domain.
                    if path[0] != '/':
                        path = '/' + path
                    return path

        err_msg = (
            'Missing "path" attribute for bundle {bundle}'
        ).format(bundle=chunk_name)
        raise WebpackBundleTrackerError(err_msg)


def get_bundle_path_by_filename(bundle_filename):
    """Get the path of a bundle by filename.

    Args:
        file_name (str): The filename of a bundle.

    Returns:
        str: A bundle's path.

    """
    # FIXME -------------------------
    print('\n\n\nBUNDLE FILENAME {}\n\n\n'.format(bundle_filename))
    # ENDDEBUG ----------------------

    webpack_stats = get_webpack_stats()
    status_ok = check_status(webpack_stats, True)
    if not status_ok:
        status_ok = check_status(webpack_stats, False)
    if status_ok:
        for static_dir in STATICFILES_DIRS:
            static_dir = unixify(static_dir)
            for path, _, files in os.walk(static_dir):
                path = unixify(path)
                if bundle_filename in files and static_dir in path:

                    # FIXME ----------------------------
                    print(
                        'PATH: ',
                        path,
                        '\n\nFILENAME: ',
                        bundle_filename,
                        sep='',
                    )
                    # ENDDEBUG -------------------------

                    # Split off the part of path containing STATICFILES_DIRS
                    # then join the resulting list into string and prepend
                    # STATIC_URL to get the URL path.
                    path = static("".join(path.split(static_dir)))
                    if path[0] != '/':
                        path = '/' + path
                    return path

            err_msg = (
                'The file "{file}" does not exist in any directories '
                'named in STATICFILES_DIRS or their subdirectories.'
            ).format(file=bundle_filename)
            raise ValueError(err_msg)


# All the following version related functions are edited copies
# of Django's source code, which, as of 12/2017, are located at:
# https://github.com/django/django/blob/master/django/utils/version.py

# Private, stable API for detecting the Python version. PYXY means "Python X.Y
# or later". So that third-party apps can use these values, each constant
# should remain as long as the oldest supported django-simple-webpack version
# supports that Python version.
PY36 = sys.version_info >= (3, 6)
PY37 = sys.version_info >= (3, 7)
PY38 = sys.version_info >= (3, 8)
PY39 = sys.version_info >= (3, 9)


def get_version(version=None):
    """Return a PEP 440-compliant version number from VERSION."""
    version = get_complete_version(version)

    # Now build the two parts of the version number:
    # base = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|rc}N - for alpha, beta, and rc releases

    base = get_base_version(version)

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        git_changeset = get_git_commit_timestamp()
        if git_changeset:
            sub = '.dev{}'.format(git_changeset)
        else:
            sub = '.dev'

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
        sub = mapping[version[3]] + str(version[4])

    return base + sub


def get_base_version(version=None):
    """Return base version (X.Y[.Z]) from VERSION."""
    version = get_complete_version(version)
    parts = 2 if version[2] == 0 else 3
    return '.'.join(str(x) for x in version[:parts])


def get_complete_version(version=None):
    """Return a tuple of the django-simple-webpack version.

    Return a tuple of the complete version of django-simple-webpack.
    If version argument is non-empty,
    check for correctness of the tuple provided.
    """
    if version is None:
        from simple_webpack import VERSION as version  # noqa: N811
    else:
        assert len(version) == 5
        assert version[3] in ('alpha', 'beta', 'rc', 'final')
        assert version[4] == 0 if version[3] == 'final' else True

    return version


def get_docs_version(version=None):
    version = get_complete_version(version)
    if version[3] != 'final':
        return 'dev'
    return '{}.{}'.format(version[0], version[1])


def get_git_commit_timestamp():
    """Return a numeric identifier of the latest git commit.

    The result is the UTC timestamp of the commit in YYYYMMDDHHMMSS format.
    This value isn't guaranteed to be unique, but collisions are very unlikely,
    so it's sufficient for generating the development version numbers.
    """
    repo_dir = settings.BASE_DIR
    timestamp = subprocess.check_output(
        'git log --pretty=format:%ct --quiet -1 HEAD',
        cwd=repo_dir,
        universal_newlines=True,
    )
    try:
        timestamp = datetime.utcfromtimestamp(int(timestamp))
    except ValueError:
        return None
    return timestamp.strftime('%Y%m%d%H%M%S')
