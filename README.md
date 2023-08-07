# DJI_DB2CSV


Python script to extract metadata from a db file in the DJI device's recording file directory and export it as a CSV file

从DJI设备录制文件目录中的db文件提取metadata并导出CSV的脚本

## Prerequisites
- Python 3.10+

## How to use
For most cases, just run a simple line in terminal .
csv file will export at `DB_file directory / Reel_Name directory`
```
python dji_db2csv.py -f /Path/To/DB/File -c
```
use `-c/-combine` it will combine selet metadata from table in db file into one csv file 

if you do not want to export every table in db file as a csv file, just want a single csv file, use `-oc/-onlyCombine`

>⚠️using script with a DJI mavic drone, add `-mavic` 