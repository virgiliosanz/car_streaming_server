#!/bin/bash
# run this as the root user!

WDIR="/home/pi/Develop/car_streaming_server"
VIRTUALENV_DIR="$WDIR/pyenv"

source $VIRTUALENV_DIR/bin/activate

cd $WDIR
python app.py
