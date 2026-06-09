FROM flink:1.18-java11

# Install Python 3.9 and pip (Debian Bullseye base)
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

# Install torch first from the CPU-only index
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu

# Install PyFlink first
RUN pip3 install apache-flink==1.18.1 kafka-python-ng

# Install ML dependencies separately so pip doesn't cross-check them against Flink
RUN pip3 install nltk \
    vaderSentiment \
    transformers \
    onnxruntime \
    optimum[onnxruntime] \
    requests \
    langdetect \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple

# Ensure VADER lexicon is downloaded
RUN python -c "import nltk; nltk.download('vader_lexicon')"

# Download Flink Kafka Connector JAR
RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.0.2-1.18/flink-sql-connector-kafka-3.0.2-1.18.jar

# Create directory for models
RUN mkdir -p /opt/pulse/models
