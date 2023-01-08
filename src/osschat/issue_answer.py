import random
import faiss
from wechaty import WechatyPlugin, Message

from datasets import load_dataset
from datasets.dataset_dict import DatasetDict
from datasets.arrow_dataset import Dataset
from datasets.search import NearestExamplesResults

from paddlenlp.transformers import AutoTokenizer, AutoModel
from src.osschat.tensor_encoder import TextEncoder, TextEncoderConfig

tokenizer = AutoTokenizer.from_pretrained("simbert-base-chinese")

dataset: DatasetDict = load_dataset("json", data_files='./data/faq.json')

config: TextEncoderConfig = TextEncoderConfig().parse_args(known_only=True)
encoder = TextEncoder(config)


def convert_features(examples):
    embedding = encoder.encode(examples['title'])
    return {
        "embedding": embedding
    }
    

feature_dataset: Dataset = dataset['train'].map(convert_features, batched=True, batch_size=100)
feature_dataset.add_faiss_index("embedding", metric_type=faiss.METRIC_INNER_PRODUCT)


class IssueAnswer(WechatyPlugin):

    def __init__(self,):
        super().__init__(None)
        self.threshold = 0.9

    def is_question(self, text: str):
        if "？" in text:
            return True
        if "为什么" in text:
            return True
        if "如何" in text:
            return True
        if "怎么" in text:
            return True
        return False
        

    async def on_message(self, msg: Message) -> None:
        room = msg.room()
        if room and room.room_id not in self.setting["room_ids"]:
            return

        text = msg.text()
        if not self.is_question(text):
            return

        embedding = encoder.encode([text])
        result: NearestExamplesResults = feature_dataset.get_nearest_examples(
            "embedding",
            embedding,
            k=3
        )

        head_text = random.choice(
            [
                '我发现你的问题已经有小伙伴问过了，可以参考：',
                '我这里有几个类似的问题，你可以参考：',
                '针对于你的问题，我这里有几个建议：',
                "兄嘚，我在 github issue 找到了几个类似的问题："
            ]
        )
        msg_result = [
            head_text,
            ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
        ]

        for index, score in enumerate(result.scores):
            if score > self.threshold:
                msg_result.append(
                    f'{index}. {result.examples["title"][index]} \n   {result.examples["url"][index]}'
                )
        
        talker = msg.talker()
        await msg.say("\n".join(msg_result), mention_ids=[talker.contact_id])

        import os, psutil
        p = psutil.Process(int(os.getpid()))

        msg_info = "current memory usage: %dMB" % int(p.memory_info().rss / 1024 / 1024)
        self.logger.info(msg_info)

