import re

from simple_webpack.utils import get_version, unixify


def test_unixify():
    assert unixify('\\') == '/'


class TestVersionUtils(object):

    def test_development(self):
        ver_tuple = (1, 2, 0, 'alpha', 0)
        # This will return a different result when it's run within or outside
        # of a git clone: 1.4.devYYYYMMDDHHMMSS or 1.4.
        ver_string = get_version(ver_tuple)
        assert re.search(r'1\.2(\.dev[0-9]+)?', ver_string)
