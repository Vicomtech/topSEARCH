FROM continuumio/miniconda

RUN apt-get -y update && apt-get -y install build-essential

RUN conda update -n base -c defaults conda

ADD requirements.yml /tmp/requirements.yml
RUN conda env update --file /tmp/requirements.yml

ADD ../.. /opt/project
WORKDIR /opt/project
