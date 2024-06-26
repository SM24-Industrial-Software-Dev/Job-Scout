#!/bin/bash

# Start Zookeeper using its configuration file
exec /opt/zookeeper/bin/zookeeper-server-start.sh /opt/zookeeper/conf/zookeeper.properties
