import cloudconvert
api = cloudconvert.Api('5Cl0Jof_PxgEepLMQcPcALwYQzw8YQTIXmTOaCkEpeRbtwe94TwqEVghsQhy5R1tnXWTDuWqNRnNUPxkg--WxQ')

def convert(url): 
	process = api.convert({
	    "inputformat": "ogg",
	    "outputformat": "mp3",
	    "input": "download",
	    "file": url,
	    "save": "true"
	})
	process.wait()

	return(process['output']['url'])
