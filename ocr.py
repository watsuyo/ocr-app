from PIL import Image
import sys
import pyocr
import os
import json

# pip install requests
import requests

NOTION_ACCESS_TOKEN = '****************'
NOTION_PAGE_ID = '****************'

def request_google_api(isbn):
	url = "https://www.googleapis.com/books/v1/volumes"
	try:
		response = requests.get(url, params={"q": "isbn" + isbn})
		response.raise_for_status()
	except requests.exceptions.RequestException as e:
		print("error : ", e)
		print(response.text)
		exit(1)
	return response.json()

def POST_dict(data):
	dic = {}
	dic["title"] = data["items"][0]["volumeInfo"]["title"]
	dic["author"] = ", ".join(data["items"][0]["volumeInfo"]["authors"])
	dic["date"] = data["items"][0]["volumeInfo"]["publishedDate"]
	tmp = data["items"][0]["volumeInfo"]["industryIdentifiers"]
	value_list = [x["identifier"] for x in tmp if x["type"] == "ISBN_13"]
	value = value_list[0] if len(value_list) else 0
	dic["isbn"] = value
	return dic

def notion_post(data, words, newDir):
	file = newDir + 'page_id.txt'
	if os.path.exists(file):
		with open(file) as f:
			pageId = f.read() or ''
		url = 'https://api.notion.com/v1/pages/' + pageId
		try:
			headers = {
				"Authorization": NOTION_ACCESS_TOKEN,
				"Content-Type": "application/json",
				"Notion-Version": "2021-05-13",
			}
			data = {
				"parent": {"database_id": NOTION_PAGE_ID},
				"properties": {
					"Words": {
						"type": "rich_text",
						"rich_text": [{"text": {"content": words}}],
					},
				},
			}
			response = requests.patch(url=url, headers=headers, data=json.dumps(data))
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print("error : ", e)
			print(response.text)
			exit(1)
	else:
		url = "https://api.notion.com/v1/pages"
		try:
			headers = {
				"Authorization": NOTION_ACCESS_TOKEN,
				"Content-Type": "application/json",
				"Notion-Version": "2021-05-13",
			}
			data = {
				"parent": {"database_id": NOTION_PAGE_ID},
				"properties": {
					"Title": {
						"type": "title",
						"title": [{"text": {"content": data["title"]}}],
					},
					"Author": {
						"type": "rich_text",
						"rich_text": [{"text": {"content": data["author"]}}],
					},
					"PublishedDate": {
						"type": "rich_text",
						"rich_text": [{"text": {"content": data["date"]}}],
					},
					"ISBN": {"type": "number", "number": int(data["isbn"])},
					"Words": {
						"type": "rich_text",
						"rich_text": [{"text": {"content": words}}],
					},
				},
			}
			response = requests.post(url=url, headers=headers, data=json.dumps(data))
			pageId = response.json()['id']

			with open(newDir + '/page_id.txt', 'w') as f:
				f.write(pageId)
				f.close()
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print("error : ", e)
			print(response.text)
			exit(1)


def create_words(data, txt):
	title = data['title']

	newDir = title + '/'
	if not os.path.exists(newDir):
		os.makedirs(newDir)
	newResultFile = newDir + 'ocr_result.txt'
	with open(newResultFile, 'a') as f:
		f.write(txt.replace(",", "").replace(".", "").replace("\n", " ") + ' ')
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
	obj = dict();
	obj['words'] = '\n'.join(countWords)
	obj['newDir'] = newDir
	return	obj

def main():
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

			isbn = sys.argv[2]

			if len(isbn) != 13:
				exit(1)

			bookInfo = request_google_api(isbn)

			data = POST_dict(bookInfo)
			obj = create_words(data, txt.lower())
			notion_post(data, obj['words'], obj['newDir'])
		except ValueError:
			print("Oops! Your input output file name is already exists.")
		except FileNotFoundError:
			sys.exit('nl: No such file or directory: ' + inputFile)

	else:
		sys.exit('usage: nl [file]')

main()
