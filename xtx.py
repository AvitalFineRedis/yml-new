#! /usr/bin/python

from optparse import OptionParser
import sys
import jinja2


class parse_yml(object):
    """
    A class for parsing fiels to yaml files
    """
    def __init__(self, src_file_name, dest_file_name, library):

        self.__include_role = "@include "
        self.__multilinebeginnig_role = "@define "
        self.__onelinebeginnig_role = "@def "
        self.__functionending_role = "@end"
        self.__comment_role = "#"
        self.srcname = src_file_name
        self.dest = open(dest_file_name, 'w+')
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
            sys.stderr.write("must declate a name for function")
            sys.exit(1)

        # read the function content
        line = fp.readline()
        while line and not line.startswith(self.__functionending_role):
            content += line
            line = fp.readline()

        # insert the content to the dictionary corresponding
        # to the name (the key)
        self.vars[name] = content

    def readfile(self):
        self.parseDefinitionsAndInclude(self.srcname)
        print(self.vars)
        self.insertDefinitions()

    def parseDefinitionsAndInclude(self, filename):
        with open(filename, 'r') as fp:
            # we use the readline methodology to be able to continue to
            # read the file in readfunction methode from the same line
            # we left this methode
            line = fp.readline()
            while line:
                if line.startswith(self.__include_role):
                    nextfilename = line[len(self.__include_role):].strip()  # isolate the name of the file
                    self.parseDefinitionsAndInclude(self.library + nextfilename)

                elif line.startswith(self.__multilinebeginnig_role):
                    name = line[len(self.__multilinebeginnig_role):].strip()  # isolate the name of the function
                    self.readDefinition(fp, name)

                elif line.startswith(self.__onelinebeginnig_role):
                    temp = line[len(self.__onelinebeginnig_role):].strip().split('=')
                    # if lenght of temp != 2 -> need to throw exeption
                    name = temp[0]
                    content = temp[1]
                    self.vars[name] = content

                elif line.startswith(self.__comment_role):
                    pass

                else:
                    self.dest.write(line)

                line = fp.readline()

    def insertDefinitions(self):
        pass

if __name__ == "__main__":
    p = OptionParser()

    p.add_option("-s", "--sourcefile", dest="surcefiles", action="append", help="insert the files you want to parse")
    p.add_option("-d", "--destinationfile", dest="destinationfiles",action="append", help="insert the destination for each file you want to parse")
    p.add_option("-l", "--library", dest="libraryfolder", help="")

    (options, args) = p.parse_args()
    print(options.surcefiles)
    print(options.destinationfiles)

    if options.surcefiles is not None and options.destinationfiles is not None:
        if len(options.surcefiles) != len(options.destinationfiles):
            sys.stderr.write("The number of the source files must be equal to the number of the destination files")
            sys.exit(1)

        for i, filename in enumerate(options.surcefiles):
            xtx = parse_yml(filename, options.destinationfiles[i], options.libraryfolder)
            xtx.readfile()

    exit(0)
