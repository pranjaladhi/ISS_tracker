# Tracking the International Space Station 

### Purpose
One of the goals of this project is to develop a Flask application to query and return information regarding the position and velocity of the International Space Station (ISS) at a given time. The data of the ISS is supplied through the [NASA](https://spotthestation.nasa.gov/trajectory_data.cfm) website and is stored [here](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml), a XML data set. Taking the data, a Flask application is developed that exposes the data to the user by eight different routes with the user's input, all done within the file *iss_tracker.py*. A main objective of this project is to develop skills working with the Python Flask web framework and learn how to setup a REST API with multiple routes (URLs). Additionally, another object is to learn how to containerize the script with Docker for any user to utilize the script. Working with the Flask library will allow for the understanding of building web servers and allow for fimiliarization in understanding how they are used. Furthermore, learning how to containerize will allow for the sharing of programs to other users.

### Code Scripts
In the *iss_tracker.py* file, lines 14-24 `@app.route('/', methods = ['GET'])...` defines the URL `/` within the application. It takes an argument `methods` which is list of string containing the HTTP method `GET`. When the URL + HTTP combination is requested, the Python function below `def data_set()...` is called which returns the entire ISS data set in the XML file. In lines 27-57 `@app.route('/epochs', methods = ['GET'])...` the URL `/epochs` is requested, from which the function returns a list of all EPOCHs in the data set. In lines 37-40
```
try:
        num_epochs = request.args.get('limit', len(data['ndm']['oem']['body']['segment']['data']['stateVector']))
except KeyError:
        return "Data not loaded in\n"
```
the `try` block checks to verify if the ISS data has been loaded properly. If not, no data is output for the user as there is no data available. This is seen in other routes throughout the script to verify the ISS data has not been deleted in the script. In this specific route, the user is able to pass a query for `limit` and `offset`. If there is no query parameter passed, the default values of the length of the ISS data set and 0 will be set, respectively. This is seen in line 38
```
num_epochs = request.args.get('limit', len(data['ndm']['oem']['body']['segment']['data']['stateVector']))
```
and line 41
```
start = request.args.get('offset', 0)
```
If a query parameter is passed, the scrip will verify the correct data type is passed (int), seen in lines 42-51
```
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
```
In lines 54-56
```
while start < end:
        epochs.append(data['ndm']['oem']['body']['segment']['data']['stateVector'][start]['EPOCH'])
        start += 1
```
the while loop iterates through the `stateVector` list and extracts all values with the key `EPOCH`. Next, in lines 59-77 `@app.route('/epochs/<epoch>', methods = ['GET'])...` the URL `/epochs/<epoch>` is requested, with `<epoch>` being input by the user. This will call the function `def vectors(epoch: str) -> list:...` and return the state vectors for the specific `<epoch>`. This is performed in lines 72-75
```
if (data['ndm']['oem']['body']['segment']['data']['stateVector'][i]['EPOCH'] == epoch):
            state_vectors = []
            state_vectors.append(data['ndm']['oem']['body']['segment']['data']['stateVector'][i])
return state_vectors
```
where the `if (data['ndm']...` function will gather and return the state vector data if the iterated `['EPOCH']` matches the user input of `<epoch>`. This is also incased in a `try` block to verify the ISS data has been loaded in. From lines 79-96, `@app.route('/epochs/<epoch>/speed', methods = ['GET'])...` the speed of the ISS is returned with the user input of `<epoch>`. In line 89
```
data = vectors(epoch)
```
the function will first call the `def vectors(epoch: str) -> list:...` function (in line 60) to gather the state vectors in the specified `<epoch>`. Then, in lines 91-95
```
try:
        sumSpeedSquare = pow(float(data[0]['X_DOT']['#text']), 2) + pow(float(data[0]['Y_DOT']['#text']), 2) + pow(float(data[0]['Z_DOT']['#text']), 2)
except TypeError:
        return "Data not loaded in\n"
speed['Speed of EPOCH'] = (sqrt(sumSpeedSquare)) #magnitude of speed utilizing the x, y, and z components of speed
```
the `try` block will first verify the ISS data has been loaded, then the x, y, and z components of the ISS is extracted to compute the instantaneous speed at time `<epoch>`. In lines 99-103 `@app.route('/delete-data', methods = ['DELETE'])...` route will delete the ISS data stored in the global `iss_data` dictionary. This will result in the previous routes not working as the data is not available anymore. However, the data can be restored with the route in lines 106-111 `@app.route('/post-data', methods = ['POST'])...`, which will allow for the previous routes to function properly again. Lastly, in lines 113-124 `@app.route('/help', methods = ['GET'])...` route will allow for the user to seek help on how to run the routes described above.

### Running the Code
First, open two terminals. The first terminal will be used to utilize the the image from Docker Hub, which will be pulled with the line:
> `docker pull pranjaladhikari/iss_tracker:hw05`

Next, to run the containerized Flask app, run the line:
> `docker run -it --rm -p <host port>:<container port> pranjaladhikari/iss_tracker:hw05`

The flag `-p` is used to bind a port on the container to a port on the machine that is running the script. For example, if the Flask application is running on the port 5000, if the <container port> is not connected to port 5000 as well, then the Flask program won't be able to communicate with the machine.

If building a new image from the Dockerfile, both of the files *Dockerfile* and *iss_tracker.py* will need to be in the same directory. Afterwards, the image can be built with the line:
> `docker build -t <username>/iss_tracker:<version> .`

where `<username>` is your Docker Hub username. Afterwards, it can be ran with the line:
> `docker run -it --rm -p <host port>:<container port> <username>/iss_tracker:<version>`

After building and running the containerized Flask app in the first terminal, the server will be running. Now, the second terminal will be used for the API query commands. To start, run the line:
> `curl localhost:5000/help`

This will output brief descriptions of all the available routes in the API. An example may look like:
```
Usage: curl 'localhost:5000[OPTIONS]'

Options:
        1. /                                    returns entire ISS data set
        2. /epochs                              returns list of all EPOCHs
        3. /epochs?limit=<int>&offset=<int>     returns modified list of EPOCHs given query parameters of limit and offset
        4. /epochs/<epoch>                      returns state vectors for a specified EPOCH
        5. /epochs/<epoch>/speed                returns instantaneous speed for specified EPOCH
	6. /epochs/<epoch>/location		returns latitude, longitude, altitude, and geoposition for the specified <epoch>
	7. /now                                 returns same data at #6, but for real time position of the ISS
    	8. /comment                             returns 'comment' list from ISS data
    	9. /header                              returns 'header' dictionary from ISS data
    	10. /metadata                           returns 'metadata'dictionary from ISS data
    	11. /delete-data                        deletes all data stored in the ISS data set dictionary
    	12. /post-data                          reloads the ISS data set from the web into the dictionary object
```

The first route will make a request to the Flask app to return the entire ISS data set. It can be ran with the line:
> `curl localhost:5000/`

An example output may look like:
```
.
.
.

                },
                "Z": {
                  "#text": "1652.0698653803699",
                  "@units": "km"
                },
                "Z_DOT": {
                  "#text": "-5.7191913150960803",
                  "@units": "km/s"
                }
              }
            ]
          },
          "metadata": {
            "CENTER_NAME": "EARTH",
            "OBJECT_ID": "1998-067-A",
            "OBJECT_NAME": "ISS",
            "REF_FRAME": "EME2000",
            "START_TIME": "2023-048T12:00:00.000Z",
            "STOP_TIME": "2023-063T12:00:00.000Z",
            "TIME_SYSTEM": "UTC"
          }
        }
      },
      "header": {
        "CREATION_DATE": "2023-049T01:38:49.191Z",
        "ORIGINATOR": "JSC"
      }
    }
  }
}
```

Next, the second route will return all the EPOCHs data, and can be ran with the line:
> `curl localhost:5000/epochs`

The output may look like: 
```
.
.
.
  "2023-063T11:51:00.000Z",
  "2023-063T11:55:00.000Z",
  "2023-063T11:59:00.000Z",
  "2023-063T12:00:00.000Z"
]
```

Furthermore, the user has the ability to input query parameters for how many and which EPOCHs to return. It can be ran with the line:
> `curl 'localhost:5000/epochs?limit=<int>&offset=<int>'`

The user can input values in place of `<int>`. An example output for `limit=2&offset=4` may look like:
```
[
 "2023-058T12:16:00.000Z",
 "2023-058T12:20:00.000Z"
]   
```
        
Furthermore, running the line:
> `curl localhost:5000/epochs/<epoch>`

with '2023-063T12:00:00.000Z' in the place of `<epoch>` may result in the output of:
```
[
  {
    "EPOCH": "2023-063T12:00:00.000Z",
    "X": {
      "#text": "2820.04422055639",
      "@units": "km"
    },
    "X_DOT": {
      "#text": "5.0375825820999403",
      "@units": "km/s"
    },
    "Y": {
      "#text": "-5957.89709645725",
      "@units": "km"
    },
    "Y_DOT": {
      "#text": "0.78494316057540003",
      "@units": "km/s"
    },
    "Z": {
      "#text": "1652.0698653803699",
      "@units": "km"
    },
    "Z_DOT": {
      "#text": "-5.7191913150960803",
      "@units": "km/s"
    }
  }
]
```

The user also has the ability to output the speed of a specific EPOCH with the line:
> `curl localhost:5000/epochs/<epoch>/speed`

With '2023-063T12:00:00.000Z' in place of `<epoch>`, the output may be:
```
{
  "Speed of EPOCH": 7.661757196327827
}
```

If the user wanted to delete all ISS data gathered from the source, they can do so with the line:
> `curl -X DELETE localhost:5000/delete-data`

The `-X DELETE` is required as the route accepts a `DELETE` method, and not the default `GET` method. After running this route, the previous routes will result in error as the ISS data is no longer available for usage. The output will be:
```
Deleted ISS data
```

Lastly, if the user wanted to restore/reload the ISS data (reverse of the route above), it can be done so with the line:
> `curl -X POST localhost:5000/post-data`

Here, the `-X POST` is required as the route accepts a `POST` method, and not the default `GET` method. This route will allow the user to run previous routes above as the ISS data has been reloaded. The output after running this route will be:
```
Successfully reloaded data 
```
        
### ISS Data
The data used for this project is gathered from the NASA website for the ISS. The file which encompasses this data is in XML format, and contains the state vectors for each time set (or EPOCH) which this project utilizes. The state vectors data set lists the time in UTC; position X, Y, and Z in kilometers (km); and the velocity X, Y, and Z in kilometers per second (km/s). The data set can be found on the [NASA](https://spotthestation.nasa.gov/trajectory_data.cfm) website and is stored [here](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml).
