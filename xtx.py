#! /usr/bin/python

import argparse
import os
import sys
import jinja2
import re

#parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
#                                 description='Template text Jinja2-style formatter.\nUse {{VAR}} syntax to insert variables.\nUse @include filename to include code files')

#parser.add_argument('-r', '--recursive', action='store_true', help='recirsive yml-new file\nTrue by default')
#parser.add_argument('-d', '--destinationfile', action='append',  help='name of the new yaml file')
#parser.add_argument('-f', '--file', action='append', help='Templates file')
#parser.add_argument('template', metavar='FILE', nargs='?', help='template file')
#args = parser.parse_args()

args = {
    "file": ["circleci.txt"],
    "destinationfile": ["new.yml"] 
}

include_role = "@include"

def readfile(newfile, filename) :
    with open(filename, 'r') as file:
        for line in file.readlines():
            if line.startswith(include_role):
                print("hi")
                nextfilename = line[len(include_role):].strip() # isolate the name of the file
                readfile(newfile, nextfilename) 
            else:
                newfile.write(line)


if not args["file"] is None and not args["destinationfile"] is None:
    if len(args["destinationfile"]) != len(args["file"]):
        # throw some exception
        exit(0)

    for i, filename in enumerate(args["file"]):
        newfile = open(args["destinationfile"][i], 'a')
        readfile(newfile, filename)

