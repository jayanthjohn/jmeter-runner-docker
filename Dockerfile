FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV JMETER_VERSION=5.6.3
ENV RUNNER_VERSION=2.316.0

# Install dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    python3 \
    python3-pip \
    curl \
    wget \
    unzip \
    git \
    && ln -s $(find /usr/lib/jvm -type d -name "java-11-openjdk*") /usr/lib/jvm/java-11-openjdk-amd64 \
    && apt-get clean

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${PATH}:${JAVA_HOME}/bin:/opt/jmeter/bin"

# Install JMeter
RUN wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz && \
    tar -xzf apache-jmeter-${JMETER_VERSION}.tgz && \
    mv apache-jmeter-${JMETER_VERSION} /opt/jmeter && \
    rm apache-jmeter-${JMETER_VERSION}.tgz

# Install GitHub Runner
RUN mkdir /actions-runner && cd /actions-runner && \
    curl -o actions-runner-linux-x64.tar.gz -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz && \
    tar -xzf actions-runner-linux-x64.tar.gz && rm actions-runner-linux-x64.tar.gz

# Install Python packages
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy scripts and test files
COPY --chmod=755 entrypoint.sh /entrypoint.sh
COPY . /workspace
WORKDIR /workspace

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]