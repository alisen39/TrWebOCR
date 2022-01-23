# coding: utf-8
import os
import platform
import ctypes
import numpy as np

try:
    unichr
except NameError:
    unichr = chr

CV_8UC1 = 0
CV_32FC1 = 5
CV_8UC3 = 16
CV_32FC3 = 21

FLAG_RECT = (1 << 0)
FLAG_ROTATED_RECT = (1 << 1)

ORT_DISABLE_ALL = 0
ORT_ENABLE_BASIC = 1
ORT_ENABLE_EXTENDED = 2
ORT_ENABLE_ALL = 99

RECT_SIZE = 6
ORT_SIZE = 256
_BASEDIR = os.path.dirname(os.path.abspath(__file__))

_cwd = os.getcwd()
os.chdir(_BASEDIR)

if platform.system() == "Windows":
    raise NotImplementedError()
else:
    _libc = ctypes.cdll.LoadLibrary(os.path.join(_BASEDIR, 'libtr.so'))
assert _libc is not None
os.chdir(_cwd)

_libc.tr_init.argtypes = (
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p
)

_libc.tr_release.argtypes = (ctypes.c_int,)

_libc.tr_detect.restype = ctypes.c_int
_libc.tr_detect.argtypes = (
    ctypes.c_int,
    ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int,
    ctypes.c_void_p, ctypes.c_int
)

_libc.tr_recognize.restype = ctypes.c_int
_libc.tr_recognize.argtypes = (
    ctypes.c_int,
    ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_int
)

_libc.tr_run.restype = ctypes.c_int
_libc.tr_run.argtypes = (
    ctypes.c_int, ctypes.c_int,
    ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int,
    ctypes.c_void_p, ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_int
)

_libc.tr_crnn.restype = ctypes.c_int
_libc.tr_crnn.argtypes = (
    ctypes.c_int,
    ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_int
)

def c_ptr(arr):
    if not isinstance(arr, (np.ndarray, str)):
        arr = np.array(arr)

    if isinstance(arr, np.ndarray):
        assert arr.flags['C_CONTIGUOUS']
        return np.ctypeslib.as_ctypes(arr)
    elif isinstance(arr, str):
        return ctypes.create_string_buffer(arr.encode())
    else:
        raise NotImplementedError()


def c_img(arr):
    if not isinstance(arr, (np.ndarray, str)):
        arr = np.array(arr)

    if isinstance(arr, str):
        return c_ptr(arr), 0, 0, 0
    elif isinstance(arr, np.ndarray):
        res = [None, 0, 0, 0]
        res[0] = c_ptr(arr)
        res[1] = arr.shape[0]
        res[2] = arr.shape[1]

        channel = 0
        if arr.ndim == 2:
            channel = 1
        elif arr.ndim == 3:
            channel = arr.shape[2]

        if channel not in [1, 3]:
            raise NotImplementedError()

        if arr.dtype == np.uint8:
            res[3] = CV_8UC3 if channel == 3 else CV_8UC1
        elif arr.dtype == np.float32:
            res[3] = CV_32FC3 if channel == 3 else CV_32FC1

        return tuple(res)
    else:
        raise NotImplementedError()


def init(pid, id, model, arg=None):
    """
    :param pid: process id
    :param id: session id
    :param model: model path
    :param arg: extra arguments
    :return: None
    """
    _cwd = os.getcwd()
    os.chdir(_BASEDIR)

    _libc.tr_init(pid, id, c_ptr(model), arg)

    os.chdir(_cwd)


def _parse(unicode_arr, prob_arr, num):
    txt = ""
    prob = 0.
    unicode_pre = -1
    count = 0
    for pos in range(num):
        unicode = unicode_arr[pos]
        if unicode >= 0:
            if unicode != unicode_pre:
                txt += unichr(unicode)

            count += 1
            prob += prob_arr[pos]

        unicode_pre = unicode

    return txt, float(prob / max(count, 1))


def crnn(img, max_items=512*7000, crnn_id=1):
    buf_arr = np.zeros((max_items,), dtype="float32")
    shape_arr = np.zeros((8,), dtype="int32")
    img = c_img(img)

    assert img[3] == CV_32FC1
    assert img[1] == 32

    num = _libc.tr_crnn(
        crnn_id,
        img[0], img[1], img[2],
        c_ptr(buf_arr),
        c_ptr(shape_arr),
        max_items
    )

    buf_arr = buf_arr[:num]
    return buf_arr.reshape(shape_arr[0], shape_arr[2])


def recognize(img, max_width=512, crnn_id=1):
    unicode_arr = np.zeros((max_width,), dtype="int32")
    prob_arr = np.zeros((max_width,), dtype="float32")
    img = c_img(img)
    num = _libc.tr_recognize(
        crnn_id,
        img[0], img[1], img[2], img[3],
        c_ptr(unicode_arr),
        c_ptr(prob_arr),
        max_width
    )

    return _parse(unicode_arr, prob_arr, num)


def detect(img, max_lines=512, flag=FLAG_ROTATED_RECT, ctpn_id=0):
    rect_arr = np.zeros((max_lines, RECT_SIZE), dtype="float32")
    img = c_img(img)
    num = _libc.tr_detect(
        ctpn_id,
        img[0], img[1], img[2], img[3],
        flag,
        c_ptr(rect_arr),
        max_lines
    )

    return rect_arr[:num, :5].tolist()


def release(*args):
    for arg in args:
        _libc.tr_release(arg)


def run(img,
        max_lines=512,
        flag=FLAG_ROTATED_RECT,
        max_width=512,
        ctpn_id=0,
        crnn_id=1):
    rect_arr = np.zeros((max_lines, RECT_SIZE), dtype="float32")
    unicode_arr = np.zeros((max_lines, max_width), dtype="int32")
    prob_arr = np.zeros((max_lines, max_width), dtype="float32")
    img = c_img(img)
    line_num = _libc.tr_run(
        ctpn_id, crnn_id,
        img[0], img[1], img[2], img[3],
        flag,
        c_ptr(rect_arr),
        max_lines,
        c_ptr(unicode_arr),
        c_ptr(prob_arr),
        max_width
    )

    results = []
    for i in range(line_num):
        num = int(rect_arr[i][-1] + 0.5)
        txt, confidence = _parse(unicode_arr[i], prob_arr[i], num)
        results.append((rect_arr[i][:5].tolist(), txt, confidence))

    return results


init(0, 0, "ctpn.bin")
init(0, 1, "crnn.bin")

if __name__ == "__main__":
    pass
