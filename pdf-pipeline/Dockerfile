FROM ubuntu:22.04

RUN apt update && apt install -y \
  poppler-utils \
  ghostscript \
  imagemagick \
  tesseract-ocr \
  tesseract-ocr-fas \
  tesseract-ocr-eng \
  python3 \
  python3-pip \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /data

COPY convertor.py /data/

ENTRYPOINT ["python3", "convertor.py"]
