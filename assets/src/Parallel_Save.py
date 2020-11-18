import re
from os import listdir, path, remove
import sqlite3
import mysql.connector
import pandas as pd
import pymysql
import math
import urllib.request
from datetime import date
import bz2
import time
import csv

download_path = "./downloaded_files/"

def shorten_filename(filename):
    try:
        short_name = re.search('[0-9]{4}-[0-9]{2}', filename).group()
        short_name = re.sub(pattern='-', repl="_", string=short_name)
        return short_name
    except:
        print("Trouble extracting shortened filename")

def save_data_aws(data, num_moves, filename):

    db_config = {
        'user': 'admin',
        'password': '1AWSpass!',
        'host': 'chess-visual-instance.ckfjtpsuvx0s.us-east-1.rds.amazonaws.com',
        'raise_on_warnings': True
    }
    db_name = 'Chess_Games'

    # first, dynamically create the half move columns each with a max of 6 characters: gxf1=Q+
    move_col_table_query = ""
    move_col_query = ""
    for i in range(1, num_moves * 2 + 1):
        if i < num_moves * 2:
            move_col_table_query += "Half_Move_" + str(i) + " VARCHAR(7) NULL, "
            move_col_query += "Half_Move_" + str(i) + ", "
        else:
            move_col_table_query += "Half_Move_" + str(i) + " VARCHAR(7) NULL"
            move_col_query += "Half_Move_" + str(i)
    col_names = ['WhiteName', ' BlackName', 'Result'] + move_col_query.split(', ')

    aws_conn = mysql.connector.connect(**db_config)

    # db_cursor = aws_conn.cursor(buffered=True)
    db_cursor = aws_conn.cursor()

    # Create database if it does not already exist
    db_cursor.execute("SET sql_notes = 0;")
    create_db_stmt = f"CREATE DATABASE IF NOT EXISTS {db_name};"
    db_cursor.execute(create_db_stmt)
    db_cursor.execute("SET sql_notes = 1;")

    # Begin using this database
    db_cursor.execute(f"USE {db_name}")

    gametype_mapping = {
        # 0: "bullet", # Commenting out bullet because I want to reduce games/storage
        # 1: "blitz", # Commenting out bullet because I want to reduce games/storage
        2: "rapid",
        3: "classical"
    }
    for key in gametype_mapping:
        game_data = [(games[:3] + games[4:]) for games in data if games[3] == key]

        # Parse the filename to get a year and month
        table_name = f"Games_{gametype_mapping[key]}"

        # Check if table exists already
        table_exists_stmt = (
            f"SELECT COUNT(*) "
            f"FROM information_schema.tables "
            f"WHERE table_schema = '{db_name}'"
            f"AND table_name = '{table_name}';"
        )
        db_cursor.execute(table_exists_stmt)
        if db_cursor.fetchall()[0][0] == 1:
            # Table already exists, now check if these games have already been inserted.
            for game_num in range(0, 3):
                # Check the first three games

                game_exists = f"SELECT * FROM {table_name} WHERE "
                for index, element in enumerate(game_data[game_num]):
                    element_term = f'"{element}"' if isinstance(element, str) else element
                    game_exists += f"{col_names[index]} = {element_term}"
                    if index + 1 != len(game_data[game_num]):
                        game_exists += " AND "

                db_cursor.execute(game_exists)
                if len(db_cursor.fetchall()) == 0:
                    # print("These Games have not been seen before.")
                    break
            else:
                print("Games Have been seen before.")
                continue  # only executed if the inner loop did NOT break

        # Create table if it does not already exists
        else:
            create_table_stmt = (
                f"CREATE TABLE {str(table_name)}("
                f"WhiteName VARCHAR(28) NOT NULL, "
                f"BlackName VARCHAR(28) NOT NULL, "
                f"Result DECIMAL(3, 1) NOT NULL, "
                f"{move_col_table_query});"
            )
            db_cursor.execute(create_table_stmt)

        # Insert the data in Batch Inserts
        batch_size = 50000
        num_lines = len(game_data)

        lower_bound = 0
        upper_bound = batch_size
        while True:
            print(f"{filename}_{gametype_mapping[key]}: Starting batch {upper_bound / batch_size} of {math.ceil(num_lines/batch_size)}.")
            i_stmt = f'INSERT INTO {table_name} (WhiteName, BlackName, Result, Half_Move_1, Half_Move_2, Half_Move_3, Half_Move_4, Half_Move_5, Half_Move_6, Half_Move_7, Half_Move_8, Half_Move_9, Half_Move_10, Half_Move_11, Half_Move_12, Half_Move_13, Half_Move_14, Half_Move_15, Half_Move_16, Half_Move_17, Half_Move_18, Half_Move_19, Half_Move_20) VALUES {str(list(map(tuple, game_data[lower_bound:upper_bound])))[1:-1]}'
            db_cursor.execute(i_stmt)

            if upper_bound >= num_lines:
                break

            lower_bound = upper_bound
            upper_bound += batch_size


    aws_conn.commit()
    aws_conn.close()

if __name__ == "__main__":
    today = date.today().strftime("%m-%d-%Y")
    num_moves = 10
    # Get the list of files to download
    # file_list_website_url = "https://database.lichess.org/standard/list.txt"
    # urllib.request.urlretrieve(file_list_website_url, f"./downloaded_files/file_list_{today}.txt")
    # for file_url in reversed(open(f"./downloaded_files/file_list_{today}.txt").readlines()):

    for file_url in reversed(open(f"./downloaded_files/adjusted_list3.txt").readlines()):

        # check # of csv files.
        # Otherwise, wait. So need a While True loop or something and a 5 minute wait.
        while True:
            csv_files = [csv_file for csv_file in listdir(download_path) if csv_file.split('.')[-1] == "csv"]
            if len(csv_files) == 0:
                time.sleep(60)
            else:
                # Looking for "Games_YYYY_MM.csv"
                desired_file = f"Games_{shorten_filename(file_url)}.csv"
                if desired_file in csv_files:
                    time.sleep(6)
                    with open(f"./downloaded_files/{desired_file}", newline='') as f:
                        reader = csv.reader(f)
                        data_array = list(reader)

                    # Data is read in as all strings. 2 columns are numeric.
                    fixed_data = [(game[:2] + [float(game[2])] + [int(game[3])] + game[4:]) for game in data_array]
                    # save it, delete it
                    short_filename = f"Games_{shorten_filename(file_url)}"

                    start_time = time.time()
                    print(f"Saving {short_filename}")
                    save_data_aws(fixed_data, num_moves, short_filename)
                    print(f"Saving took {round((time.time() - start_time)/60, 1)} minutes")

                    remove(f"./downloaded_files/{desired_file}")
                    break

                else:
                    print(f"Expecting file: {desired_file}. Instead file {csv_files[0]} found.")
                    time.sleep(300)
                    pass
