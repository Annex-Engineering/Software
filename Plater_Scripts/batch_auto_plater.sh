#!/bin/sh

#script.sh height width config_folder

PLATER=./plater
height=$1
width=$2
config_folder=$3

if [[ -d $config_folder ]]
then
for conf in `find $config_folder -iname "*.conf"`
do
    echo "Next: $conf"

		plate_name=${conf##*/}
		plate_name=${plate_name%.*}
		plate_name=${plate_name}"_%02d"

		$"$PLATER" -t 8 -j 0.5 -s 1.5 -r 90 -R 10 -S -d 1.0 -H $height -W $width -o "$plate_name" $conf		
done
fi
