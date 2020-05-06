FROM python:3.7.7-slim

COPY . ./TrWebOCR
RUN apt update && apt install -y libglib2.0-dev libsm6 libxrender1 libxext-dev
RUN pip install -r ./TrWebOCR/requirements.txt
RUN python ./TrWebOCR/install.py
EXPOSE 8089
CMD ["python","  ./TrWebOCR/backend/main.py"]

# apt update && apt install -y libglib2.0-dev libsm6 libxrender1 libxext-dev
 ##