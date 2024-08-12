#!/usr/bin/env python3
# This script formats celer files in-place

import re
import os
import sys

COORD_2_REGEX = re.compile(r"(\[\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*\])")
COORD_3_REGEX = re.compile(r"(\[\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*\])")

def format_path(path):
    if os.path.isfile(path) and path.endswith(".yaml"):
        format_file(path)
        return
    if os.path.isdir(path):
        for subpath in os.listdir(path):
            subpath = os.path.join(path, subpath)
            format_path(subpath)

def format_file(path):
    formatted = False
    output = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            formatted_line = format_line(line)
            if formatted_line != line:
                formatted = True
            output.append(formatted_line)
    
    if formatted:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(output)
        print(path)

def format_line(line):
    match2 = COORD_2_REGEX.findall(line)
    if match2:
        for match in match2:
            coord_str = match[0]
            formatted_coord = format_coord(coord_str)
            line = line.replace(coord_str, formatted_coord)

    match3 = COORD_3_REGEX.findall(line)
    if match3:
        for match in match3:
            coord_str = match[0]
            formatted_coord = format_coord(coord_str)
            line = line.replace(coord_str, formatted_coord)
    
    return line

def format_coord(coord_str):
    coords = [ round(float(x.strip()), 2) for x in coord_str[1:-1].split(",") ]
    return"[" + ", ".join([str(x) for x in coords]) + "]"

if __name__ == "__main__":
    paths = ["."]
    if len(sys.argv) > 2:
        paths = sys.argv[1:]
    for p in paths:
        format_path(p)