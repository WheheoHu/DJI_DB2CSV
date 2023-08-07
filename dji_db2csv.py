import argparse
import csv
from os import path
import re
import sqlite3
from typing import List

DJI_REEL_REGEX = re.compile(r'([A-Z][0-9]{3}_[A-Z0-9]{4})')


def dji_csv_export(db_file_path: str, combine_export: bool = False, only_combine: bool = False, is_mavic: bool = False):

    database_file_path, database_full_name = path.split(db_file_path)
    database_name = path.splitext(database_full_name)[0]

    con = sqlite3.connect(db_file_path)
    con.text_factory = str
    cur = con.cursor()
    #table_names=cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = ['gis_info_table', 'video_info_table', 'combine']
    gis_select_col_names = ['ID', 'file_name', 'uuid', 'video_index']
    video_select_col_names = ['ID', 'frame_num',
                              'project_frame', 'project_frame_num']

    db_data = {table: [] for table in table_names}

    def combine_csv_ouput(gis_cols: List[str], video_cols: List[str]):

        # slect data col from table
        def select_data(table_name: str, select_cols: List[str]) -> List:
            _list = []
            col_index_list = [idx for idx, x in enumerate(
                db_data[table_name][0]) if x in select_cols]
            for data in db_data[table_name][1]:
                select_data = [data[idx] for idx in col_index_list]
                _list.append(select_data)
            return _list

        # for different project frame name in database
        _index = db_data['video_info_table'][0].index('project_frame')
        if db_data['video_info_table'][1][0][_index] == 0:
            video_cols.remove('project_frame')
        else:
            video_cols.remove('project_frame_num')

        # Use regex find reel name from file name
        if is_mavic:
            reel_name = "MAVIC_REEL"
        else:
            file_name_index = db_data['gis_info_table'][0].index('file_name')
            file_name_eg_str = db_data['gis_info_table'][1][0][file_name_index]

            reel_name_match = DJI_REEL_REGEX.findall(file_name_eg_str)
            reel_name = reel_name_match[0]

        db_data['combine'].append(gis_cols+video_cols[1:])
        gis_select_data = select_data('gis_info_table', gis_cols)
        video_selet_data = select_data('video_info_table', video_cols[1:])
        combine_data = []

        # combie select data
        for idx in range(len(gis_select_data)):
            combine_data.append(
                tuple(gis_select_data[idx]+video_selet_data[idx]))

        db_data['combine'].append(combine_data)

        with open(f"{database_file_path}/{reel_name}.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(db_data['combine'][0])
            writer.writerows(db_data['combine'][1])
            print(f"{database_file_path}/{reel_name}.csv")

    def csv_output(table_name: str):
        with open(f"{database_file_path}/{table_name}_output.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(db_data[table_name][0])
            writer.writerows(db_data[table_name][1])
            print(f"{database_file_path}/{table_name}_output.csv")

    for table in table_names:
        if table == 'video_info_table':
            if is_mavic:
                
                true_frame_num_list = cur.execute(
                    f"SELECT frame_num FROM {table} WHERE duration IS 0 AND shutter_integer IS NOT 0").fetchall()
                project_frame_num=cur.execute(
                    f"SELECT frame_num FROM {table} WHERE duration IS NOT 0 AND shutter_integer IS NOT 0").fetchall()
                data = cur.execute(
                    f"SELECT * FROM {table} WHERE duration IS NOT 0 AND shutter_integer IS NOT 0").fetchall()
                
                
                for index in range(len(data)):
                    _data=list(data[index])
                    _frame_rate=list(true_frame_num_list[index])
                    _project_frame_num=list(project_frame_num[index])
                    
                    _data[2]=_frame_rate[0]
                    _data[22]=_project_frame_num[0]
                    
                    data[index]=tuple(_data)
                    true_frame_num_list[index]=tuple(_frame_rate)
                    project_frame_num[index]=tuple(_project_frame_num)
                    
            else:
                data = cur.execute(
                    f"SELECT * FROM {table} WHERE duration IS NOT 0 AND duration IS NOT -1").fetchall()

        elif table == 'gis_info_table':
            data = cur.execute(
                f"SELECT * FROM {table} WHERE file_name NOT LIKE '%LRF%'").fetchall()
        else:
            continue

        data_names = [description[0] for description in cur.description]
        db_data[table].append(data_names)
        db_data[table].append(data)
        if only_combine is False:
            csv_output(table)

    if combine_export is True:
        combine_csv_ouput(gis_select_col_names, video_select_col_names)


if __name__ == "__main__":
    paser = argparse.ArgumentParser("DJI Database to csv by wheheohu")

    paser.add_argument('-filePath', '-f', required=True,
                       help='database file path')
    paser.add_argument('-combine', '-c', action='store_true',
                       help='combile csv output')
    paser.add_argument('-onlyCombine', '-oc', action='store_true',
                       help='only combile csv output')
    paser.add_argument('-mavic', action='store_true',
                       default=False, help='for mavic db')
    args = paser.parse_args()

    db_file_path = args.filePath
    is_combile = args.combine

    is_only_combile = args.onlyCombine
    if is_only_combile is True:
        is_combile = True
    dji_csv_export(db_file_path=db_file_path,
                   combine_export=is_combile, only_combine=is_only_combile, is_mavic=args.mavic)
