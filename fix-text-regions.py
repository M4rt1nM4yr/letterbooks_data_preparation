import os
from bs4 import BeautifulSoup
import numpy as np

target_dir = "diplomatic-regularised"
# for all collections
for i in range(2, 6):
    dir_path = f"{target_dir}/Band{i}"
    # for all letters
    for file in os.listdir(dir_path):
        # open letter with BeautifulSoup
        with open(f"{dir_path}/{file}", 'r', encoding='utf-8') as xml_file:
            soup = BeautifulSoup(xml_file, 'xml')
            # for all textregions in letter
            for textregion in soup.findAll("TextRegion"):
                # remove textregions that do not have any lines
                if not textregion.find("TextLine"):
                    textregion.decompose()
                    continue
                # calculate minimum and maximum x and y values for textregion
                y_min = np.inf
                x_min = np.inf
                y_max = -np.inf
                x_max = -np.inf
                for line in textregion.findAll("TextLine"):
                    lineCoords = line.find("Coords")["points"].split(' ')
                    for el in lineCoords:
                        x = int(el.split(',')[0])
                        y = int(el.split(',')[1])
                        if x < x_min:
                            x_min = x
                        if x > x_max:
                            x_max = x
                        if y < y_min:
                            y_min = y
                        if y > y_max:
                            y_max = y
                points_att = f"{x_min},{y_min} {x_min},{y_max} {x_max},{y_max} {x_max},{y_min}"

                # if points differ from before, correct entry in tei
                points_before = textregion.find("Coords")["points"]
                if points_before == points_att:
                    continue
                else:
                    textregion.find("Coords")["points"] = points_att
        # write tei
        with open(f"{dir_path}/{file}", 'w', encoding='utf-8') as xml_file:
            xml_file.write(str(soup))
