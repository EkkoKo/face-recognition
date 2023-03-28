FROM python:3.6.13

WORKDIR /service
COPY requirements.txt .
RUN apt-get update && apt-get install -y cmake
RUN pip install -r requirements.txt
COPY . ./
EXPOSE 5000
ENTRYPOINT ["python3", "main.py"]
