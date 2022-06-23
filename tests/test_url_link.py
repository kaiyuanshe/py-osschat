from osschat.url_link import GithubInfo


def test_payload():
    github_info = GithubInfo(None)
    payload = github_info.get_short_description_of_pr('wechaty/python-wechaty', pr_id=331)
    assert payload.title == 'improve the qrcode printed at terminal'
    