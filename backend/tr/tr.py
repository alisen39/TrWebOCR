# coding: utf-8
import numpy
from PIL import Image
import os, time, platform
import ctypes
import cv2
from functools import cmp_to_key

FLAG_RECT = (1 << 0)
FLAG_ROTATED_RECT = (1 << 1)
FLAG_CRNN_PROB = (1 << 16)
FLAG_CRNN_INDEX = (1 << 17)

_BASEDIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_BASEDIR, "char_table.txt"), "r", encoding="utf-8") as f:
    char_table = " " + f.read()

_cwd = os.getcwd()
os.chdir(_BASEDIR)

if platform.system() == "Windows":
    _libc = ctypes.cdll.LoadLibrary(os.path.join(_BASEDIR, 'libtr.dll'))
else:
    _libc = ctypes.cdll.LoadLibrary(os.path.join(_BASEDIR, 'libtr.so'))
assert _libc is not None

_libc.tr_init.restype = ctypes.c_int
_libc.tr_detect.argtypes = (ctypes.c_void_p,)

_libc.tr_detect.restype = ctypes.c_int
_libc.tr_detect.argtypes = (ctypes.c_void_p, ctypes.c_void_p,
                            ctypes.c_int, ctypes.c_int)

_libc.tr_read_float.restype = ctypes.c_int
_libc.tr_read_float.argtypes = (ctypes.c_void_p, ctypes.c_int)

_libc.tr_read_int.restype = ctypes.c_int
_libc.tr_read_int.argtypes = (ctypes.c_void_p, ctypes.c_int)

_libc.tr_init()
os.chdir(_cwd)

line_count = 0


def _read(arr, flag):
    if arr.dtype == numpy.int32:
        nbytes = _libc.tr_read_int(
            numpy.ctypeslib.as_ctypes(arr),
            flag)
        return nbytes == arr.nbytes
    elif arr.dtype == numpy.float32:
        nbytes = _libc.tr_read_float(
            numpy.ctypeslib.as_ctypes(arr),
            flag)
        return nbytes == arr.nbytes
    else:
        raise NotImplementedError()


def recognize(img):
    if isinstance(img, numpy.ndarray):
        height, width = img.shape
        if height != 32:
            new_width = int(width * 32 / height + 0.5)
            img_arr = cv2.resize(img, (new_width, 32), cv2.INTER_CUBIC)
        else:
            img_arr = img
    else:
        if isinstance(img, str):
            img_pil = Image.open(img).convert("L")
        elif isinstance(img, Image.Image):
            if img.mode != "L":
                img_pil = img.convert("L")
            else:
                img_pil = img
        else:
            raise NotImplementedError()

        if img_pil.height != 32:
            new_width = int(img_pil.width * 32 / (img_pil.height + 0.5))
            # new_width = int(img_pil.width * 32 / img_pil.height + 0.5)
            img_pil = img_pil.resize((new_width, 32), Image.BICUBIC)

        img_arr = numpy.asarray(img_pil, dtype="float32") / 255.

    # img_arr = (img_arr - img_arr.min()) / (img_arr.max() - img_arr.min())

    # global line_count
    # line_count += 1
    # cv2.imwrite("tmp/" + str(line_count) + ".png", img_arr * 255.0)

    # img_arr = (img_arr - 0.5) * 2
    # print("img_arr", img_arr.min(), img_arr.max())

    height, width = img_arr.shape
    size = numpy.array([width, height], dtype="int32")

    num = _libc.tr_recognize(
        numpy.ctypeslib.as_ctypes(img_arr),
        numpy.ctypeslib.as_ctypes(size),
        2,
    )

    if num <= 0:
        return None, None

    crnn_prob = numpy.zeros((num,), "float32")
    crnn_index = numpy.zeros((num,), "int32")

    if not _read(crnn_prob, FLAG_CRNN_PROB):
        return None, None
    if not _read(crnn_index, FLAG_CRNN_INDEX):
        return None, None

    txt = ""
    prob = 0.
    idx_pre = -1
    count = 0
    for pos in range(num):
        idx = crnn_index[pos]
        if idx > 0:
            if idx != idx_pre:
                txt += char_table[idx]

            # txt += char_table[idx]

            count += 1
            prob += crnn_prob[pos]

        idx_pre = idx

    return txt, float(prob / max(count, 1))


