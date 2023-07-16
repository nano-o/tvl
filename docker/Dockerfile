FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get --yes update \
  && apt-get install --yes \
  curl \
  git \
  sudo \
  unzip \
  wget \
  aptitude \
  build-essential \
  python3 \
  pip \
  vim \
  nano \
  && apt-get clean

ARG USERNAME=user
ENV USERNAME=${USERNAME}
ARG USER_UID=1000
ENV USER_UID=${USER_UID}
ARG USER_GID=${USER_UID}
ENV USER_HOME=/home/${USERNAME}

RUN (groupadd --gid=${USER_GID} ${USERNAME} || true) \
  && (useradd --shell=/bin/bash --uid=${USER_UID} --gid=${USER_GID} --create-home ${USERNAME} || true) \
  && echo "${USERNAME}  ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USERNAME}
WORKDIR ${USER_HOME}

RUN git clone https://github.com/nano-o/tvl.git
# pip installs stuff in ~/.local/bin/, so we put in in our PATH
ENV PATH=/home/user/.local/bin/:$PATH
RUN pip install pysmt requests
RUN pysmt-install --z3 --confirm-agreement

WORKDIR ${USER_HOME}/tvl/
CMD python3 check_stellar_network.py
