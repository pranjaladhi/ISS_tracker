# Tracking International Space Station API 

## Purpose
This project develops a local Flask application to query and return information regarding the International Space Station (ISS). The data of the ISS is supplied through the [NASA](https://spotthestation.nasa.gov/trajectory_data.cfm) website and is stored [here](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml), a XML data set. Taking the data, a Flask application is developed that exposes the data to the user by twelve different routes with the user's input, all done within the file *iss_tracker.py*. A main objective of this project is to develop skills working with the Python Flask web framework and learn how to setup a REST API with multiple routes (URLs). Additionally, another object is to learn how to containerize the script with Docker for any user to utilize the script. Working with the Flask library will allow for the understanding of building web servers in a small scale and allow for fimiliarization in understanding how they are used.

## Running the Code

### With Docker
First, open two terminals. The first terminal will be used to utilize the the image from Docker Hub, which will be pulled with the line:
> `docker pull pranjaladhikari/iss_tracker:1.0`

Next, to run the containerized Flask app, run the line:
> `docker run -it --rm -p <host port>:<container port> pranjaladhikari/iss_tracker:1.0`

The flag `-p` is used to bind a port on the container to a port on the machine that is running the script. For example, if the Flask application is running on the port 5000, but the `<container port>` is not connected to port 5000, then the Flask program won't be able to communicate with the machine.

If building a new image from the Dockerfile, both of the files *Dockerfile* and *iss_tracker.py* will need to be in the same directory. Afterwards, the image can be built with the line:
> `docker build -t <username>/iss_tracker:<version> .`

where `<username>` is your Docker Hub username. Afterwards, it can be ran with the line:
> `docker run -it --rm -p <host port>:<container port> <username>/iss_tracker:<version>`

After pulling the image from the Docker Hub, the above processes of running and building can be simplified utilizing *docker-compose.yml*. This will automatically configure all options needed to start the container in a single file. Once the file is in the same directory as *Dockerfile* and *iss_tracker.py*, the container can be started with the line:
> `docker-compose up --build`

After building and running the containerized Flask app in the first terminal, the server will be running. Now, the second terminal will be used for the HTTP requests to the API.

### Requests to the API
With the container running in the other terminal, requests can be made to the API. To start, run the line:
> `curl localhost:5000/help`

This will output brief descriptions of all the available routes in the API. The output may look like:
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

> `curl localhost:5000/`

This first route will make a request to the Flask app to return the entire ISS Trajectory data set. An example output may look like:
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

> `curl localhost:5000/epochs`

This route will return all the EPOCHs (time set) data in the set. The output may look like: 
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

> `curl 'localhost:5000/epochs?limit=<int>&offset=<int>'`

This request gives the user the ability to input query parameters for the number of EPOCHs (limit) and beginning index (offset) to return. The user can input values in place of `<int>`. An example output for `limit=2&offset=4` may look like:
```
[
 "2023-058T12:16:00.000Z",
 "2023-058T12:20:00.000Z"
]   
```
        
START HERE Furthermore, running the line:
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
Successfully reloaded ISS data 
```
        
## ISS Data
The data used for this project is gathered from the NASA website for the ISS. The file which encompasses this data is in XML format, and contains the state vectors for each time set (or EPOCH) which this project utilizes. The state vectors data set lists the time in UTC; position X, Y, and Z in kilometers (km); and the velocity X, Y, and Z in kilometers per second (km/s). The data set can be found on the [NASA](https://spotthestation.nasa.gov/trajectory_data.cfm) website and is stored [here](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml).
