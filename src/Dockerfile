FROM ubuntu:20.04

LABEL software.name="Greg's D&D Voice Generator Implementation"

# packaging dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        dh-make \
        fakeroot \
        build-essential \
        devscripts \
        lsb-release && \
    rm -rf /var/lib/apt/lists/*

# packaging
ARG PKG_VERS
ARG PKG_REV
ARG RUNTIME_VERSION
ARG DOCKER_VERSION

ENV DEBFULLNAME "NVIDIA CORPORATION"
ENV DEBEMAIL "cudatools@nvidia.com"
ENV REVISION "$PKG_VERS-$PKG_REV"
ENV DOCKER_VERSION $DOCKER_VERSION
ENV RUNTIME_VERSION $RUNTIME_VERSION
ENV SECTION ""

# output directory
ENV DIST_DIR=/tmp/nvidia-docker2-$PKG_VERS
RUN mkdir -p $DIST_DIR /dist

# output directory
ENV DIST_DIR=/tmp/nvidia-docker2-$PKG_VERS
RUN mkdir -p $DIST_DIR /dist

# nvidia-docker 2.0
COPY nvidia-docker $DIST_DIR/nvidia-docker
COPY daemon.json $DIST_DIR/daemon.json

WORKDIR $DIST_DIR
RUN ln -s nvidia-docker/debian/ .

#RUN sed -i "s;@VERSION@;${REVISION};" debian/changelog && \
#    sed -i "s;@VERSION@;${PKG_VERS};" $DIST_DIR/nvidia-docker && \
#
#
#    if [ "$REVISION" != "$(dpkg-parsechangelog --show-field=Version)" ]; then echo "$(dpkg-parsechangelog --show-field=Version)" && exit 1; fi

CMD export DISTRIB="$(lsb_release -cs)" && \
    debuild --preserve-env --dpkg-buildpackage-hook='sh debian/prepare' -i -us -uc -b && \
    mv /tmp/*.deb /dist

RUN apt-get update --fix-missing && \
    apt-get install -y nano git \
    software-properties-common \
    aptitude

RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get install -y python3.7 python3.7-dev python3-pip \
    libsndfile1 libportaudio2 ffmpeg freeglut3 freeglut3-dev \
    libxi-dev libxmu-dev libssl-dev libffi-dev libxml2-dev \
    libxslt1-dev zlib1g-dev

RUN aptitude install -y nvidia-cuda-dev

ADD Real-Time-Voice-Cloning /opt/Real-Time-Voice-Cloning
#ADD cuda_11.1.1_455.32.00_linux.run /opt/cuda_11.1.1_455.32.00_linux.run
WORKDIR /opt/Real-Time-Voice-Cloning

RUN python3.7 -m pip install -r requirements.txt
RUN python3.7 -m pip install -r requirements_gpu.txt

CMD [ "/bin/bash" ]
