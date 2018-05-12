# This script attempts to correct basic transcription errors in texts generated with OCR

import nltk
import os

pathname = "./corpus/novels/1926-01_Soldiers_Pay.txt"
output = "./out.txt"

def main():
	with open(pathname, "r") as textfile:
		with open(output, "w") as outputfile:
			#TODO: finish writing this script
			
	textfile.close()
	outputfile.close()

if __name__ == "__main__":
	main()
