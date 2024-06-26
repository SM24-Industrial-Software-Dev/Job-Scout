#!/bin/bash

# Create Kafka config file with advertised listeners
echo "advertised.listeners=PLAINTEXT://$HOSTNAME:9092" > /opt/kafka/config/server.properties

# Start Kafka server
exec /opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
