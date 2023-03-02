#Pranjal Adhikari pa8729

from flask import Flask, request
import requests
import xmltodict
from math import sqrt

r = requests.get('https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
iss_data = xmltodict.parse(r.text)

app = Flask(__name__)


@app.route('/', methods = ['GET'])
def data_set():
    """
    Outputs the entire ISS Trajectory Data found on the NASA website.

    Args:
        none
    Returns:
        iss_data (dictionary): ISS data set
    """
    return iss_data

#to run with query parameter: curl 'localhost:5000/epochs?limit=int&offset=int'
@app.route('/epochs', methods = ['GET'])
def modified_epoch():
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
    except KeyError:
        return "Data not loaded in\n"
    start = request.args.get('offset', 0)
    if num_epochs:
        try:
            num_epochs = int(num_epochs)
        except ValueError:
            return "Limit must be an integer\n"
    if start:
        try:
            start = int(start)
        except ValueError:
            return "Start must be an integer\n"
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
    try:
        for i in range(len(data['ndm']['oem']['body']['segment']['data']['stateVector'])):
            if (data['ndm']['oem']['body']['segment']['data']['stateVector'][i]['EPOCH'] == epoch):
                state_vectors = []
                state_vectors.append(data['ndm']['oem']['body']['segment']['data']['stateVector'][i])
            return state_vectors
    except KeyError:
        return "Data not loaded in\n"
    
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
    speed = {}
    try:
        sumSpeedSquare = pow(float(data[0]['X_DOT']['#text']), 2) + pow(float(data[0]['Y_DOT']['#text']), 2) + pow(float(data[0]['Z_DOT']['#text']), 2)
    except TypeError:
        return "Data not loaded in\n"
    speed['Speed of EPOCH'] = (sqrt(sumSpeedSquare)) #magnitude of speed utilizing the x, y, and z components of speed
    return speed

#to run: curl -X DELETE localhost:5000/delete-data
@app.route('/delete-data', methods = ['DELETE'])
def del_data():
    global iss_data
    iss_data.clear()
    return "Deleted ISS data\n"

#to run: curl -X POST localhost:5000/post-data
@app.route('/post-data', methods = ['POST'])
def retrieve_data():
    global iss_data
    r = requests.get('https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    iss_data = xmltodict.parse(r.text)
    return "Successfully reloaded data\n"

@app.route('/comment', methods = ['GET'])
def display_comments():
    data = data_set()
    comments = []
    for i in range(len(data['ndm']['oem']['body']['segment']['data']['COMMENT'])):
        comments.append(data['ndm']['oem']['body']['segment']['data']['COMMENT'][i])
    #for ndm, oem, body, segment, datas in data.items():
        #for val in datas:
            #comments.append(datas[val])        
    #res = [val[temp] for key, val in data.items() if temp in val]
    #print(str(res))
    return comments

@app.route('/help', methods = ['GET'])
def define_routes():
    return '''\nUsage: curl 'localhost:5000[OPTIONS]'\n
    Options:\n
    1. /                                   returns entire ISS data set\n
    2. /epochs                             returns list of all EPOCHs\n
    3. /epochs?limit=<int>&offset=<int>    returns modified list of EPOCHs given query parameters of limit and offset\n
    4. /epochs/<epoch>                     returns state vectors for a specified EPOCH\n
    5. /epochs/<epoch>/speed               returns instantaneous speed for specified EPOCH\n
    6. /delete-data                        deletes all data stored in the ISS data set dictionary\n
    7. /post-data                          reloads the ISS data set from the web into the dictionary object\n
'''

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')
