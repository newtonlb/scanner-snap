import serial
import re

def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd;


def getNumbers(number, coord='lat'):
	if coord == 'lon':
		matcher = re.search(r'^[0-9]{3}', number)
	else:
		matcher = re.search(r'^[0-9]{2}', number)
	if matcher:
		degrees = float(str(matcher.group()))

	matcher = re.search(r'[0-9]{2}\.', number)
	if matcher:
		minutes = float(matcher.group()[:-1])

	matcher = re.search(r'\.[0-9]*$', number)
	if matcher:
		seconds = float(matcher.group()[1:])

	print(degrees, minutes, seconds)
	return degrees, minutes, seconds

while True:
	with serial.Serial('/dev/ttyS4', timeout=100) as ser:
		line = ser.readline()
		try:
			line = line.decode("utf-8").split('\x00')	
		except:
			print ("could not decode")
			continue
		line = "".join(line)
		print(line)
		data = line.split(",")
		if re.match(r"^\$GNGGA", line):
			timestamp = data[1]
			deg, minu, sec = getNumbers(data[2])
			sec=sec/1000.0
			lat = dms2dd(deg, minu, sec, data[3])

			deg, minu, sec = getNumbers(data[4], coord='lon')
			sec=sec/1000.0
			lon = dms2dd(deg, minu, sec, data[5])
			# if data[5] == 'E':
			# 	lon = float(data[4])
			# else:
			# 	lon = -float(data[4])

		elif re.match(r"^\$GNGLL", line):
			timestamp = data[5]
			deg, minu, sec = getNumbers(data[1])
			sec=sec/1000.0
			lat = dms2dd(deg, minu, sec, data[2])

			deg, minu, sec = getNumbers(data[3], coord='lon')
			sec=sec/1000.0
			lon = dms2dd(deg, minu, sec, data[4])
			# if data[2] == 'N':
			# 	lat = float(data[1])
			# else:
			# 	lat = -float(data[1])

			# if data[4] == 'E':
			# 	lon = float(data[3])
			# else:
			# 	lon = -float(data[3])

		elif re.match(r"^\$GNRMC", line):
			timestamp = data[1]

			deg, minu, sec = getNumbers(data[3])
			sec=sec/1000.0
			lat = dms2dd(deg, minu, sec, data[4])

			deg, minu, sec = getNumbers(data[5], coord='lon')
			sec=sec/1000.0
			lon = dms2dd(deg, minu, sec, data[6])
			# if data[4] == 'N':
			# 	lat = float(data[3])
			# else:
			# 	lat = -float(data[3])

			# if data[6] == 'E':
			# 	lon = float(data[5])
			# else:
			# 	lon = -float(data[5])
		else:
			continue
			
		json = {
				'timestamp': timestamp,
				'lat': lat,
				'lon': lon
			}
		print(json)
		

