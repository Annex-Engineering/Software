#! /bin/bash

#scriptname.sh config_file input_folder output_folder

config=$1
input_folder=$2
output_folder=$3

if [[ -d $input_folder ]]
then
for stl in `find $input_folder -iname "*.stl"`
do
    echo "Next: $stl"
    /Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer --slice --load $config --output $output_folder $stl
done
fi