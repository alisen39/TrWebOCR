FROM python:3.7.7-slim

COPY . ./TrWebOCR
RUN sed -i 's#http://deb.debian.org#https://mirrors.163.com#g' /etc/apt/sources.list
RUN apt update && apt install -y libglib2.0-dev libsm6 libxrender1 libxext-dev supervisor

RUN /usr/local/bin/python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -r ./TrWebOCR/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN python ./TrWebOCR/install.py
EXPOSE 8089
CMD ["supervisord","-c","/TrWebOCR/supervisord.conf"]
