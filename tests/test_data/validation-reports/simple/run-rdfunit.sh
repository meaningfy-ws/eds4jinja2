#!/bin/bash

DATA_FOLDER=`pwd`
CONTAINER_DATA_FOLDER=/mnt/data
DATA_FILE=$CONTAINER_DATA_FOLDER/shacl.example.data.ttl
SHAPE_FILE=$CONTAINER_DATA_FOLDER/shacl.example.shapes.ttl


docker run -v $DATA_FOLDER:${CONTAINER_DATA_FOLDER}  --rm -it aksw/rdfunit -d $DATA_FILE -u $DATA_FILE  -s $SHAPE_FILE -r shacl -o html,ttl -f $CONTAINER_DATA_FOLDER/

#docker run -v $DATA_FOLDER:$CONTAINER_DATA_FOLDER  --rm -it  --entrypoint bash aksw/rdfunit