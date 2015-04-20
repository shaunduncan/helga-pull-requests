import re

from mock import patch

from helga_pull_requests import pull_requests


def test_simple_match():
    resp = pull_requests('', '', 'me', '', [('', 'foo', 'bar', '10')])
    assert resp == 'me might be talking about pull request: https://github.com/foo/bar/pull/10'


def test_multi_match():
    resp = pull_requests('', '', 'me', '', [
        ('', 'foo', 'bar', '10'),
        ('', 'baz', 'qux', '42'),
    ])
    assert resp == ('me might be talking about pull request: '
                    'https://github.com/foo/bar/pull/10, '
                    'https://github.com/baz/qux/pull/42')


def test_returns_none_with_no_matches():
    assert pull_requests('', '', '', '', []) is None


@patch('helga_pull_requests.settings')
def test_ignores_match_without_default(settings):
    settings.PULL_REQUESTS_DEFAULT_ACCOUNT = ''
    del settings.PULL_REQUESTS_GITHUB_HOST

    resp = pull_requests('', '', 'me', '', [
        ('', '', 'bar', '10'),
        ('', 'baz', 'qux', '42'),
    ])
    assert resp == 'me might be talking about pull request: https://github.com/baz/qux/pull/42'


@patch('helga_pull_requests.settings')
def test_uses_default_account(settings):
    settings.PULL_REQUESTS_DEFAULT_ACCOUNT = 'foo'
    del settings.PULL_REQUESTS_GITHUB_HOST

    resp = pull_requests('', '', 'me', '', [
        ('', '', 'bar', '10'),
        ('', 'baz', 'qux', '42'),
    ])
    assert resp == ('me might be talking about pull request: '
                    'https://github.com/foo/bar/pull/10, '
                    'https://github.com/baz/qux/pull/42')


@patch('helga_pull_requests.settings')
def test_uses_nondefault_github_url(settings):
    settings.PULL_REQUESTS_DEFAULT_ACCOUNT = ''
    settings.PULL_REQUESTS_GITHUB_HOST = 'http://my_github.com'

    resp = pull_requests('', '', 'me', '', [
        ('', 'foo', 'bar', '10'),
    ])
    assert resp == ('me might be talking about pull request: '
                    'http://my_github.com/foo/bar/pull/10')


def test_match_regex():
    plugin_cls = pull_requests._plugins[0]
    expectations = {
        'foo-pr1': ('', '', 'foo', '1'),
        'foo-bar-pr1': ('', '', 'foo-bar', '1'),
        'foo/bar-pr1': ('foo/', 'foo', 'bar', '1'),
        'foo/bar-baz-pr1': ('foo/', 'foo', 'bar-baz', '1'),
        'and a long thing foo/bar-pr1': ('foo/', 'foo', 'bar', '1'),
        'extra-chars.in_here-pr1': ('', '', 'extra-chars.in_here', '1'),
    }

    for repo, expected in expectations.iteritems():
        assert re.findall(plugin_cls.pattern, repo)[0] == expected


def test_extended_regex():
    plugin_cls = pull_requests._plugins[1]
    msg = 'shaunduncan/helga-pull-requests/pull/2'
    res = ('shaunduncan/', 'shaunduncan', 'helga-pull-requests', '2')
    assert re.findall(plugin_cls.pattern, msg)[0] == res

    msg = 'https://github.com/shaunduncan/helga-pull-requests/pull/2'
    assert re.findall(plugin_cls.pattern, msg) == []

    plugin_cls = pull_requests._plugins[2]
    msg = 'this is a test shaunduncan/helga-pull-requests/pull/2'
    res = ('shaunduncan/', 'shaunduncan', 'helga-pull-requests', '2')
    assert re.findall(plugin_cls.pattern, msg)[0] == res

    msg = 'this is a test https://github.com/shaunduncan/helga-pull-requests/pull/2'
    assert re.findall(plugin_cls.pattern, msg) == []
