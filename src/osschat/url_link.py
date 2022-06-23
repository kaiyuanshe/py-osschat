from __future__ import annotations
from dataclasses import dataclass
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Issue import Issue
from github.IssueComment import IssueComment
from github.NamedUser import NamedUser

from wechaty_puppet.schemas.url_link import UrlLinkPayload


def get_user_thumbnail_url(user_id: str) -> str:
    user = NamedUser     

class GithubInfo:
    def __init__(self, token: str):
        self._github = Github(login_or_token=token)
    
    def get_short_description_of_pr(self, repo_name, pr_id: int) -> UrlLinkPayload:
        repo: Repository = self._github.get_repo(repo_name)
        pull_request: PullRequest = repo.get_pull(pr_id)
        payload = UrlLinkPayload(
            url=pull_request.url,
            title=pull_request.title,
            description=pull_request.body,
            thumbnailUrl=pull_request.user.avatar_url
        )
        return payload
     