def detect(img, flag=FLAG_RECT):
    if isinstance(img, str):
        img_pil = Image.open(img).convert("L")
    elif isinstance(img, Image.Image):
        if img.mode != "L":
            img_pil = img.convert("L")
        else:
            img_pil = img
    else:
        raise NotImplementedError()

    img_arr = numpy.asarray(img_pil, dtype="float32") / 255

    size = numpy.array([img_pil.width, img_pil.height], dtype="int32")

    num = _libc.tr_detect(
        numpy.ctypeslib.as_ctypes(img_arr),
        numpy.ctypeslib.as_ctypes(size),
        2,
        flag
    )

    if num <= 0:
        return None

    if flag == FLAG_RECT:
        rect_arr = numpy.zeros((num, 4), "float32")
    elif flag == FLAG_ROTATED_RECT:
        rect_arr = numpy.zeros((num, 5), "float32")
    else:
        raise NotImplementedError(flag)

    if not _read(rect_arr, flag):
        return None

    return rect_arr


def _sort_blocks(blocks):
    def block_cmp(b1, b2):
        list1 = [b1[0][0], b1[0][1], b1[0][2], b1[0][3]]
        list2 = [b2[0][0], b2[0][1], b2[0][2], b2[0][3]]
        if len(b1[0]) == 4:
            list1[0] += list1[2] / 2
            list1[1] += list1[3] / 2
            list2[0] += list2[2] / 2
            list2[1] += list2[3] / 2

        flag = 1
        if list1[0] > list2[0]:
            list1, list2 = list2, list1
            flag = -1

        if list2[1] + list1[3] / 2 < list1[1]:
            return flag
        return -flag

    blocks.sort(key=cmp_to_key(block_cmp), reverse=False)


def run_angle(img, px=0, py=2):
    if isinstance(img, str):
        img_pil = Image.open(img).convert("L")
    elif isinstance(img, Image.Image):
        if img.mode != "L":
            img_pil = img.convert("L")
        else:
            img_pil = img
    else:
        raise NotImplementedError()

    img_arr = numpy.asarray(img_pil, dtype="float32") / 255.0
    rect_arr = detect(img_pil, FLAG_ROTATED_RECT)

    if rect_arr is None:
        return []

    results = []
    for rect in rect_arr:
        cx, cy, w, h, a = rect
        if a < -45:
            w, h = h, w
            a += 90
        w += px * 2
        h += py * 2
        box1 = cv2.boxPoints(((cx, cy), (w, h), a))

        w = int(w + 0.5)
        h = int(h + 0.5)
        box2 = numpy.array([[0, h - 1],
                            [0, 0],
                            [w - 1, 0],
                            [w - 1, h - 1]], dtype="float32")

        matrix = cv2.getPerspectiveTransform(box1, box2)
        img_line = cv2.warpPerspective(img_arr, matrix, (w, h), flags=cv2.INTER_CUBIC, borderValue=1.0)

        txt, prob = recognize(img_line)

        if txt != "":
            results.append(((cx, cy, w, h, a), txt, prob))

    _sort_blocks(results)
    return results


def run(img, px=3, py=0):
    if isinstance(img, str):
        img_pil = Image.open(img).convert("L")
    elif isinstance(img, Image.Image):
        if img.mode != "L":
            img_pil = img.convert("L")
        else:
            img_pil = img
    else:
        raise NotImplementedError()

    rect_arr = detect(img_pil, FLAG_RECT)
    if rect_arr is None:
        return []

    rect_arr = numpy.int0(rect_arr)

    results = []
    for rect in rect_arr:
        x, y, w, h = rect
        x -= px
        w += px * 2
        line_pil = img_pil.crop((x, y, x + w, y + h))

        txt, prob = recognize(line_pil)

        if txt != "":
            results.append(((x, y, w, h), txt, prob))

    _sort_blocks(results)
    return results


if __name__ == "__main__":
    pass
