from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
from github import Github
from github.Repository import Repository

from github.PullRequest import PullRequest
from github.PullRequestComment import PullRequestComment

from github.Issue import Issue
from github.IssueComment import IssueComment

from github.NamedUser import NamedUser

from wechaty_puppet.schemas.url_link import UrlLinkPayload


class GithubUrlLink:
    def __init__(self, token: str):
        self._github = Github(login_or_token=token)
        self._repositories: Dict[str, Repository] = {}

    def get_repo(self, repo_name: str) -> Repository:
        if repo_name in self._repositories:
            return self._repositories[repo_name]
        
        repo = self._github.get_repo(repo_name)
        self._repositories[repo_name] = repo
        return repo
    
    def get_pr_payload(self, repo_name, pr_id: int) -> UrlLinkPayload:
        repo: Repository = self.get_repo(repo_name)
        pull_request: PullRequest = repo.get_pull(pr_id)
        payload = UrlLinkPayload(
            url=pull_request.html_url,
            title=pull_request.title,
            description=pull_request.body,
            thumbnailUrl=pull_request.user.avatar_url
        )
        return payload
    
    def get_pr_comment_payload(self, repo_name: str, pr_id: int, comment_id: int, comment_type: str = 'issue') -> UrlLinkPayload:
        repo: Repository = self.get_repo(repo_name)
        pull_request: PullRequest = repo.get_pull(pr_id)
        if comment_type == 'issue':
            comment: PullRequestComment = pull_request.get_issue_comment(comment_id)
        else:
            comment: PullRequestComment = pull_request.get_review_comment(comment_id)

        payload = UrlLinkPayload(
            url=comment.html_url,
            title=pull_request.title,
            description=comment.body,
            thumbnailUrl=comment.user.avatar_url
        )
        return payload  

    def get_issue_payload(self, repo_name: str, issue_id: int) -> UrlLinkPayload:
        repo: Repository = self.get_repo(repo_name)
        issue: Issue = repo.get_issue(issue_id)
        payload = UrlLinkPayload(
            url=issue.html_url,
            title=issue.title,
            description=issue.body,
            thumbnailUrl=issue.user.avatar_url
        )
        return payload  
    
    def get_issue_comment_payload(self, repo_name, issue_id: int, comment_id: int) -> UrlLinkPayload:
        repo: Repository = self.get_repo(repo_name)
        issue: Issue = repo.get_issue(issue_id)
        comment: IssueComment = issue.get_comment(comment_id)

        payload = UrlLinkPayload(
            url=comment.html_url,
            title=issue.title,
            description=comment.body,
            thumbnailUrl=comment.user.avatar_url
        )
        return payload  
    