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
feature_dataset.add_faiss_index("embedding")


embedding = encoder.encode(["get_offset_mapping 用不起来了"])
result: NearestExamplesResults = feature_dataset.get_nearest_examples(
    "embedding",
    embedding,
    k=10
)

for index, score in enumerate(result.scores):
    print("-=============")
    print(f'score: <{score}>')
    print(f'score: <{result.examples["title"][index]}>')
    print(f'score: <{result.examples["url"][index]}>')