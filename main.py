import sys
import os
import yaml
import urllib.parse
import urllib.request
import time
import progressbar

from jinja2 import Template

mapTemplateURL = ""
zoom = ""

def main():

	configFile = sys.argv[1]

	if "yaml" not in configFile:
		if "yml" not in configFile:
			print("yaml file not provided")
			sys.exit()

	if not (os.path.isdir("output")):
		try:
			os.mkdir("output")
		except OSError:
			print ("failed to create output directory", OSError)
			sys.exit()

	outputDirName = os.path.join("output",str(int(time.time())))

	try:
		os.mkdir(outputDirName)
	except OSError:
		print ("failed to create download directory", OSError)
		sys.exit()
	else:
		print("downloading tiles into directory:",outputDirName)

	parsedMapURL, zoom = readConfig(configFile)

	numTilesPerIteration  = (2 ** zoom) - 1

	for xTile in progressbar.progressbar(range(numTilesPerIteration)):
		for yTile in progressbar.progressbar(range(numTilesPerIteration)):
			saveMapTile(outputDirName, parsedMapURL, zoom, xTile, yTile)
			# pausing download to avoid any security flags with tile service
			time.sleep(0.2)

	pass



def readConfig(configFile):
	print("using config %s" % configFile)

	mapURL = ""
	zoom = 0

	with open(configFile, 'r') as file:
		try:
			# print(yaml.safe_load(file))

			lookup = yaml.safe_load(file)
			mapURL = lookup["mapURL"]
			zoom = lookup["zoom"]

			paramList = lookup["paramList"]

			encodedParamList = urllib.parse.urlencode(paramList)
			
			mapURL = mapURL +"?"+encodedParamList

		except yaml.YAMLError as err:
			print(err)
			sys.exit()

	return mapURL, zoom


def saveMapTile(outputDir, mapURL, zoom, xTile, yTile):

	urlTemplate = Template(mapURL)

	mapURL = urlTemplate.render(z=str(zoom), x=str(xTile), y=str(yTile))

	fileName = str(xTile) + "-" + str(yTile) + ".png"
	filePath = os.path.join(outputDir,fileName)
	# print(mapURL)

	urllib.request.urlretrieve(mapURL, filePath)


main()