FROM debian:bullseye

RUN apt update && apt install -y build-essential gcc-10 clang clang-tools cmake python3 cppcheck valgrind afl gcc-multilib && rm -rf /var/lib/apt/lists/*

WORKDIR /service
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . ./
EXPOSE 5000
ENTRYPOINT ["python3", "main.py"]
