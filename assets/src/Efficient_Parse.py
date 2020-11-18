# Purpose of this is to fully parse and clean a pgn file and save it into a new SQL table
import re
from os import listdir, environ, remove
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

path_pgn = "./pgn_files/"
path_db = "./databases/"
database_name = path_db + 'Lichess_Monthly_parse.db'
database_name2 = path_db + 'Chess_Games.db'

def valid_lichess_name(name, verbose=True):
    '''Rules for a valid Lichess name:
    1. 28 characters or less
    2. Only letters, numbers, hyphens, underscores
    :param name: WhiteName or BlackName
    :return: boolean. True if valid, False if invalid'''
    if len(name) <= 20 and re.match("^[A-Za-z0-9_-]+$", name):
        return True
    else:
        if verbose:
            print("Invalid Name:", name)
        return False

def convert_result(result_text, verbose=True):
    if result_text == '0-1':
        return 0  # Black win
    elif result_text == '1-0':
        return 1  # White win
    elif result_text == '1/2-1/2':
        return 0.5  # Draw
    else:
        if verbose:
            print("Invalid Result:", result_text)
        return 'invalid result'

def convert_elo(elo, verbose=True):
    '''Rules for a valid elo:
    1. positive integer under 5000
    :param elo: White or Black Elo
    :return: elo as integer. '''
    try:
        elo = int(elo)
    except:
        if verbose:
            print("Invalid Elo:", elo)
        return 'invalid elo'

    if elo>0 and elo<5000:
        return elo
    else:
        return 'invalid elo'

def convert_timeControl(timeControl, verbose=True):
    # Verify minutes '+' Increment
    split_time = timeControl.split('+')
    if len(split_time)!=2:
        if verbose:
            print("Invalid Gametype:", timeControl)
        return 'invalid gametype'

    # Verify integer
    try:
        seconds = int(split_time[0])
    except:
        if verbose:
            print("Invalid Gametype:", timeControl)
        return 'invalid gametype'

    if seconds < 180:
        return 0  # bullet
    elif seconds < 480:
        return 1  # blitz
    elif seconds < 1500:
        return 2  # rapid
    else:
        return 3  # classical

def convert_moves(moves, num_moves, min_moves, verbose=True):
    try:
        # Check number of moves
        if moves.count(".") < min_moves:
            return "invalid moves"
        # First removing move numbers
        moves = re.sub('[0-9]+\. ', '', moves)
        # Add space at the end so number of spaces corresponds to number of half_moves
        moves = moves + " "
        # Extracting first [num_moves] of moves
        moves = re.sub('[0-9]+\. ', '', moves)

        moves = ' '.join(moves.split(' ', 2 * num_moves)[:2 * num_moves])
        moves = moves.split()
        temp_num = 2 * num_moves - len(moves)
        moves.extend([''] * temp_num)

        return moves
    except:
        print("Issue with Moves:", moves)
        return "invalid moves"

def parse_pgn(filename, num_moves, min_moves, verbose=True):

    pgn_keep_dict = {
        "[White": 0,
        "[Black": 1,
        "[Result": 2,
        "[TimeControl": 3,
        "Moves_Here": 4
    }
    pgn_filter_out = ["[Event", "[Site", "[UTCDate", "[UTCTime", "[WhiteRatingDiff", "[BlackRatingDiff", "[WhiteTitle",
                      "[BlackTitle", "[ECO", "[Opening", "[Termination", '[LichessId', "[WhiteElo", "[BlackElo",
                      "[Date", "[Round"]
    bad_rows = [" 0-1\n", " 1-0\n", " 1/2-1/2\n", " *\n"]

    num_columns = len(pgn_keep_dict)
    blank_list = ["missing"] * num_columns

    data = []
    current_list = blank_list[:]

    ext = file_url.split('.')[-1].split('\n')[0]
    if ext == 'bz2':
        file = bz2.open(filename)
    else:
        file = open(filename)

    line = " "
    while line:
        ''' Process within loop
        1. Read in a singe line
        2. Extract starting sequence
        3. If line is one of our compatible ones then save data
        4. Otherwise just ignore the data
        5. If a "bad row" comes up then remove the row
        6. Clean data
        7. Append data
        '''

        line = file.readline()
        if ext == 'bz2':
            line = line.decode('utf-8')
        line_start = line.split(' ')[0]
        if line_start in pgn_keep_dict:
            current_list[pgn_keep_dict[line_start]] = line[line.find(" \"") + 2:line.find("\"]")]
            continue
        if line_start in pgn_filter_out:
            continue
        elif line_start == "\n":  # Covers empty lines and move lines with just results
            continue
        elif line_start == "1.":
            # remove comp analysis and clock timings
            line_clean = re.sub(r'{[^}]*} ', '', line)
            # remove additional move #'s brought about from comp analysis
            line_clean = re.sub(r'[0-9]*\.\.\. ', '', line_clean)
            # remove question marks and exclamation marks
            line_clean = re.sub(r'[?!]', '', line_clean)
            # remove final result
            line_clean = re.sub(r' (1/2|0|1)-(1/2|0|1)\n', '', line_clean)
            current_list[pgn_keep_dict["Moves_Here"]] = line_clean

            # All fields have been completed and we need to clean the data before appending it

            # Column 1: Validate WhiteName
            if not valid_lichess_name(current_list[0], verbose=verbose):
                current_list = blank_list[:]
                continue
            # Column 2: Validate BlackName
            if not valid_lichess_name(current_list[1], verbose=verbose):  # BlackName
                current_list = blank_list[:]
                continue
            # Column 3: Convert Result to a digit
            current_list[2] = convert_result(current_list[2], verbose=verbose)
            if current_list[2] == 'invalid result':
                current_list = blank_list[:]
                continue
            # # Column 4: Convert WhiteElo to an integer
            # current_list[3] = convert_elo(current_list[3], verbose=verbose)
            # if current_list[3] == 'invalid Elo':
            #     current_list = blank_list[:]
            #     continue
            # # Column 5: Convert BlackElo to an integer
            # current_list[4] = convert_elo(current_list[4], verbose=verbose)
            # if current_list[4] == 'invalid Elo':
            #     current_list = blank_list[:]
            #     continue
            # Column 6: Convert Time_Control to 1 of 4 gametypes- bullet(0), blitz(1), rapid(2), classical(3)
            current_list[3] = convert_timeControl(current_list[3], verbose=verbose)
            if current_list[3] in ['invalid gametype', 0, 1]: # Quick fix to ignore bullet and blitz
                current_list = blank_list[:]
                continue
            # Column 7: Remove games under [min_moves]. Reduce moves to first [num_moves] and give each half move a cell
            moves = convert_moves(current_list[4], num_moves=num_moves, min_moves=min_moves, verbose=verbose)
            if moves == 'invalid moves':
                current_list = blank_list[:]
                continue
            else:
                current_list = current_list[:4] + moves

            data.append(current_list)
            # Reset list
            current_list = blank_list[:]
            continue

        elif line in bad_rows:
            # Reset list
            current_list = blank_list[:]
            continue

        elif len(line) == 0:
            # print("Done parsing ", filename)
            continue

        else:
            print("Unexpected line start: ", line)
            # Reset list
            current_list = blank_list[:]
            continue

    return data

