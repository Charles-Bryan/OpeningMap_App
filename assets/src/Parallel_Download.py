# Purpose of this is to fully parse and clean a pgn file and save it into a new SQL table
import re
from os import listdir, path
import sqlite3
import mysql.connector
import pandas as pd
import pymysql
import math
import urllib.request
from datetime import date
import bz2
import time

download_path = "./downloaded_files/"

def shorten_filename(filename):
    try:
        short_name = re.search('[0-9]{4}-[0-9]{2}', filename).group()
        short_name = re.sub(pattern='-', repl="_", string=short_name)
        return short_name
    except:
        print("Trouble extracting shortened filename")

if __name__ == "__main__":
    today = date.today().strftime("%m-%d-%Y")

    # Get the list of files to download
    # file_list_website_url = "https://database.lichess.org/standard/list.txt"
    # urllib.request.urlretrieve(file_list_website_url, f"./downloaded_files/file_list_{today}.txt")
    # for file_url in reversed(open(f"./downloaded_files/file_list_{today}.txt").readlines()):

    for file_url in reversed(open(f"./downloaded_files/adjusted_list.txt").readlines()):

        # check # of bz2 files. If under 2, download.
        # Otherwise, wait. So need a While True loop or something and a 5 minute wait.
        while True:
            already_downloaded = [zip_file for zip_file in listdir(download_path) if zip_file.split('.')[-1] == "bz2"]
            if len(already_downloaded) < 2:
                # For each file in the list, download it, parse it, save it, delete it locally
                short_filename = f"Games_{shorten_filename(file_url)}"
                downloaded_filename = f"./downloaded_files/{short_filename}.bz2"

                print(f"Downloading {short_filename}")
                start_time = time.time()
                urllib.request.urlretrieve(file_url, downloaded_filename)
                print(f"Download took {round((time.time() - start_time)/60, 1)} minutes")
                break
            else:
                time.sleep(60)