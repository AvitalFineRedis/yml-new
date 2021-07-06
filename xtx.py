#! /usr/bin/python

import argparse
import os
from os import linesep, path
import sys
import re

# import sys, os
# sys.path.insert(0, '/w/rafi_1/readies')
# import paella


class Gena(object):
    """
    A class for parsing fiels to yaml files
    """
    def __init__(self, src_file_name, dest_file_name, library):

        self.srcname = src_file_name
        self.destname = dest_file_name
        self.library = library # can be list or single name 
        self.vars = {}

    def readFile_newversion(self):
        lines = []
        # open the surce file and convert it to list of strings (lines)
        with open(self.srcname, 'r') as f:
            lines = f.readlines()
        
        # go over the lines and parse them until nothing changed
        finised = False
        while not finised:
            finised, lines = self.parseDefinitionsAndInclude_newversion(lines)

        # write the lines to the destination file and remove redundant new lines
        last_added = None
        with open(self.destname, 'w') as dest:
            for l in lines:
                if l != "\n" or l != last_added:
                    last_added = l
                    dest.write(l)

    def parseDefinitionsAndInclude_newversion(self, lines):
            working_lines = []
            finished = True
            in_define = False
            define_content = []
            defien_name =""

            for line in lines:
                # define state: read lines to define the content until reach the "@end"
                if in_define:
                    if line.startswith("@end"):
                        in_define = False
                        self.vars[defien_name] = define_content
                    else:
                        define_content.append(line)
                    continue
                        
                p = re.compile(r"^\s*")
                result = p.search(line)
                indentation = result.group()
                line = line[len(indentation):]
                
                # check include statements                    
                if line.startswith("@include"):
                    nextfilename = line[len("@include")+1:].strip()  # isolate the name of the file
                    found = False
                    file_path = ""
                    if isinstance(self.library, list):
                        for lib in self.library:
                            file_path = os.path.join(lib, nextfilename)
                            if os.path.exists(file_path):
                                found = True
                                break
                    else:
                        file_path = os.path.join(self.library, nextfilename)
                        if os.path.exists(file_path):
                            found = True

                    if found:
                        with open(file_path, 'r') as f_inc:
                            _ , included_lines = self.parseDefinitionsAndInclude_newversion(f_inc.readlines())
                            working_lines += included_lines
                            finished = False
                    else:
                        raise RuntimeError("the file {nextfilename} was not found in any of the given libraries.")

                # check multiline definitions (define)
                elif line.startswith("@define"):
                    in_define = True
                    define_content = []
                    defien_name = line[len("@define")+1:].strip()  # isolate the name of the function
                    if not defien_name:
                        raise RuntimeError("Must declare a name for function after @define")
                    
                    define_content = []

                # check one-line definitions (@def)
                elif line.startswith("@def"):
                    temp = line[len("@def")+1:].strip().split('=')
                    if len(temp) != 2:
                        raise RuntimeError("@def must be declared with '='.")
                    name = temp[0].strip()
                    content = temp[1].strip()
                    self.vars[name] = content
                    if name == "steps:prebuild":
                        print("yeyy")

                elif line.startswith("#"):
                        pass

                else:
                    m = re.search('{{(.+?)}}', line)
                    if m: 
                        name = m.group(1)
                        if name in self.vars:
                            content = self.vars[name]
                            for cur_line in content:
                                working_lines.append(indentation + cur_line)
                            finished = False
                        else:
                            working_lines.append(indentation + line)
                            #raise RuntimeError(f"{name} must be declated before it used.")

                    else:
                        working_lines.append(indentation + line)
            
            return finished, working_lines

    def readDefinition(self, fp, name):
        """
        This function reads the content of the function.
        Make sure that the pointer of the file will be on
        the first line of the function
        """
        content = []

        # check if the name of the function is not empty
        if not name:
            raise RuntimeError("Must declare a name for function after @define")

        # read the function content
        line = fp.readline()
        while line and not line.startswith("@end"):
            content += line
            line = fp.readline()

        # insert the content to the dictionary corresponding
        # to the name (the key)
        self.vars[name] = content

    def readFile(self):
        for _ in range(6):
            # print(_)
            self.dest = open(self.destname, 'w+')
            self.parseDefinitionsAndInclude(self.srcname)
            self.srcname = self.destname
            # print("flow:automation:release" in self.vars.keys())

    def parseDefinitionsAndInclude(self, filename):

        with open(filename, 'r') as fp:
            # we use the readline methodology to be able to continue to
            # read the file in readDefinition method from the same line
            # we left this method
            line = fp.readline()
            while line:
                p = re.compile(r"^\s*")
                result = p.search(line)
                indentation = result.group()
                line = line[len(indentation):]
                if line.startswith("@include"):
                    nextfilename = line[len("@include")+1:].strip()  # isolate the name of the file
                    self.parseDefinitionsAndInclude(self.library + nextfilename)

                elif line.startswith("@define"):
                    name = line[len("@define")+1:].strip()  # isolate the name of the function
                    self.readDefinition(fp, name)

                elif line.startswith("@def"):
                    temp = line[len("@def")+1:].strip().split('=')
                    # if lenght of temp != 2 -> need to throw exeption
                    name = temp[0].strip()
                    content = temp[1].strip()
                    # print (name, "->", content)
                    self.vars[name] = content

                elif line.startswith("#"):
                        pass

                else:
                    m = re.search('{{(.+?)}}', line)
                    if m: 
                        name = m.group(1)
                        if name in self.vars:
                            value = self.vars[name]
                            for l in value.splitlines():
                                self.dest.write(indentation + l + "\n")
                        else:
                            self.dest.write(indentation + line)

                    else:
                        self.dest.write(indentation + line)

                line = fp.readline()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-s',  dest='surcefiles', help="insert the files you want to parse")
    parser.add_argument('-d', dest='destinationfiles', help="insert the destination for each file you want to parse")
    parser.add_argument('-l', action='append', dest='libraryfolders')
    args = parser.parse_args()
    
    # TODO: catch exception and return error
    try:
        if args.surcefiles is not None and args.destinationfiles is not None:
            xtx = Gena(args.surcefiles, args.destinationfiles, args.libraryfolders)
            xtx.readFile_newversion()
    except RuntimeError as x:
        sys.stderr.write(f"{x}")
        sys.exit(1)
    
    exit(0)

# TODO:
# (1) handle undefined {{...}} - print error
