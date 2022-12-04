from __future__ import annotations
import os
from typing import Optional, Union, List
from numpy import ndarray
import paddle
from paddle.tensor.tensor import Tensor
import faiss                   # make faiss available
from faiss.swigfaiss import IndexFlat, Index
import numpy as np
from tap import Tap

from .tensor_encoder import TextEncoder
from .schema import Document


class InitFaissIndexMixin:
    @staticmethod
    def get_default_faiss_index() -> Index:
        return faiss.index_factory(
            768,
            "Flat",
            faiss.METRIC_INNER_PRODUCT,
        )

class TensorSearcherConfig(Tap):
    index_file = ""


class FaissTensorSeacher(InitFaissIndexMixin):
    def __init__(self, encoder: TextEncoder, index: Optional[Index] = None, top_k: int = 50) -> None:
        self.encoder: TextEncoder = encoder
        self.index: Index = index or self.get_default_faiss_index()
        self.top_k = top_k
        self.index.

    @staticmethod
    def from_file(index_file: str) -> FaissTensorSeacher:
        index = faiss.read_index(index_file)
        return FaissTensorSeacher(index)
    
    def add(self, tensor: Union[ndarray, Tensor], documents: List[Document]):
        if paddle.is_tensor(tensor):
            tensor = tensor.numpy()

        # normalize the tensor
        tensor = tensor / np.linalg.norm(tensor)
        self.index.add(
            tensor
        )

        self.top_k = min(self.top_k, self.index.ntotal)
        np.save(self.all_tensor_file, tensor)

    def search(self, tensor: Union[ndarray, Tensor]):
        if paddle.is_tensor(tensor):
            tensor = tensor.numpy()

        tensor = tensor / np.linalg.norm(tensor)

        _, indexes = self.index.search(
            tensor,
            k=self.top_k,
        ) 
        return indexes


def test_seacher():
    searcher = FaissTensorSeacher(top_k=5)
    all_tensors = np.random.randn(20, 768)
    tensor_ids = list(range(20))
    searcher.add(
        all_tensors,
        tensor_ids
    )

    searcher.search(
        all_tensors[0].reshape(-1, 768)
    )

test_seacher()