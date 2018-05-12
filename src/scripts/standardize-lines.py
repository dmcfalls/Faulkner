# This script removes lines with isolated titles, page numbers, and blank lines

import nltk
import os

pathname = "./corpus/novels/1942-01_Go_Down_Moses.txt"
output = "./out.txt"

title = "GO DOWN, MOSES"

def main():
	with open(pathname, "r") as textfile:
		with open(output, "w") as outputfile:
			blankline = False
			skipline = False
			for line in textfile:
				# Remove blank lines
				if line in ["\n", "\r\n"]:
					if blankline:
						skipline = True
					blankline = True
				else:
					blankline = False
				# Remove lines that only contain title or page number
				if title in line or title.isdigit():
					skipline = True

				if not skipline:
					outputfile.write(line)
				skipline = False
	textfile.close()
	outputfile.close()

if __name__ == "__main__":
	main()
