#!/bin/sh

if ! which pip > /dev/null; then
	echo "Installing PIP..."
	sudo apt-get -y install python-pip
fi

echo "Installing markdown2..."
sudo pip install markdown2

echo "Initializing submodules..."
git submodule init
git submodule update

echo "Done."