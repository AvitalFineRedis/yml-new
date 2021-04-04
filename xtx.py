#! /usr/bin/python

from optparse import OptionParser
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

class parse_yml(object):

    def __init__(self):

        self.__include_role = "@include "
        self.__functionbeginnig_role = "@def "
        self.__functionending_role = "@end"
        self.vars = {}


    def readfunction(self, file, function_name):
        function_content = ""

        # check if the name of the function is not empty
        if not function_name:
            sys.stderr.write("must declate a name for function")
            sys.exit(1)

        # read the function content
        line = file.readline()
        while line and not line.startswith(self.__functionending_role):
            function_content += line
            line = file.readline()

        # insert the function content to the dictionary corresponding to the function name (the key)
        self.vars[function_name] = function_content


    def readfile(self, newfile, filename) :
        with open(filename, 'r') as fp:
            # we use the readline methodology to be able to continue to read thr file in readfunction methode from the same 
            # line we left this methode 
            line = fp.readline()
            while line: 
                if line.startswith(self.__include_role):
                    nextfilename = line[len(self.__include_role):].strip() # isolate the name of the file
                    self.readfile(newfile, nextfilename)   
                elif line.startswith(self.__functionbeginnig_role):
                    name = line[len(self.__functionbeginnig_role):].strip() # isolate the name of the function
                    self.readfunction(fp, name)
                else:
                    newfile.write(line)

                line = fp.readline()

if __name__ == "__main__":
    p = OptionParser()

    p.add_option("-s", "--sourcefile", dest="filename", action="append", help="insert the files you want to parse")
    p.add_option("-d", "--destinationfile", dest="filename", action="append", help="insert the destination for each file you want to parse")
    #args = {
     #   "file": ["circleci.txt"],
      #  "destinationfile": ["new.yml"] 
    #}

    (options, args) = p.parse_args()
    
    if not args["file"] is None and not args["destinationfile"] is None:
        if len(args["file"]) != len(args["destinationfile"]):
            sys.stderr.write("The number of the source files must be equal to the number of the destination files")
            sys.exit(1)

        xtx = parse_yml()

        for i, filename in enumerate(args["file"]):
            newfilename = args["destinationfile"][i]
            newfile = open(newfilename, 'r+')
            xtx.readfile(newfile, filename)
            
            tmpl = jinja2.Template(open(newfilename).read())
            rendered = tmpl.render(xtx.vars)
            print(rendered)

    exit(0)