# Use the specified Python base image for amd64
FROM python:3.10-slim AS amd64

# Define environment variables for Kafka version and Scala version
ENV KAFKA_VERSION=3.7.0
ENV KAFKA_SCALA_VERSION=2.13
ENV ARCH=amd64

# Install necessary packages: OpenJDK, wget, curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget curl openjdk-17-jdk && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and extract Kafka for amd64 architecture
RUN wget -q https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz -O /tmp/kafka.tgz && \
    mkdir -p /opt/kafka && \
    tar -xzf /tmp/kafka.tgz -C /opt/kafka --strip-components=1 && \
    rm /tmp/kafka.tgz

# Set environment variables for Kafka and Python
ENV PATH="/opt/kafka/bin:${PATH}"
ENV KAFKA_HEAP_OPTS="-Xmx1G -Xms1G"

# Expose Kafka and Zookeeper ports
EXPOSE 9092 2181

# Copy server.properties and startup scripts into the container
COPY server.properties /opt/kafka/config/server.properties
COPY start-kafka.sh /start-kafka.sh
COPY start-zookeeper.sh /start-zookeeper.sh

# Make scripts executable
RUN chmod +x /start-kafka.sh /start-zookeeper.sh

# Start Zookeeper and Kafka
CMD ["/start-zookeeper.sh"]

# Use the specified Python base image for arm64
FROM python:3.10-slim AS arm64

# Define environment variables for Kafka version and Scala version
ENV KAFKA_VERSION=3.7.0
ENV KAFKA_SCALA_VERSION=2.13
ENV ARCH=arm64

# Install necessary packages: OpenJDK, wget, bash
RUN apt-get update && apt-get install -y --no-install-recommends wget openjdk-17-jdk bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and extract Kafka for arm64 architecture
RUN wget -q https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz -O /tmp/kafka.tgz && \
    mkdir -p /opt/kafka && \
    tar -xzf /tmp/kafka.tgz -C /opt/kafka --strip-components=1 && \
    rm /tmp/kafka.tgz

# Set environment variables for Kafka and Python
ENV PATH="/opt/kafka/bin:${PATH}"
ENV KAFKA_HEAP_OPTS="-Xmx1G -Xms1G"

# Expose Kafka and Zookeeper ports
EXPOSE 9092 2181

# Copy server.properties and startup scripts into the container
COPY server.properties /opt/kafka/config/server.properties
COPY start-kafka.sh /start-kafka.sh
COPY start-zookeeper.sh /start-zookeeper.sh

# Make scripts executable
RUN chmod +x /start-kafka.sh /start-zookeeper.sh

# Start Zookeeper and Kafka
CMD ["/start-zookeeper.sh"]

# ----------------------------------------
# Stage for Zookeeper setup
# ----------------------------------------
FROM amd64 AS zookeeper-setup

# Install Zookeeper
RUN curl -fsSL https://downloads.apache.org/zookeeper/zookeeper-3.7.0/apache-zookeeper-3.7.0-bin.tar.gz -o /tmp/zookeeper.tgz && \
    mkdir -p /opt/zookeeper && \
    tar -xzf /tmp/zookeeper.tgz -C /opt/zookeeper --strip-components=1 && \
    rm /tmp/zookeeper.tgz


# Copy Zookeeper configuration files
COPY zookeeper.properties /opt/zookeeper/conf/zookeeper.properties

# Copy Zookeeper start script
COPY start-zookeeper.sh /start-zookeeper.sh

# Make start-zookeeper.sh executable
RUN chmod +x /start-zookeeper.sh

# ----------------------------------------
# Final image setup
# ----------------------------------------
FROM arm64 AS final

# Copy Kafka binaries and configuration from arm64 stage
COPY --from=arm64 /opt/kafka /opt/kafka

# Copy Zookeeper binaries and configuration from zookeeper-setup stage
COPY --from=zookeeper-setup /opt/zookeeper /opt/zookeeper

# Copy server.properties and startup scripts from arm64 stage
COPY server.properties /opt/kafka/config/server.properties
COPY start-kafka.sh /start-kafka.sh
COPY start-zookeeper.sh /start-zookeeper.sh

# Make scripts executable
RUN chmod +x /start-kafka.sh /start-zookeeper.sh

# Expose Kafka and Zookeeper ports
EXPOSE 9092 2181

# Set the entrypoint for the container
ENTRYPOINT ["/start-kafka.sh"]
