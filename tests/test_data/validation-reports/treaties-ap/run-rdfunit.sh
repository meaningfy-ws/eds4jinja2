#!/bin/bash

DATA_FILE=`pwd`/treaties-2019-01-28-nal-src-ap.rdf
SHAPE_FILE=`pwd`/skosShapes.shapes.ttl
DATA_FOLDER=`pwd`/data
mkdir -p $DATA_FOLDER

docker run --rm -it aksw/rdfunit -d $DATA_FILE -u $DATA_FILE  -s $SHAPE_FILE -f $DATA_FOLDER