def shorten_filename(filename):
    try:
        short_name = re.search('[0-9]{4}-[0-9]{2}', filename).group()
        short_name = re.sub(pattern='-', repl="_", string=short_name)
        return short_name
    except:
        print("Trouble extracting shortened filename")

def save_data(data, num_moves, filename):

    with sqlite3.connect(database_name) as conn:
        c = conn.cursor()

        # Parse the filename to get a year and month
        table_name = "table_" + shorten_filename(filename)

        # Takes advantage of the fact that every sqlite database has an sqlite_master table to check for table
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + table_name + "'"

        if len(c.execute(query).fetchall()):
            c.execute("DROP TABLE " + table_name)
            # restores memory for easier checking
            c.execute("VACUUM")

        # Create table if it does not exist
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

        create_table_sql = "CREATE TABLE " + str(table_name) + "(" \
                           "WhiteName VARCHAR(28) NOT NULL," \
                           "BlackName VARCHAR(28) NOT NULL," \
                           "Result FLOAT NOT NULL," \
                           "WhiteElo SmallInt NOT NULL," \
                           "BlackElo SmallInt NOT NULL," \
                           "GameType TinyInt NOT NULL," + \
                           move_col_table_query + \
                           ");"
        c.execute(create_table_sql)

        insert_data_statement = "INSERT INTO " + table_name + " (WhiteName, BlackName, Result, WhiteElo, " \
                            "BlackElo, GameType, " + move_col_query + ") VALUES (?, ?, ?, ?, ?, ?" + ', ?' * 2*num_moves + ")"

        c.executemany(insert_data_statement, data)
        conn.commit()

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

download_path = "./downloaded_files/"

if __name__ == "__main__":

    num_moves = 10
    min_moves = 10
    verbose=False
    today = date.today().strftime("%m-%d-%Y")

    # For monitoring time
    start_time = time.time()

    # # # Get the list of files to download
    # file_list_website_url = "https://database.lichess.org/standard/list.txt"
    # urllib.request.urlretrieve(file_list_website_url, f"./downloaded_files/file_list_{today}.txt")
    # for file_url in reversed(open(f"./downloaded_files/file_list_{today}.txt").readlines()):

    for file_url in reversed(open(f"./downloaded_files/adjusted_list2.txt").readlines()):
        while True:
            already_downloaded = [zip_file for zip_file in listdir(download_path) if zip_file.split('.')[-1] == "bz2"]

            # if len(already_downloaded) == 2: # Doesn't get the last file
            if len(already_downloaded) == 1:  # really crappy fix
                cycle_start_time = time.time()
                print(f"Total Minutes Elapsed: {round((time.time() - start_time)/60, 1)}")

                # For each file in the list, download it, parse it, save it, delete it locally
                short_filename = f"Games_{shorten_filename(file_url)}"
                downloaded_filename = f"./downloaded_files/{short_filename}.bz2"

                # print(f"Downloading {short_filename}")
                # urllib.request.urlretrieve(file_url, downloaded_filename)

                print(f"Parsing {short_filename}")
                data_array = parse_pgn(downloaded_filename, num_moves=num_moves, min_moves=min_moves, verbose=verbose)

                with open(f"./downloaded_files/{short_filename}.csv", "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(data_array)

                # print(f"Saving {short_filename}")
                # save_data_aws(data_array, num_moves, short_filename)

                print(f"Deleting {short_filename}")
                remove(downloaded_filename)

                print(f"Cumulative {short_filename} Minutes Elapsed: {round((time.time() - cycle_start_time)/60, 1)}")
                print()
                break
            else:
                time.sleep(300)
