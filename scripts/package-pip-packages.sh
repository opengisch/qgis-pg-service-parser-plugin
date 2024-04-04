#!/usr/bin/env bash

LIBS_DIR="pg_service_parser/libs"

echo download and unpack pgserviceparser
#create temp folder
mkdir -p temp
#download the wheel
pip download -v pgserviceparser --only-binary :all: -d temp/
#unpack all the wheels found (means including dependencies)
unzip -o "temp/*.whl" -d $LIBS_DIR
#remove temp folder
rm -r temp
#set write rights to group (because qgis-plugin-ci needs it)
chmod -R g+w $LIBS_DIR

#create the __init__.py in libs folder
cd $LIBS_DIR
touch __init__.py
chmod g+w __init__.py
