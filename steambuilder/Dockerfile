FROM ubuntu:18.04

RUN set -xe

ENV HOME /src
ENV DEBIAN_FRONTEND noninteractive
ENV TERM=xterm

WORKDIR /usr/local/src
RUN apt-get -qqy update
RUN apt-get -qqy install wget build-essential git libreadline-dev
RUN apt-get install -y python3 python3-pip libc-bin binutils zlib1g
RUN pip3 install pygame==2.0.1
RUN pip3 install "numpy==1.13.3"
RUN pip3 install cython
RUN pip3 install setuptools
RUN pip3 install steam[client]
RUN pip3 install pyinstaller==4.3
RUN pip3 install yapf







