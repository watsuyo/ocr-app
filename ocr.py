from PIL import Image
import sys
import pyocr
import datetime

argc = len(sys.argv)

if argc == 1:
  inputFile = sys.stdin
elif argc == 2 or argc == 3:
	try:
		open(sys.argv[1], 'r')
		inputFile = sys.argv[1]
	except FileNotFoundError:
		sys.exit('nl: No such file or directory: ' + sys.argv[1])

else:
	sys.exit('usage: nl [file]')

tools = pyocr.get_available_tools()
tool = tools[0]

txt = tool.image_to_string(
  Image.open(inputFile),
  lang='eng',
  builder=pyocr.builders.TextBuilder()
)

try:
	now = datetime.datetime.now()
	f = open(now.strftime('%Y%m%d_%H%M%S') + '.txt', 'x')
	f.write(txt)
except ValueError:
	print("Oops! Your input output file name is already exists.")

f.close()
