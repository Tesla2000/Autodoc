FROM pytorch/pytorch:2.4.0-cuda11.8-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code
WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME ["/code/models"]

CMD ["python", "main.py"]
