FROM python:3

WORKDIR /usr/src/app

RUN curl --output jdk.tar.gz  https://download.oracle.com/graalvm/17/latest/graalvm-jdk-17_linux-x64_bin.tar.gz && \
    tar -zxvf jdk.tar.gz && \
    mv graalvm-jdk-17.0.12+8.1 jdk && \
    rm jdk.tar.gz

ENV JAVA_CMD="/usr/src/app/jdk/bin/java" \
    JAVAC_CMD="/usr/src/app/jdk/bin/javac"

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "rabbit_listener.py"]
