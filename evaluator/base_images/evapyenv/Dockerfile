FROM py3-py2
LABEL maintainer="changyua@ualberta.ca"

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
		apt-utils \
		build-essential \
		python3-dev \
		python-dev \
		mesa-common-dev \
		liblapack-dev \
		libopenblas-dev \
		ffmpeg \
		libsdl2-dev \
		libsdl2-image-dev \
		libsdl2-mixer-dev \
		libsdl2-ttf-dev \
		libportmidi-dev \
		libswscale-dev \
		libavformat-dev \
		libavcodec-dev \
		zlib1g-dev \
		python-pyqt5 \
		python-qt4 \
		python3-pyqt4 \
		python3-pyqt5 \
		python-tk \
		python3-tk \
		dpkg-dev \
		python2.7-dev \
		libjpeg-dev \
		libtiff-dev \
		libsdl1.2-dev \
		libgstreamer-plugins-base1.0-dev \
		libnotify-dev \
		freeglut3 \
		freeglut3-dev \
		libsm-dev \
		libgtk-3-dev \
		libwebkitgtk-3.0-dev \
		libxtst-dev \
		python-setuptools \
		python-pygame \
		python-opengl \
		python-enchant \
		libgl1-mesa-dev \
		libgles2-mesa-dev \
		python3-kivy \
		python-kivy \
	&& rm -rf /var/lib/apt/lists/*

#Python3 packages
COPY packages-py3.txt /
RUN pip3 install Cython #Required by kivy
RUN pip3 install -r /packages-py3.txt

#Python2 packages
RUN apt-get update && apt-get install -y --no-install-recommends \
		cmake \
		qt4-qmake \
		libqt4-dev \
	&& rm -rf /var/lib/apt/lists/*
COPY packages-py2.txt /
RUN pip2 install Cython #Required by kivy
RUN pip2 install -r /packages-py2.txt


CMD tail -f /dev/null
