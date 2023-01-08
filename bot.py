"""template of your bot"""
from __future__ import annotations
from argparse import ArgumentParser
import os
import asyncio
from wechaty import Wechaty, WechatyOptions
from wechaty_puppet import PuppetOptions
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from wechaty.fake_puppet import FakePuppet
from wechaty_plugin_contrib.message_controller import message_controller
from wechaty_plugin_contrib.contrib.api_plugin import APIPlugin
from wechaty_plugin_contrib.contrib.ding_dong_plugin import DingDongPlugin
from wechaty_plugin_contrib.contrib.chat_history_plugin import ChatHistoryPlugin, ChatHistoryPluginOptions
from src.osschat.sync_github_issue import SyncGithubIssuePlugin
from src.osschat.issue_answer import IssueAnswer
from dotenv import load_dotenv


def get_args():
    """get args which only contains port"""
    parser = ArgumentParser()
    parser.add_argument("--port", default=8081, required=False)
    args = parser.parse_args()
    print(args)
    return args
    

async def main():
    args = get_args()
    load_dotenv()
    options = WechatyOptions(
        port=args.port,
        scheduler=AsyncIOScheduler(),
    )
    bot = Wechaty(options)
    bot.use([
        DingDongPlugin(),
        IssueAnswer(),
    ])
    message_controller.init_plugins(bot)

    await bot.start()
    

if __name__ == "__main__":
    asyncio.run(main())
