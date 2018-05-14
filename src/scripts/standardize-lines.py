# This script removes lines with isolated titles, page numbers, and blank lines

import nltk
import os

pathname = "./corpus/novels/1926-01_Soldiers_Pay.txt"
output = "./out.txt"

title1 = "soldiers"
title2 = "pay"

def main():
	with open(pathname, "r") as textfile:
		with open(output, "w") as outputfile:
			blankline = False
			skipline = False
			for line in textfile.read():
				# Remove blank lines
				if line in ["\n", "\r\n"]:
					if blankline:
						skipline = True
					blankline = True
				else:
					blankline = False
				# Remove lines that only contain title or page number
				if (title1 in line.lower() and title2 in line.lower()) or line.isdigit():
					skipline = True

				if not skipline:
					outputfile.write(line)
				skipline = False
	textfile.close()
	outputfile.close()

if __name__ == "__main__":
	main()
