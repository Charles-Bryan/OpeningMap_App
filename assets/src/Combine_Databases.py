'''
Purpose: Merge Monthly Databases into a complete collection.
'''

import sqlite3

path_pgn = "./pgn_files/"
path_db = "./databases/"
merged_database_name = path_db + 'Merged_Monthlies.db'
monthly_database_name = path_db + 'Lichess_Monthly_parse.db'

if __name__ == "__main__":

    with sqlite3.connect(monthly_database_name) as conn:
        # Get the table name from user
        merged_table_name = input("Enter the name for the merged table: ")

        c = conn.cursor()

        # Attach command required to work with both databases
        attach_query = 'ATTACH DATABASE "' + merged_database_name + '" AS merged_db'
        conn.execute(attach_query)

        # Get a list of table names in our monthly database
        tbl_name_query = "SELECT DISTINCT(tbl_name) FROM sqlite_master"
        table_names = c.execute(tbl_name_query).fetchall()

        ## Start assembling our query for a temporary table
        union_query = "CREATE TEMP TABLE ignore_name AS "

        # Add a new column for the count of each sequence of moves
        table_info = c.execute('PRAGMA table_info(' + table_names[0][0] + ')').fetchall()

        # Get all column names that start with Half_Move
        move_column_names = [column[1] for column in table_info if column[1].startswith("Half_Move")]
        half_move_columns = ' || '.join(move_column_names)

        # Generate the sql_query to UNION ALL everything
        union_query += "SELECT *, (" + half_move_columns + ") AS grouped FROM ("

        # Generate the sql_query to UNION ALL everything
        for index, row in enumerate(table_names):
            if index+1 < len(table_names):
                union_query += "SELECT * FROM main." + row[0] + " UNION ALL "
            else:
                union_query += "SELECT * FROM main." + row[0] + ")"

        # Run the query that actually creates the new table
        c.execute(union_query)

        # Get all column names other than 'grouped'
        all_column_names = [("main." + column[1]) for column in table_info if column[1] != "grouped"]
        all_column_columns = ', '.join(all_column_names)

        # Using the temporary table, create a table with an additional column for the count of each opening
        joined_query = "CREATE TABLE merged_db." + merged_table_name + " AS " \
                       "SELECT " + all_column_columns + ", Count " \
                       "FROM ignore_name AS main " \
                       "LEFT JOIN (" \
                            "SELECT COUNT(*) AS Count, grouped " \
                            "FROM ignore_name " \
                            "GROUP BY grouped) AS other " \
                            "ON main.grouped = other.grouped"

        c.execute(joined_query)
        conn.commit()
