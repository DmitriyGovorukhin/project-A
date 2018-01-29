#!/usr/bin/env bash

gst-launch-1.0 v4l2src ! 'video/x-raw, width=1280, height=720, framerate=30/1' ! videoconvert ! x264enc pass=qual quantizer=20 tune=zerolatency ! rtph264pay ! udpsink host=127.0.0.1 port=8004