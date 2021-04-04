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
vars = {}

include_role = "@include "
functionbeginnig_role = "@def "
functionending_role = "@end"


def readfunction(file, function_name):
    function_content = ""

    # check if the name of the function is not empty
    if not function_name:
        #throw some exeption 
        exit(1)

    # read the function content
    line = file.readline()
    while line and not line.startswith(functionending_role):
        function_content += line
        line = file.readline()

    vars[function_name] = function_content


def readfile(newfile, filename) :
    with open(filename, 'r') as file:
        line = file.readline()
        while line: 
            if line.startswith(include_role):
                nextfilename = line[len(include_role):].strip() # isolate the name of the file
                readfile(newfile, nextfilename)   
            elif line.startswith(functionbeginnig_role):
                name = line[len(functionbeginnig_role):].strip() # isolate the name of the function
                readfunction(file, name)
            else:
                newfile.write(line)

            line = file.readline()


if not args["file"] is None and not args["destinationfile"] is None:
    if len(args["file"]) != len(args["destinationfile"]):
        # throw some exception
        exit(1)

    for i, filename in enumerate(args["file"]):
        newfile = open(args["destinationfile"][i] + ".jinja", 'w')
        readfile(newfile, filename)
        
        file = open(args["destinationfile"][i] + ".jinja", 'r')
        t = file
        print(jinja2.Template(t).render(vars))

exit(0)