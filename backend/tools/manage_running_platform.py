#!/usr/bin/env python
# encoding: utf-8
# author:alisen
# time: 2020/7/25 14:22
'''
    管理使用gpu或cpu的方式
'''

import hashlib
import json
import os
import sys
import shutil

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

LIB_TR = 'libtr.so'
LIB_ONNX = 'libonnxruntime.so.1.3.0'

TR_GPU_PATH = os.path.join(BASE_PATH, "tr_gpu")
TR_CPU_PATH = os.path.join(BASE_PATH, "tr_cpu")
TR_PATH = os.path.join(BASE_PATH, "tr")


def calc_sha256(filname):
    with open(filname, "rb") as f:
        sha256obj = hashlib.sha256()
        sha256obj.update(f.read())
        hash_value = sha256obj.hexdigest()
    return hash_value


def get_run_version():
    sha256 = ''
    for lib in [LIB_TR, LIB_ONNX]:
        sha256 += calc_sha256(os.path.join(TR_PATH, lib))
    with open(os.path.join(BASE_PATH, 'tools/version_map.txt'), 'r', encoding='utf8') as r:
        version_map = r.read()
    version_map = json.loads(version_map)
    if sha256 not in version_map:
        return "error!!! 请重新下载项目"
    return version_map.get(sha256)


def change_version(version):
    path_map = {
        'cpu': TR_CPU_PATH,
        'gpu': TR_GPU_PATH,
    }
    if version not in path_map:
        return ValueError('只能选择 cpu/gpu')
    path = path_map.get(version)
    for lib in [LIB_TR, LIB_ONNX]:
        shutil.copy(os.path.join(path, lib),  TR_PATH)


def update_sha256():
    gpu_sha256 = ''
    cpu_sha256 = ''

    for lib in [LIB_TR, LIB_ONNX]:
        gs = calc_sha256(os.path.join(BASE_PATH, "tr_gpu/" + lib))
        cs = calc_sha256(os.path.join(BASE_PATH, "tr_cpu/" + lib))
        gpu_sha256 += gs
        cpu_sha256 += cs

    with open(os.path.join(BASE_PATH, 'tools/version_map.txt'), 'w', encoding='utf8') as w:
        version_map = {gpu_sha256: 'gpu', cpu_sha256: 'cpu'}
        w.write(json.dumps(version_map))


if __name__ == '__main__':
    update_sha256()
