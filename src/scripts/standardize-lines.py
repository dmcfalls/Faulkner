# This script removes lines with isolated titles, page numbers, and blank lines

import nltk
import re
import os

pathname = "./corpus/novels/1959-01_The_Mansion.txt"
output = "./out.txt"

title = "THE MANSION"
author = "WILLIAM FAULKNER"

beginLine = 10

def main():
    with open(pathname, "r") as textfile:
        with open(output, "w") as outputfile:
            blankline = False
            skipline = False
            currLine = 0
            for line in textfile.readlines():
                skipline = False
                # Remove blank lines
                if line in ["\n", "\r\n"]:
                    if blankline:
                        skipline = True
                    blankline = True
                else:
                    blankline = False
                    # Remove lines that only contain title or page number
                    titleInLine = (title.lower() in line.lower())
                    authorInLine = (author.lower() in line.lower())
                    if ((titleInLine or authorInLine) and currLine > beginLine) or re.match("^[0-9*]+$", line.strip()):
                        skipline = True
                # Only write to output file lines not containing title/ author / page number
                if not skipline:
                    outputfile.write(line)
                currLine = currLine + 1
    textfile.close()
    outputfile.close()

if __name__ == "__main__":
    main()
