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
                    found, file_path = self._find_file(nextfilename)

                    if found and file_path:
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

                elif line.startswith("#"):
                        pass

                else:
                    m = re.search('{{(.+?)}}', line)
                    if m: 
                        name = m.group(1)
                        if name in self.vars:
                            content = self.vars[name]
                            if isinstance(content, list):
                                for cur_line in content:
                                    working_lines.append(indentation + cur_line)
                            else:
                                working_lines.append(indentation + content + '\n')
                            finished = False
                        else:
                            working_lines.append(indentation + line)
                            #raise RuntimeError(f"{name} must be declated before it used.")

                    else:
                        working_lines.append(indentation + line)
            
            return finished, working_lines

    def _find_file(self, file_name):
        """
        Loop over the given libraries and looking for the file.
        Return bool that indicates if the file was found or not,
        and returns the file's path if it was found.
        """
        found = False
        if isinstance(self.library, list):
            for lib in self.library:
                file_path = os.path.join(lib, file_name)
                if os.path.exists(file_path):
                    found = True
                    break
        else:
            file_path = os.path.join(self.library, file_name)
            if os.path.exists(file_path):
                found = True

        return found, file_path

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
