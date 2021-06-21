#! /usr/bin/python

# TODO: OptionParser is deprecated, use ArgumentParser
from optparse import OptionParser
from os import linesep
import sys
import re

# import sys, os
# sys.path.insert(0, '/w/rafi_1/readies')
# import paella


class Gena(object):
    """
    A class for parsing fiels to yaml files
    """
    # TODO: allow multiple libraries (include directories)
    def __init__(self, src_file_name, dest_file_name, library):

        self.__include_role = "@include "
        self.__multilinebeginnig_role = "@define "
        self.__onelinebeginnig_role = "@def "
        self.__functionending_role = "@end"
        self.__comment_role = "#"
        self.srcname = src_file_name
        self.destname = dest_file_name
        #self.dest = open(dest_file_name, 'w+')
        self.library = library
        self.vars = {}

    def readDefinition(self, fp, name):
        """
        This function reads the content of the function.
        Make sure that the pointer of the file will be on
        the first line of the function
        """
        content = ""

        # check if the name of the function is not empty
        if not name:
            raise RuntimeException("Must declare a name for function after @define")

        # read the function content
        line = fp.readline()
        while line and not line.startswith(self.__functionending_role):
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
                if line.startswith(self.__include_role):
                    nextfilename = line[len(self.__include_role):].strip()  # isolate the name of the file
                    self.parseDefinitionsAndInclude(self.library + nextfilename)

                elif line.startswith(self.__multilinebeginnig_role):
                    name = line[len(self.__multilinebeginnig_role):].strip()  # isolate the name of the function
                    self.readDefinition(fp, name)

                elif line.startswith(self.__onelinebeginnig_role):
                    temp = line[len(self.__onelinebeginnig_role):].strip().split('=')
                    # if lenght of temp != 2 -> need to throw exeption
                    name = temp[0].strip()
                    content = temp[1].strip()
                    # print (name, "->", content)
                    self.vars[name] = content

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

                    elif line.startswith(self.__comment_role):
                        pass

                    else:
                        self.dest.write(indentation + line)

                line = fp.readline()


if __name__ == "__main__":
    # TODO: OptionParser -> ArgumentParser
    p = OptionParser()
    p.add_option("-s", "--sourcefile", dest="surcefiles",help="insert the files you want to parse")
    p.add_option("-d", "--destinationfile", dest="destinationfiles", help="insert the destination for each file you want to parse")
    p.add_option("-l", "--library", dest="libraryfolder", help="")

    (options, args) = p.parse_args()
    # print(options.surcefiles)
    # print(options.destinationfiles)

    # TODO: catch exception and return error
    try:
        if options.surcefiles is not None and options.destinationfiles is not None:
            xtx = Gena(options.surcefiles, options.destinationfiles, options.libraryfolder)
            xtx.readFile()
    except x:
        sys.stderr.write(f"{x}")
        sys.exit(1)
        

    exit(0)

# TODOs:
# (1) handle undefined {{...}} - print error
# (2) operate on lists of lines instead on a file
