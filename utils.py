import os
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pyodbc


# establish connection to database
def retrieve_database():
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=P:\MAG\Briefbuch\Projektarbeit\Datenbank\Projektdatenbank4_aktuell.accdb;'
    )
    connection = pyodbc.connect(conn_str)
    cursor = connection.cursor()
    return cursor


# get the current time
def retrieve_time():
    # datetime object containing current date and time
    now = datetime.now()
    return str(now)


# make string into soup
def reTEIfy(s, tag):
    newSoup = BeautifulSoup(s, "xml")
    out = newSoup.find(tag)
    assert out is not None
    return out


# modifications to string
def clean_string_basic(str_in):
    text = str_in.replace(u'\u0056\u0308', u'\ue342')
    text = text.replace(u'\u0076\u0308', u'\ue742')
    text = text.replace('å', 'ä')
    text = text.replace(u'\u0065\u0308', '\u00eb')
    text = text.replace(u'\u0045\u0308', '\u00cb')
    text = text.replace("ẅ", "w")
    text = text.replace(u'\u0079\u0308', '\u00ff')
    text = text.replace(u'\u0059\u0308', '\u0178')
    text = text.replace('ÿ', "y")
    text = text.strip()
    assert "&" not in text
    assert "$" not in text
    return text.strip()


# expand boundaries of coordinates by a set margin
def expand_boundaries(pageSoup):
    lower_margin = 20
    upper_margin = 40
    left_margin = right_margin = 10
    for line in pageSoup.findAll("TextLine"):
        line_points = line.Coords["points"]
        new_line_points = ""
        upper_line = []
        lower_line = []
        for point in line_points.split():
            x = int(point.split(',')[0])
            y = int(point.split(',')[1])
            found = False
            radius = 0
            while not found:
                for point2 in line_points.split():
                    if point == point2:
                        continue
                    x2 = int(point2.split(',')[0])
                    y2 = int(point2.split(',')[1])
                    if x == x2 or x == x2 - radius or x == x2 + radius:
                        found = True
                        if y2 > y:
                            upper_line.append((x, y))
                        else:
                            lower_line.append((x, y))
                        break
                radius += 1
        upper_x_max, upper_x_min = find_x_max_min(upper_line)
        lower_x_max, lower_x_min = find_x_max_min(lower_line)
        for x, y in upper_line:
            y -= upper_margin
            if x == upper_x_min:
                x -= left_margin
            if x == upper_x_max:
                x += right_margin
            new_line_points += f"{x},{y} "
        for x, y in lower_line:
            y += lower_margin
            if x == lower_x_min:
                x -= left_margin
            if x == lower_x_max:
                x += right_margin

            new_line_points += f"{x},{y} "
        line.Coords["points"] = new_line_points.strip()


# find max and min for a list of (x,y) coordinates
def find_x_max_min(lst):
    x_values = [x[0] for x in lst]
    x_max = max(x_values)
    x_min = min(x_values)
    return x_max, x_min


# clear directory
def clear_directory(directory_path):
    try:
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)

            if item[-8:] == ".gitkeep":
                continue

            if os.path.isfile(item_path):
                # If it's a file, remove it
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                # If it's a directory, remove it recursively
                clear_directory(item_path)

        # After removing all files and subdirectories, remove the directory itself
        # os.rmdir(directory_path)
        print(f"Directory '{directory_path}' has been cleared.")
    except Exception as e:
        print(f"An error occurred while clearing the directory: {str(e)}")
