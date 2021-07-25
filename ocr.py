from PIL import Image
import sys
import pyocr
import datetime
import os

# pip install requests
import requests
import json

def getBookInfo(isbn):
	url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'
	req_url = url + isbn
	response = requests.get(req_url)
	return response.text

argc = len(sys.argv)

if argc == 1:
	inputFile = sys.stdin
elif argc == 2 or argc == 3:
	try:
		inputFile = sys.argv[1]
		with open(inputFile) as f:
			tools = pyocr.get_available_tools()
			tool = tools[0]

			txt = tool.image_to_string(
				Image.open(inputFile),
				lang='eng',
				builder=pyocr.builders.TextBuilder()
			)

		bookInfo = getBookInfo(sys.argv[2])
		title = json.loads(bookInfo)['items'][0]['volumeInfo']['title']

		newDir = title + '/'
		os.makedirs(newDir)
		newResultFile = newDir + 'ocr_result.txt'

		f = open(newResultFile, 'w')
		f.write(txt)
		f.close()

		with open(newResultFile) as newF:
			data = newF.read()
			words = {}
			for word in data.split():
				words[word] = words.get(word, 0) + 1
		d = [(v, k) for k, v in words.items()]
		d.sort()
		d.reverse()

		countWords = []

		for count, word in d[:100]:
			countWords.append(str(count) + ' ' + word)

		newWordsFile = newDir + 'words.txt'

		f = open(newWordsFile, 'w')
		f.write('\n'.join(countWords))
		f.close()

		print("done")
	except ValueError:
		print("Oops! Your input output file name is already exists.")
	except FileNotFoundError:
		sys.exit('nl: No such file or directory: ' + sys.argv[1])

else:
	sys.exit('usage: nl [file]')
