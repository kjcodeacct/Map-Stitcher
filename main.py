import argparse
import sys
import os
import yaml
import urllib.parse
import urllib.request
import time
import progressbar

from PIL import Image

from jinja2 import Template

parser = argparse.ArgumentParser(description='Map Stitcher')

parser.add_argument('--config', dest='config_file', help = "specify yaml config file",
	default="example.yaml")

parser.add_argument('--file-ext', dest='file_ext', help = "specify default image file extension",
	default=".png")

parser.add_argument('--cleanup', dest='cleanup_temp_files', help = "cleanup temporary files after download",
	default=True)

fileExtension = ".png"

def main():

	args = parser.parse_args()

	configFile = args.config_file
	cleanupTempFiles = args.cleanup_temp_files
	fileExtension = args.file_ext

	if "yaml" not in configFile:
		if "yml" not in configFile:
			print("yaml file not provided")
			sys.exit()

	parsedMapURL, zoom = readConfig(configFile)
	print(parsedMapURL)
	outputDir = downloadTileSet(parsedMapURL, zoom)

	print("stitching together image")
	worldMapFilePath = stitchImages(outputDir, zoom)

	print("completed stiching world map")

	cleanupTempFiles = args.cleanup_temp_files
	if (cleanupTempFiles):
		print("cleaning up temporary files")
		cleanupFiles(outputDir, zoom)
		
	print("please see %s for stitched map" %  worldMapFilePath)

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

def downloadTileSet(parsedMapURL, zoom):

	if not (os.path.isdir("output")):
		try:
			os.mkdir("output")
		except OSError:
			print ("failed to create output directory", OSError)
			sys.exit()

	outputDir = os.path.join("output",str(int(time.time())))

	try:
		os.mkdir(outputDir)
	except OSError:
		print ("failed to create download directory", OSError)
		sys.exit()
	else:
		print("downloading tiles into directory:",outputDir)

	numTilesPerIteration  = (2 ** zoom)

	for xTile in progressbar.progressbar(range(numTilesPerIteration)):
		for yTile in progressbar.progressbar(range(numTilesPerIteration)):
			saveMapTile(outputDir, parsedMapURL, zoom, xTile, yTile)
			# pausing download to avoid any security flags / http issues with tile service
			time.sleep(0.2)

	return outputDir

def saveMapTile(outputDir, mapURL, zoom, xTile, yTile):

	urlTemplate = Template(mapURL)

	mapURL = urlTemplate.render(z=str(zoom), x=str(xTile), y=str(yTile))

	fileName = str(xTile) + "-" + str(yTile) + fileExtension
	filePath = os.path.join(outputDir,fileName)

	succeeded = False
	numRetries = 3
	for _ in range(numRetries):
		try:
			urllib.request.urlretrieve(mapURL, filePath)
			succeeded = True
			break
		except Exception:
			print(Exception)
			time.sleep(0.2)

	else:
		raise

	if not succeeded:
		print("failed to download %s" % mapURL)
		sys.exit()

	pass

def stitchImages(outputDir, zoom):

	numTilesPerIteration  = (2 ** zoom)

	for xTile in range(numTilesPerIteration):

		imageColumn = []

		print("creating vertical image for column %d " % xTile)

		for yTile in range(numTilesPerIteration):

			fileName = str(xTile) + "-" + str(yTile) + fileExtension
			filePath = os.path.join(outputDir,fileName)

			imageColumn.append(filePath)


		imageList = [Image.open(y) for y in imageColumn]
		widths, heights = zip(*(i.size for i in imageList))

		totalHeight = sum(heights)
		maxWidth = max(widths)

		yOffset = 0

		newImgColumn = Image.new('RGB', (maxWidth, totalHeight))

		for img in progressbar.progressbar(imageList):
			newImgColumn.paste(img, (0, yOffset))
			yOffset = yOffset + img.size[0]

		imgColumnFileName = str(xTile)+ fileExtension
		imgColumnFilePath = os.path.join(outputDir,imgColumnFileName)
		newImgColumn.save(imgColumnFilePath)

	print("stitching together vertical columns")

	imgRow = []

	for xTile in range(numTilesPerIteration):
		
		fileName = str(xTile) + fileExtension
		filePath = os.path.join(outputDir,fileName)
		imgRow.append(filePath)
	

	imageList = [Image.open(x) for x in imgRow]
	widths, heights = zip(*(i.size for i in imageList))

	totalWidth = sum(widths)
	maxHeight = max(heights)

	xOffset = 0 

	newWorldMap = Image.new('RGB', (totalWidth, maxHeight))

	for img in progressbar.progressbar(imageList):
		newWorldMap.paste(img, (xOffset, 0))
		xOffset = xOffset + img.size[0]

	worldMapFileName = "world-map" + fileExtension
	worldMapFilePath = os.path.join(outputDir,worldMapFileName)
	newWorldMap.save(worldMapFilePath)

	return worldMapFilePath

def cleanupFiles(outputDir, zoom):

	numTilesPerIteration  = (2 ** zoom)
	
	for xTile in progressbar.progressbar(range(numTilesPerIteration)):

		fileName = str(xTile) + fileExtension
		filePath = os.path.join(outputDir,fileName)

		try:
			os.remove(filePath)
		except Exception:
			print(Exception)
			sys.exit()

		for yTile in progressbar.progressbar(range(numTilesPerIteration)):
			fileName = str(xTile) + "-" + str(yTile) + fileExtension
			filePath = os.path.join(outputDir,fileName)

			try:
				os.remove(filePath)
			except Exception:
				print(Exception)
				sys.exit()

	pass

main()