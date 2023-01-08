from __future__ import annotations

import asyncio
from typing import Optional, List
from dataclasses import dataclass
from wechaty import WechatyPlugin, Wechaty
from github import Repository, Issue, IssueComment, Github
import time


@dataclass
class IssueData:
    body: str
    labels: List[str]
    creator: str
    url: str


class SyncGithubIssuePlugin(WechatyPlugin):
    """sync github issue with wechaty plugin"""
    def __init__(self, repo_id: str, token: Optional[str] = None, sleep_seconds: int = 2):
        super().__init__()
        self.github: Github = Github(token)
        self.repo_id = repo_id
        self.sleep_seconds = sleep_seconds
    
    async def sync_issues(self):
        repo = self.github.get_repo(self.repo_id)
        for issue in repo.get_issues():
            issue_number = str(issue.number)
            if issue_number in self.setting or issue.pull_request:
                continue

            self.logger.info(f'start to save issue<{issue}>')

            # 1. set main body
            issue_data = {
                "title": issue.title,
                "body": issue.body,
                "labels": [],
                "creator": issue.user.login,
                "url": issue.html_url,
                "state": issue.state,
            }

            # 2. get labels
            for label in issue.get_labels():
                issue_data["labels"].append(label.name)
            
            # 3. comment
            comments = []
            for comment in issue.get_comments():
                reactions = comment.raw_data.get("reactions", {})
                comments.append({
                    "body": comment.body,
                    "url": comment.html_url,
                    "creator": comment.user.login,
                    "good_count": reactions.get("+1", 0) + reactions.get("heart", 0)
                })
            issue_data["comments"] = comments

            self.setting[issue_number] = issue_data
            time.sleep(self.sleep_seconds)

    async def init_plugin(self, wechaty: Wechaty) -> None:
        asyncio.create_task(
            self.sync_issues()
        )
