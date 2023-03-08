#Pranjal Adhikari pa8729

from flask import Flask, request
from geopy.geocoders import Nominatim
import requests
import xmltodict
import math
import time

r = requests.get('https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
iss_data = xmltodict.parse(r.text)

app = Flask(__name__)


@app.route('/', methods = ['GET'])
def data_set() -> dict:
    """
    Outputs the entire ISS Trajectory Data found on the NASA website.

    Args:
        none
    Returns:
        iss_data (dictionary): ISS data set
    """
    global iss_data
    if not iss_data:
        return f"Data not loaded in\n", 404
    return iss_data

#to run with query parameter: curl 'localhost:5000/epochs?limit=int&offset=int'
@app.route('/epochs', methods = ['GET'])
def modified_epoch() -> list:
    """
    Lists all the EPOCHs in the data set of the ISS. With query parameters ('limit' and 'offset'), the user will be able to control how many and which EPOCHs to display.
    Args:
        none
    Return:
        epochs (list): list of all EPOCHs
    """
    data = data_set()
    try:
        num_epochs = request.args.get('limit', len(data['ndm']['oem']['body']['segment']['data']['stateVector']))
    except TypeError:
        return f"Data not loaded in\n", 404
    except KeyError:
        return f"Data not loaded in\n", 404
    start = request.args.get('offset', 0)
    if num_epochs:
        try:
            num_epochs = int(num_epochs)
        except ValueError:
            return f"Limit must be an integer\n", 404
    if start:
        try:
            start = int(start)
        except ValueError:
            return f"Start must be an integer\n", 404
    end = start + num_epochs
    epochs = []
    while start < end:
        epochs.append(data['ndm']['oem']['body']['segment']['data']['stateVector'][start]['EPOCH'])
        start += 1
    return epochs

@app.route('/epochs/<epoch>', methods = ['GET'])
def vectors(epoch: str) -> list:
    """
    Outputs the state vectors for the specified EPOCH from the data set.
    
    Args:
        epoch (str): specified EPOCH time stamp
    Returns:
        state_vectors (list): state vectors of the specified EPOCH
    """
    data = data_set()
    state_vectors = []
    try:
        for i in range(len(data['ndm']['oem']['body']['segment']['data']['stateVector'])):
            if (data['ndm']['oem']['body']['segment']['data']['stateVector'][i]['EPOCH'] == epoch):
                state_vectors.append(data['ndm']['oem']['body']['segment']['data']['stateVector'][i])
                return state_vectors
    except KeyError:
        return f"Data not loaded in\n", 404
    except TypeError:
        return f"Data not loaded in\n", 404
    
@app.route('/epochs/<epoch>/speed', methods = ['GET'])
def epoch_speed(epoch: str) -> dict:
    """
    Calculates the speed of the ISS in the specified EPOCH utilizing the x, y, and z components of speed.
    
    Args:
        epoch (str): specified EPOCH time stamp
    Returns:
        speed (dict): the speed of the ISS at the specified EPOCH
    """
    data = vectors(epoch)
    try:
        sumSpeedSquare = pow(float(data[0]['X_DOT']['#text']), 2) + pow(float(data[0]['Y_DOT']['#text']), 2) + pow(float(data[0]['Z_DOT']['#text']), 2)
    except TypeError:
        return f"Data not loaded in\n", 404
    except KeyError:
        return f"Data not loaded in\n", 404
    speed = (math.sqrt(sumSpeedSquare)) #magnitude of speed utilizing the x, y, and z components of speed
    speed_data = {}
    speed_data['value'] = speed
    speed_data['units'] = data[0]['X_DOT']['@units']
    return speed_data

@app.route('/epochs/<epoch>/location', methods = ['GET'])
def epoch_location(epoch: str) -> dict:
    """
    Calculates the location of the specified EPOCH with the latitude, longitude, and altitude of the ISS.
    
    Args:
        epoch (str): specified EPOCH time stamp
    Returns:
        location (dict): the location of the ISS at the specified EPOCH
    """
    data = vectors(epoch)
    mean_earth_radius = 6371 #earth radius in km
    try:
        x = float(data[0]['X']['#text'])
        y = float(data[0]['Y']['#text'])
        z = float(data[0]['Z']['#text'])
    except TypeError:
        return f"Data not loaded in\n", 404
    except KeyError:
        return f"Data not loaded in\n", 404
    hrs = int(epoch[9:11])
    mins = int(epoch[12:14])
    lat = math.degrees(math.atan2(z, math.sqrt(pow(x, 2)+pow(y, 2))))
    lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 32
    if lon > 180: #handling cases where longitude outside of earth latitude range -180 => 180 degrees
        lon -= 360
    elif lon < -180:
        lon += 360 
    alt = math.sqrt(pow(x, 2)+pow(y, 2)+pow(z, 2)) - mean_earth_radius
    geocoder = Nominatim(user_agent='iss_tracker')
    geolocation = geocoder.reverse((lat, lon), zoom=15, language='en')
    if geolocation == None:
        geolocation = 'none'
    else:
        geolocation = geolocation.raw
        geolocation = geolocation['address']
    location_data = {}
    location_data['latitude'] = lat
    location_data['longitude'] = lon
    location_data['altitude'] = {'units': data[0]['X']['@units'],
                                 'value': alt}
    location_data['geolocation'] = geolocation
    return location_data

@app.route('/now', methods = ['GET'])
def now() -> dict:
    """
    Returns the location data of the ISS for the most recent, up-to-date, real time position.

    Args:
        none
    Returns:
        location (dict): location data of the ISS for the most recent position
    """
    data = data_set()
    now_data = {}
    current_time = time.time()
    diff = float('inf')
    try:
        for i in data['ndm']['oem']['body']['segment']['data']['stateVector']:
            strptime = time.strptime(i['EPOCH'][:-5], '%Y-%jT%H:%M:%S')
            epoch_time = time.mktime(strptime)
            time_diff = current_time - epoch_time
            if abs(time_diff) < abs(diff):
                min_i = i
                diff = time_diff
    except TypeError:
        return f"Data not loaded in\n", 404
    except KeyError:
        return f"Data not loaded in\n", 404
    now_data['closest_epoch'] = min_i['EPOCH']
    now_data['speed'] = epoch_speed(min_i['EPOCH'])
    now_data['seconds_from_now'] = diff
    now_data['location'] = epoch_location(min_i['EPOCH'])
    return now_data

@app.route('/comment', methods = ['GET'])
def display_comments() -> list:
    """
    Lists all the data in the 'comment' list object in the ISS data.
    
    Args:
        none
    Returns:
        comment (list): data in the comment list
    """
    data = data_set()
    try:
        return data['ndm']['oem']['body']['segment']['data']['COMMENT']
    except TypeError:
        return f"Data not loaded in\n", 404
    except KeyError:
        return f"Data not loaded in\n", 404
    
@app.route('/header', methods = ['GET'])
def display_header() -> dict:
    """
    Outputs all data in the 'header' dictionary object in the data.

    Args:
        none
    Returns:
        header (dict): data in the 'header' dictionary
    """
    data = data_set()
    try:
        return data['ndm']['oem']['header']
    except TypeError:
        return f"Data not loaded in\n", 404
    except KeyError:
        return f"Data not loaded in\n", 404

@app.route('/metadata', methods = ['GET'])
def display_metadata() -> dict:
    """
    Lists all data in the 'metadata' dictionary object in the ISS data.

    Args:
        none
    Returns:
        metadata (dict): data in the 'metadata' dictionary
    """
    data = data_set()
    try:
        return data['ndm']['oem']['body']['segment']['metadata']
    except TypeError:
        return f"Data not loaded in\n", 404
    except KeyError:
        return f"Data not loaded in\n", 404 

#to run: curl -X DELETE localhost:5000/delete-data
@app.route('/delete-data', methods = ['DELETE'])
def del_data() -> str:
    """
    Deletes the ISS Trajectory Data stored in the global iss_data dictionary object.

    Args:
        none
    Returns:
        statement (str): verifiction the data has been deleted
    """
    global iss_data
    iss_data.clear()
    statement = "Deleted ISS data\n"
    return statement

#to run: curl -X POST localhost:5000/post-data
@app.route('/post-data', methods = ['POST'])
def retrieve_data() -> str:
    """
    Reloads the ISS Trajectory Data into the global iss_data dictionary object.

    Args:
        none
    Returns:
        statement (str): verifiction the data has been reloaded
    """
    global iss_data
    r = requests.get('https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    iss_data = xmltodict.parse(r.text)
    statement = "Successfully reloaded ISS data\n"    
    return statement
    
@app.route('/help', methods = ['GET'])
def define_routes() -> str:
    return '''\nUsage: curl 'localhost:5000[OPTIONS]'\n
    Options:\n
    1. /                                   returns entire ISS data set\n
    2. /epochs                             returns list of all EPOCHs\n
    3. /epochs?limit=<int>&offset=<int>    returns modified list of EPOCHs given query parameters of limit and offset\n
    4. /epochs/<epoch>                     returns state vectors for a specified <epoch>\n
    5. /epochs/<epoch>/speed               returns instantaneous speed for specified <epoch>\n
    6. /epochs/<epoch>/location            returns latitude, longitude, altitude, and geoposition for the specified <epoch>\n
    7. /now                                returns same data at #6, but for real time position of the ISS\n
    8. /comment                            returns 'comment' list from ISS data\n
    9. /header                             returns 'header' dictionary from ISS data\n
    10. /metadata                          returns 'metadata'dictionary from ISS data\n
    11. /delete-data                       deletes all data stored in the ISS data set dictionary\n
    12. /post-data                         reloads the ISS data set from the web into the dictionary object\n
'''

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')
