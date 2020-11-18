'''
Purpose of this file is to
1. get the filtering criteria from the user
2. Filter the database using these filters
'''
import sqlite3

from openings import opening_dict

path_db = "./databases/"
merged_database_name = path_db + 'Merged_Monthlies.db'

def obtain_criteria(openings, force_playerName = True):
    '''
    Filtering Criteria currently:
    1. PlayerName (Then check White or Black)
    2. WhiteElo (Upper and Lower bounds)
    3. BlackElo (Upper and Lower bounds)
    4. GameType (Simply 1 of 4 options)
    5. Opening (Select one of the available options)
    :return: filtering criteria in a dict
    '''

    filter_dict = {
        "input_PlayerName": "",
        "input_WhiteElo_Lower": "",
        "input_WhiteElo_Upper": "",
        "input_BlackElo_Lower": "",
        "input_BlackElo_Upper": "",
        "input_GameType": "",
        "input_Opening": ""
    }

    # ------------------------------------------------------------------------------------------------------------------
    # PlayerName: If playerName is forced, then ENTER is unaccepted. Otherwise anything is accepted.
    if force_playerName:
        while True:
            try:
                filter_dict['input_PlayerName'] = input("Games will be filtered on a Lichess username, so please enter a username here: ")
                if filter_dict['input_PlayerName'] != '':
                    filter_dict['input_PlayerName'] = filter_dict['input_PlayerName']
                    break
            except:
                pass
            print("Invalid entry. A Name must be entered.")
    else:
        filter_dict['input_PlayerName'] = input(
            "If you would like to filter based on a username, type the username. Otherwise just hit ENTER: ")
    # ------------------------------------------------------------------------------------------------------------------
    # WhiteElo_Lower: Verify it is an integer (if float, convert to int). Don't care if user enters negative number.
    while True:
        try:
            filter_dict['input_WhiteElo_Lower'] = input("If you would like to filter based on a lower bound of the "
                                                        "White player's Elo, type that lower bound now. "
                                                        "Otherwise just hit ENTER: ")
            if filter_dict['input_WhiteElo_Lower'] != '':
                filter_dict['input_WhiteElo_Lower'] = int(filter_dict['input_WhiteElo_Lower'])
            break
        except:
            pass
        print("Invalid entry. Integers only.")

    # ------------------------------------------------------------------------------------------------------------------
    # WhiteElo_Upper: Verify it is an integer (if float, convert to int). Verify that if a lower bound is entered,
    # the upper is larger.
    while True:
        try:
            filter_dict['input_WhiteElo_Upper'] = input("If you would like to filter based on an upper bound of the "
                                                        "White player's Elo, type that upper bound now. "
                                                        "Otherwise just hit ENTER: ")
            if filter_dict['input_WhiteElo_Upper'] != '':
                filter_dict['input_WhiteElo_Upper'] = int(filter_dict['input_WhiteElo_Upper'])

                # If there is a value for the lower bound, verify the lower
                if isinstance(filter_dict['input_WhiteElo_Lower'], int):
                    if filter_dict['input_WhiteElo_Lower'] >= filter_dict['input_WhiteElo_Upper']:
                        # This is an error.
                        print("Input Error: White Elo upper bound must be above the White Elo lower bound.")
                        continue
            break
        except:
            pass
        print("Invalid entry. Integers only.")

    # ------------------------------------------------------------------------------------------------------------------
    # BlackElo_Lower: Verify it is an integer (if float, convert to int)
    while True:
        try:
            filter_dict['input_BlackElo_Lower'] = input("If you would like to filter based on a lower bound of the "
                                                        "Black player's Elo, type that lower bound now. "
                                                        "Otherwise just hit ENTER: ")
            if filter_dict['input_BlackElo_Lower'] != '':
                filter_dict['input_BlackElo_Lower'] = int(filter_dict['input_BlackElo_Lower'])
            break
        except:
            pass
        print("Invalid entry. Integers only.")

    # ------------------------------------------------------------------------------------------------------------------
    # BlackElo_Upper: Verify it is an integer (if float, convert to int). Verify that if a lower bound is entered,
    # the upper is larger.
    while True:
        try:
            filter_dict['input_BlackElo_Upper'] = input("If you would like to filter based on an upper bound of the "
                                                        "Black player's Elo, type that upper bound now. "
                                                        "Otherwise just hit ENTER: ")
            if filter_dict['input_BlackElo_Upper'] != '':
                filter_dict['input_BlackElo_Upper'] = int(filter_dict['input_BlackElo_Upper'])

                # If there is a value for the lower bound, verify the lower
                if isinstance(filter_dict['input_BlackElo_Lower'], int):
                    if filter_dict['input_BlackElo_Lower'] >= filter_dict['input_BlackElo_Upper']:
                        # This is an error.
                        print("Input Error: Black Elo upper bound must be above the Black Elo lower bound.")
                        continue
            break
        except:
            pass
        print("Invalid entry. Integers only.")

    # ------------------------------------------------------------------------------------------------------------------
    # GameType: Input must be 0, 1, 2, 3, or simply ''
    while True:
        try:
            filter_dict['input_GameType'] = input("If you would like to filter based on GameType, type the "
                                                  "corresponding number for the GameType of interest - Bullet(0), "
                                                  "Blitz(1), Rapid(2), Classical(3). Otherwise just hit ENTER:")
            if filter_dict['input_GameType'] != '':
                filter_dict['input_GameType'] = int(filter_dict['input_GameType'])
            if filter_dict['input_GameType'] in [0, 1, 2, 3, '']:
                break
        except:
            pass
        print("Invalid entry. Only valid entries are 0, 1, 2, 3, or simply hitting ENTER")

    # ------------------------------------------------------------------------------------------------------------------
    # Opening: Input must be exactly the same as a valid Opening or simply ''. Later will be a pull-down list
    while True:
        try:
            filter_dict['input_Opening'] = input("If you would like to filter based on an Opening, type out the "
                                                 "name exactly (Ex. 'Ruy Lopez'). If you need to see the available "
                                                 "list, type 'help'. Otherwise just hit ENTER: ")
            if filter_dict['input_Opening'] == 'help':
                print(openings)
                continue
            if filter_dict['input_Opening'] in openings or filter_dict['input_Opening'] == '':
                break
        except:
            pass
        print("Invalid entry. Only valid entries are" + str(openings) + " or simply hitting ENTER")

    return filter_dict

