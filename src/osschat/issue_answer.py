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

dataset: DatasetDict = load_dataset("json", data_files='./data/corpus.json')

config: TextEncoderConfig = TextEncoderConfig().parse_args(known_only=True)
encoder = TextEncoder(config)


def convert_features(examples):
    embedding = encoder.encode(examples['question'])
    return {
        "embedding": embedding
    }
    

feature_dataset: Dataset = dataset['train'].map(convert_features, batched=True, batch_size=100)
feature_dataset.add_faiss_index("embedding", metric_type=faiss.METRIC_INNER_PRODUCT)


class IssueAnswer(WechatyPlugin):

    def __init__(self,):
        super().__init__(None)
        self.threshold = 90

    async def on_message(self, msg: Message) -> None:
        
        room = msg.room()
        if room and room.room_id not in self.setting["room_ids"]:
            return

        text = msg.text()

        embedding = encoder.encode([text])
        result: NearestExamplesResults = feature_dataset.get_nearest_examples(
            "embedding",
            embedding,
            k=1
        )

        head_text = random.choice(
            [
                "你的这个问题，我知道：",
                "兄嘚，我在我的知识库中找到了类似的问题："
            ]
        )
        msg_result = [
            head_text,
        ]

        for index, score in enumerate(result.scores):
            if score > self.threshold:
                print(result.examples)
                msg_result.append(
                    f'{result.examples["answer"][index]}'
                )
        if len(msg_result) == 1:
            return
        
        talker = msg.talker()
        await msg.say("\n".join(msg_result), mention_ids=[talker.contact_id])

        import os, psutil
        p = psutil.Process(int(os.getpid()))

        msg_info = "current memory usage: %dMB" % int(p.memory_info().rss / 1024 / 1024)
        self.logger.info(msg_info)

