import os

from typing import List
import numpy as np
from tap import Tap
from numpy import ndarray
from paddlenlp.transformers import AutoTokenizer, BertModel

import fastdeploy as fd


class TextEncoderConfig(Tap):
    model_name: str = "simbert-base-chinese"
    output_dir = "./output"
    vocab_path = ""
    device = "cpu"  # Type of inference device, support 'cpu' or 'gpu'.
    backend = 'onnx_runtime'    # 'onnx_runtime', 'paddle', 'openvino', 'tensorrt', 'paddle_tensorrt'
    batch_size = 1
    max_length = 64    # max sequence length
    log_interval = 10
    use_fp16 = False
    use_fast = False


import paddle
from paddle.static import InputSpec


def to_static(model, save_dir: str):
    inputs = [
        InputSpec(shape=[None, None])
    ]
    inputs = [
        paddle.static.InputSpec(shape=[None, None], dtype="int64"),
    ]

    model = paddle.jit.to_static(model, input_spec=inputs)
    # Save in static graph model.
    paddle.jit.save(model, save_dir)
        

class TextEncoder:
    def __init__(self, config: TextEncoderConfig):
        # init model
        file_path = os.path.join(config.output_dir, "simbert.pdmodel")
        if not os.path.exists(file_path):
            model = BertModel.from_pretrained(config.model_name)
            to_static(model, os.path.join(config.output_dir, "simbert"))

        self.tokenizer = AutoTokenizer.from_pretrained(
            'simbert-base-chinese', use_faster=config.use_fast)
        self.runtime = self.create_fd_runtime(config)
        self.batch_size = config.batch_size
        self.max_length = config.max_length

    def create_fd_runtime(self, config: TextEncoderConfig):
        option = fd.RuntimeOption()
        model_path = os.path.join(config.output_dir, "simbert.pdmodel")
        params_path = os.path.join(config.output_dir, "simbert.pdiparams")
        option.set_model_path(model_path, params_path)
        if config.device == 'cpu':
            option.use_cpu()
        else:
            option.use_gpu()
        if config.backend == 'paddle':
            option.use_paddle_infer_backend()
        elif config.backend == 'onnx_runtime':
            option.use_ort_backend()
        elif config.backend == 'openvino':
            option.use_openvino_backend()
        else:
            option.use_trt_backend()
            if config.backend == 'paddle_tensorrt':
                option.enable_paddle_to_trt()
                option.enable_paddle_trt_collect_shape()
            trt_file = os.path.join(config.output_dir, "infer.trt")
            option.set_trt_input_shape(
                'input_ids',
                min_shape=[1, config.max_length],
                opt_shape=[config.batch_size, config.max_length],
                max_shape=[config.batch_size, config.max_length])
            option.set_trt_input_shape(
                'token_type_ids',
                min_shape=[1, config.max_length],
                opt_shape=[config.batch_size, config.max_length],
                max_shape=[config.batch_size, config.max_length])
            if config.use_fp16:
                option.enable_trt_fp16()
                trt_file = trt_file + ".fp16"
            option.set_trt_cache_file(trt_file)
        return fd.Runtime(option)

    def preprocess(self, texts):
        data = self.tokenizer(
            texts,
            max_length=self.max_length,
            padding=True,
            truncation=True)
        input_ids_name = self.runtime.get_input_info(0).name
        input_map = {
            input_ids_name: np.array(
                data["input_ids"], dtype="int64")
        }
        return input_map

    def encode(self, texts: List[str]) -> ndarray:
        input_map = self.preprocess(texts)
        result = self.runtime.infer(input_map)
        return result[1]
        