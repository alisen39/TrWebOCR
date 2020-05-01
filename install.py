import os, sys
import glob

BIG_FILES = ["./backend/libtorch/lib/libtorch.so"]
_BASEDIR = os.path.dirname(os.path.abspath(__file__))

BIG_FILES = [os.path.join(_BASEDIR, _) for _ in BIG_FILES]

FILE_SIZE = 32 * 1024 * 1024
PART_SEP = ".part."


def split(file_path):
    if not os.path.exists(file_path):
        return

    with open(file_path, "rb") as f:
        file_data = f.read()

    if len(file_data) <= FILE_SIZE:
        return

    pos = 0
    num = 0
    while pos < len(file_data):
        with open(file_path + PART_SEP + str(num), "wb") as f:
            f.write(file_data[pos:pos + FILE_SIZE])
            pos += FILE_SIZE
            num += 1

    os.remove(file_path)


def join(file_path):
    if os.path.exists(file_path):
        return

    file_parts = glob.glob(file_path + PART_SEP + "*")
    if len(file_parts) < 1:
        return

    file_data = bytes()

    for num in range(len(file_parts)):
        with open(file_path + PART_SEP + str(num), "rb") as f:
            file_data += f.read()

    with open(file_path, "wb") as f:
        f.write(file_data)

    for file_part in file_parts:
        os.remove(file_part)


if __name__ == '__main__':
    for big_file in BIG_FILES:
        join(big_file)

