import mysql.connector

def retrieve_player_db(parameters, db_config):
    # Two Table Names are:
    # 'Games_classical' and 'Games_rapid'

    aws_conn = mysql.connector.connect(**db_config)
    db_cursor = aws_conn.cursor()
    # Begin using this database
    db_name = 'Chess_Games'
    db_cursor.execute(f"USE {db_name}")

    select_statement = "SELECT *"
    filter_statement = f" WHERE {parameters['PlayerColor']}Name = '{parameters['PlayerName']}'"
    rapid_statement = select_statement + " FROM Games_rapid" + filter_statement
    classical_statement = select_statement + " FROM Games_classical" + filter_statement

    if parameters["Rapid_Games"] == True and parameters["Classical_Games"] == True:
        sql_query = rapid_statement + " UNION ALL " + classical_statement
    elif parameters["Rapid_Games"] == True and parameters["Classical_Games"] == False:
        sql_query = rapid_statement
    elif parameters["Rapid_Games"] == False and parameters["Classical_Games"] == True:
        sql_query = classical_statement
    elif parameters["Rapid_Games"] == False and parameters["Classical_Games"] == False:
        print("Error Code 2: No GameType Selected")
        return []

    db_cursor.execute(sql_query)
    data = db_cursor.fetchall()

    return data