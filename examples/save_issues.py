import asyncio
from wechaty import Wechaty, WechatyOptions, WechatyPluginOptions
from wechaty.fake_puppet import FakePuppet


from osschat.sync_github_issue import SyncGithubIssuePlugin


async def run():
    bot = Wechaty(options=WechatyOptions(
        puppet=FakePuppet(
            options=None
        )
    ))
    bot.use(
        SyncGithubIssuePlugin("PaddlePaddle/PaddleNLP", token='b958381f96bfd5afc39ae1b508feab0abeb5ae6a')
    )
    await bot.start()

asyncio.run(run())