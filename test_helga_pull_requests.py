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
    resp = pull_requests('', '', 'me', '', [
        ('', '', 'bar', '10'),
        ('', 'baz', 'qux', '42'),
    ])
    assert resp == 'me might be talking about pull request: https://github.com/baz/qux/pull/42'


@patch('helga_pull_requests.settings')
def test_uses_default_account(settings):
    settings.PULL_REQUESTS_DEFAULT_ACCOUNT = 'foo'
    resp = pull_requests('', '', 'me', '', [
        ('', '', 'bar', '10'),
        ('', 'baz', 'qux', '42'),
    ])
    assert resp == ('me might be talking about pull request: '
                    'https://github.com/foo/bar/pull/10, '
                    'https://github.com/baz/qux/pull/42')
