"""
Code.Fun.Do. 2016, IIT Bombay
Team Name: DAK (Dhruv Ilesh Shah, Archit Gupta, Krish Mehta)
Project Name: Tetra

Backend Script for fetching data using the Microsoft Computer Vision API
(https://www.microsoft.com/cognitive-services/en-us/computer-vision-api).
"""

import time
import requests
import cv2
import operator
import numpy as np
from operator import itemgetter

import matplotlib.pyplot as plt


# Variables

_url = 'https://api.projectoxford.ai/vision/v1/analyses'
_key = 'c60ef392e53a4b96bb51304ec2463a96'  # Primary Key

_url2 = 'https://api.projectoxford.ai/emotion/v1.0/recognize'
_key2 = '12b068b59d2949eeb7940e34cedbad41'

_maxNumRetries = 10
mode = "URL" # Set to URL/Local


def processRequest(url, json, data, headers, params):
	"""
	Helper function to process the request to Project Oxford

	Parameters:
	json: Used when processing images from its URL.
	data: Used when processing image read from disk.
	headers: Used to pass the key information and the data type request.
	"""

	retries = 0
	result = None

	while True:

		response = requests.request(
			'post', url,
			json=json,
			data=data,
			headers=headers,
			params=params)

		if response.status_code == 429:

			print("Message: %s" % (response.json()['error']['message']))

			if retries <= _maxNumRetries:
				time.sleep(1)
				retries += 1
				continue
			else:
				print('Error: failed after retrying!')
				break

		elif response.status_code == 200 or response.status_code == 201:

			if 'content-length' in response.headers and int(
					response.headers['content-length']) == 0:
				result = None
			elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
				if 'application/json' in response.headers[
						'content-type'].lower():
					result = response.json() if response.content else None
				elif 'image' in response.headers['content-type'].lower():
					result = response.content
		else:
			print("Error code: %d" % (response.status_code))
			print("Message: %s" % (response.json()['error']['message']))

		break

	return result

def renderResultOnImage( result, img ):
	
	"""Display the obtained results onto the input image"""

	R = int(result['color']['accentColor'][:2],16)
	G = int(result['color']['accentColor'][2:4],16)
	B = int(result['color']['accentColor'][4:],16)

	cv2.rectangle( img,(0,0), (img.shape[1], img.shape[0]), color = (R,G,B), thickness = 25 )

	if 'categories' in result:
		categoryName = sorted(result['categories'], key=lambda x: x['score'])[0]['name']
		cv2.putText( img, categoryName, (30,70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 3 )

result = ""

"""
Analysis of the image retrieved via a URL
"""
if mode == "URL":
	# URL direction to image
	urlImage = 'http://www.bet.com/topics/b/barack-obama/_jcr_content/image.heroimage.dimg/__1358446726593/111412-politics-barack-obama-press-conference.jpg'


	headers = dict()
	headers['Ocp-Apim-Subscription-Key'] = _key2
	headers['Content-Type'] = 'application/json' 
	params = None
	json = { 'url': urlImage } 
	data = None

	result = processRequest(_url2, json, data, headers, params )

else:
	# Load raw image file into memory
	pathToFileInDisk = r'D:\tmp\3.jpg'
	with open( pathToFileInDisk, 'rb' ) as f:
		data = f.read()
		
	# Computer Vision parameters
	params = { 'visualFeatures' : 'Color,Categories'} 

	headers = dict()
	headers['Ocp-Apim-Subscription-Key'] = _key
	headers['Content-Type'] = 'application/octet-stream'

	json = None

	result = processRequest( json, data, headers, params )

list_out = sorted(result[0]['scores'].items(), key=itemgetter(1), reverse=True)
print list_out[0][0]