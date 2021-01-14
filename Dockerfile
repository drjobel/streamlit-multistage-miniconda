# Inspiration source: https://www.rockyourcode.com/run-streamlit-with-docker-and-docker-compose/
# https://pythonspeed.com/articles/conda-docker-image-size/

###############
# BASE IMAGE #
###############

FROM ubuntu:focal-20201106 as ubuntubase
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Stockholm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

    
# builder-base is used to build dependencies

RUN apt-get update --fix-missing && \
    apt-get install --no-install-recommends -y \
    locales tzdata \
    python3-pip libgdal-dev \
    curl \
    build-essential \
    libxml2-dev \
    gcc python3-dev\
    wget bzip2 ca-certificates \
    # required by psycopg2
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set python aliases for python3
RUN echo 'alias python=python3' >> ~/.bashrc
RUN echo 'alias pip=pip3' >> ~/.bashrc

# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# This will install latest version of GDAL
RUN pip3 install GDAL==3.0.4

###############
# BUILD IMAGE #
###############
FROM ubuntubase AS builderbase

ENV CONDA_ENV_NAME = aqua
ENV PATH /opt/conda/bin:$PATH 

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate $CONDA_ENV_NAME" >> ~/.bashrc

# Install the package as normal
RUN conda update -n base -c defaults conda
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "aqua", "/bin/bash", "-c"]

# Activate the environment, and make sure it's activated:
RUN echo "conda activate aqua" > ~/.bashrc
# RUN pip install pyimpute  
# handsdown

# Use conda pack to create a standalone environment
# in /venv:

RUN conda-pack -n aqua -o /tmp/env.tar && \ 
    mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar 

# We have put `venv` in the same path it will be in the final image,
# so now fix up paths:

RUN /venv/bin/conda-unpack


#################
# RUNTIME IMAGE #
#################

# The runtime-stage image; we can use `Debian` or `Ubuntu`as the
# base image since the Conda env also includes Python
FROM ubuntu:focal-20201106 AS runtime

# setup user and group ids
ARG USER_ID=1000
ENV USER_ID $USER_ID
ARG GROUP_ID=1000
ENV GROUP_ID $GROUP_ID

# add non-root user and give permissions to workdir
RUN groupadd --gid $GROUP_ID user && \
    adduser user --ingroup user --gecos '' --disabled-password --uid $USER_ID && \
    mkdir -p /usr/src/app && \
    chown -R user:user /usr/src/app

# Copy `/venv` from the previous stage
COPY  --chown=user:user --from=builderbase /venv /venv


# set working directory
WORKDIR /usr/src/app

# switch to non-root user
USER user

# disables lag in stdout/stderr output
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
# Path
ENV PATH="/venv/bin:$PATH"

# When image is run, run the code with the environment activated
SHELL ["/bin/bash", "-c"]
ENTRYPOINT source /venv/bin/activate && \
   streamlit run project/app.py


