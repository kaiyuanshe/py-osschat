
# 用来制定默认make的指令集
.DEFAULT_GOAL := all

all:
	python b.py

install:
	sudo apt-get install ffmpeg libsm6 libxext6  -y
	conda install -c pytorch faiss-cpu
	pip install -r requirements.txt
    