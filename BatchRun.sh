#!/bin/bash

# This sript is used to generate PPAFM images 
# ---------------- NOTICE!!! ----------------
# Before runing this script, run these
# three commands to enter the virtual env first
# 0. pip install --user pipenv
# 1. pipenv sync
# 2. pipenv shell
#
# Usage:   ./BatchRun.sh <structure1> <structure2> ...
# Example: ./BatchRun.sh QS_PRt QSm_PRt PR_QS QS_QSmt
# -------------------------------------------

InputsPath=BatchInputs
OutputsPath=BatchOutputs
TempPath=BatchTemplates
BakupPath=BatchBakup

##############################
## Obtain Input Data
##############################
mahtiPath=/scratch/mkaukone1/jie/Github/WaterOnCalcite/src/03_applications
mkdir -p $InputsPath 
for structure in "$@"
do
	zipfile="${InputsPath}/${structure}_s6.zip"
	if [ ! -f "$zipfile" ]; then
		echo Downloading $structure ...
		scp huangjie@mahti.csc.fi:$mahtiPath/$structure/${structure}_s6.zip $InputsPath/
	else
		echo "$zipfile already exists, skipping download."
	fi
done

#######################################
# Function to check the runner status
#######################################
check_status_and_run() {
    local database=$1
    local interval=$2

    while true; do
        # Run the command and extract the status using awk
        local status=$(runner status -db "$database" 1 | awk '/1/{print $NF}')
        if [[ $status == "done" ]]; then
            echo "Status is done. Proceeding with the next commands."
            # Insert your commands here
	    #runner stop -db ${database} 1
	    runner remove-runner -db ${database} --force terminal:PPM
            break
        else
            echo "Status is $status. Waiting for it to become done..."
            sleep $interval
        fi
    done
}

RePath=${OutputsPath}/RelativeHeightWithRotation
RawPath=${OutputsPath}/RawData
mkdir -p ${RePath}  ${RawPath}
mkdir -p ${BakupPath}

for structure in "$@"
do
	echo Step 0: Preparing inputs of  $structure ...
	rm -rf data # Folder data is the default input folder of this workflow
	unzip -o ${InputsPath}/${structure}_s6.zip -d ${InputsPath}/
	mv ${InputsPath}/${structure}_s6 data

	echo Step 1: Creating a database ..
	rm -f database.db # Remove previous one to avoid errors
	./${TempPath}/1_step1.py

	echo Step 2: Running ppafm in terminal ...
	runner start -db database.db  terminal:PPM > temp.log &
	# Wait until the end
	check_status_and_run database.db 60

	echo Step 3: Getting numpy array ...
	./${TempPath}/2_step2.py

	echo Step 4: Create relative images
	cp ${TempPath}/Images.py Images/
        cd Images
		./Images.py ${structure}_s6
		rm Images.py
	cd ..	
	mv Images/${structure}_s6.vasp ${RePath}/${structure}.vasp
	mv Images/${structure}_s6.npy ${RePath}/${structure}.npy
	mv Images/${structure}_s6 ${RePath}/${structure}

	echo Step 5: Create raw images
	./${TempPath}/genRaw.sh
	mv 1/Qo-0.12Qc0.21K0.09/Amp7.00 ${RawPath}/${structure} 
	rm ${RawPath}/${structure}/df.xsf # Remove this large file

	echo Step 6: Bakup ...
	mv 1 ${BakupPath}/${structure} 
done

# Zip files

