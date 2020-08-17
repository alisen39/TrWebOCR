FROM python:3.7-slim

RUN sed -i 's#http://deb.debian.org#https://mirrors.163.com#g' /etc/apt/sources.list
RUN apt update && apt install -y libglib2.0-dev libsm6 libxrender1 libxext-dev supervisor build-essential \
        && rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY ./requirements.txt ./TrWebOCR/
RUN pip3 install -r ./TrWebOCR/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
COPY . ./TrWebOCR

RUN python3 ./TrWebOCR/install.py
EXPOSE 8089
CMD ["supervisord","-c","/TrWebOCR/supervisord.conf"]
