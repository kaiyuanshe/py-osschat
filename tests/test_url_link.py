import pytest
from github.Repository import Repository

from osschat.url_link import GithubUrlLink 


@pytest.fixture
def github_url_link() -> GithubUrlLink:
    return GithubUrlLink(None)


def test_pr_payload(github_url_link: GithubUrlLink):
    payload = github_url_link.get_pr_payload('wechaty/python-wechaty', pr_id=331)
    assert payload.url == 'https://github.com/wechaty/python-wechaty/pull/331'
    assert payload.title == 'improve the qrcode printed at terminal'

def test_pr_comment_payload(github_url_link: GithubUrlLink):
    pr_id, comment_id = 4, 594452486

    payload = github_url_link.get_pr_comment_payload('wechaty/python-wechaty', pr_id=pr_id, comment_id=comment_id)
    assert payload.title == 'add quick test'
    assert payload.url == f'https://github.com/wechaty/python-wechaty/pull/{pr_id}#issuecomment-{comment_id}'
    assert 'Great work' in payload.description

def test_issue_payload(github_url_link: GithubUrlLink):
    payload = github_url_link.get_issue_payload('wechaty/python-wechaty', issue_id=5)

    assert payload.url == 'https://github.com/wechaty/python-wechaty/issues/5'
    assert payload.title == 'disucss the structure of starting python-wechaty'
    assert 'code structure' in payload.description


def test_issue_comment_payload(github_url_link: GithubUrlLink):
    payload = github_url_link.get_issue_comment_payload('wechaty/python-wechaty', issue_id=5, comment_id=596385964)

    assert 'Recently, I wrote async/await code in python' in payload.description