def retrieve_db(filters, table_name, path):
    '''
    This function has the capability to filter off many things, not necessarily the username.
    Was in place before retrieve_player_db. Does not adjust result based on player being black or white, and just gives
    the overall score. Good for looking at the database as a whole, but not as good for an individual player.
    :param filters:
    :param table_name:
    :param path:
    :return:
    '''
    half_move_str = ', '.join(path)
    retrieve_db_query = "SELECT AVG(Result), COUNT(*), " + half_move_str + \
                        " FROM " + table_name

    # Statements
    statements_dict = {
        "input_PlayerName": "(WhiteName = '" + filters['input_PlayerName'] + "' OR BlackName = '" + filters['input_PlayerName'] + "')",
        "input_WhiteElo_Lower": "WhiteElo >= " + str(filters['input_WhiteElo_Lower']),
        "input_WhiteElo_Upper": "WhiteElo <= " + str(filters['input_WhiteElo_Upper']),
        "input_BlackElo_Lower": "BlackElo >= " + str(filters['input_BlackElo_Lower']),
        "input_BlackElo_Upper": "BlackElo <= " + str(filters['input_BlackElo_Upper']),
        "input_GameType": "GameType == " + filters['input_GameType']
    }

    nonempty_conditions = {key: val for key, val in filters.items() if val != '' and key != 'input_Opening'}
    for index, key in enumerate(nonempty_conditions):
        if index == 0:
            retrieve_db_query += " WHERE "
        else:
            retrieve_db_query += " AND "

        retrieve_db_query += statements_dict[key]

    # Handle openings similarly, but it needs a loop
    if filters['input_Opening'] != '':
        moves = opening_dict[filters['input_Opening']]
        split_moves = moves.split()
        for index, move in enumerate(split_moves):
            if len(nonempty_conditions) == 0 and index == 0:
                retrieve_db_query += " WHERE "
            else:
                retrieve_db_query += " AND "

            retrieve_db_query += "Half_Move_" + str(index+1) + " == '" + move + "'"

    # Aggregation stuff
    retrieve_db_query += " GROUP BY " + half_move_str

    with sqlite3.connect(merged_database_name) as conn:
        c = conn.cursor()

        # Put a loop here to determine if there are too many results. If so, increase Count requirement by 1.
        count = -1
        num_lines = 1000000
        while num_lines > 20000:
            count += 1
            temp_sql = retrieve_db_query + " HAVING Count > " + str(count)
            db = c.execute(temp_sql).fetchall()
            num_lines = len(db)

    return db

def retrieve_player_db(filters, table_name, path):
    '''
    :param filters:
    :param table_name:
    :param path:
    :return:
    '''

    half_move_str = ', '.join(path)
    retrieve_player_db_query = "SELECT WhiteName, BlackName, Result, " + half_move_str + \
                        " FROM " + table_name

    # Statements
    statements_dict = {
        "input_PlayerName": "(WhiteName = '" + filters['input_PlayerName'] + "' OR BlackName = '" + filters['input_PlayerName'] + "')",
        "input_WhiteElo_Lower": "WhiteElo >= " + str(filters['input_WhiteElo_Lower']),
        "input_WhiteElo_Upper": "WhiteElo <= " + str(filters['input_WhiteElo_Upper']),
        "input_BlackElo_Lower": "BlackElo >= " + str(filters['input_BlackElo_Lower']),
        "input_BlackElo_Upper": "BlackElo <= " + str(filters['input_BlackElo_Upper']),
        "input_GameType": "GameType == " + filters['input_GameType']
    }

    # Applying filters to our SQL statement
    nonempty_conditions = {key: val for key, val in filters.items() if val != '' and key != 'input_Opening'}
    for index, key in enumerate(nonempty_conditions):
        if index == 0:
            retrieve_player_db_query += " WHERE "
        else:
            retrieve_player_db_query += " AND "

        retrieve_player_db_query += statements_dict[key]

    # Handle openings similarly, but it needs a loop
    if filters['input_Opening'] != '':
        moves = opening_dict[filters['input_Opening']]
        split_moves = moves.split()
        for index, move in enumerate(split_moves):
            if len(nonempty_conditions) == 0 and index == 0:
                retrieve_player_db_query += " WHERE "
            else:
                retrieve_player_db_query += " AND "

            retrieve_player_db_query += "Half_Move_" + str(index+1) + " == '" + move + "'"

    with sqlite3.connect(merged_database_name) as conn:
        c = conn.cursor()
        db = c.execute(retrieve_player_db_query).fetchall()

    return db

def get_half_moves(table_name):
    with sqlite3.connect(merged_database_name) as conn:
        c = conn.cursor()
        # Getting column names to determine the number of 'Half Moves' in the database
        table_info = c.execute('PRAGMA table_info(' + table_name + ')').fetchall()

        move_column_names = [column[1] for column in table_info if column[1].startswith("Half_Move")]

        return move_column_names