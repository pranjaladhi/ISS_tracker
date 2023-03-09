# Tracking the International Space Station API 

## Purpose
This project develops a local Flask application to query and return information regarding the International Space Station (ISS). The data of the ISS is supplied through the [NASA](https://spotthestation.nasa.gov/trajectory_data.cfm) website and is stored [here](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml), an XML data set. Taking the data, a Flask application is developed that exposes the data to the user by twelve different routes with the user's input, all done within the file *iss_tracker.py*.

A main objective of this project is to develop skills working with the Python Flask web framework and learn how to set up a REST API with multiple routes (URLs). Additionally, another object is to learn how to containerize the script with Docker for any user to utilize the script. Working with the Flask library will allow for the understanding of building web servers in a small scale and allow for familiarization in understanding how they are used.

## Running the Code

### Docker Setup
First, open two terminals. The first terminal will be used to utilize the image from Docker Hub, which will be pulled with the line:
> `docker pull pranjaladhikari/iss_tracker:1.0`

Next, to run the containerized Flask app, run the line:
> `docker run -it --rm -p <host port>:<container port> pranjaladhikari/iss_tracker:1.0`

The flag `-p` is used to bind a port on the container to a port on the machine that is running the script. For example, if the Flask application is running on the `<host port>` 5000, but the `<container port>` is not connected to port 5000, then the Flask program won't be able to start and communicate with the machine.

If building a new image from the Dockerfile, both of the files *Dockerfile* and *iss_tracker.py* must be in the same directory. Afterward, the image can be built with the line:
> `docker build -t <username>/iss_tracker:<version> .`

where `<username>` is your Docker Hub username and `<version>` is the version tag. Then, it can be ran with the line:
> `docker run -it --rm -p <host port>:<container port> <username>/iss_tracker:<version>`

After pulling the image from the Docker Hub, the above processes of building and running can be simplified utilizing *docker-compose.yml*. This will automatically configure all options needed to start the container in a single file. Once the file is in the same directory as *Dockerfile* and *iss_tracker.py*, the container can be started with the line:
> `docker-compose up --build`

With the commands above of building and running the containerized Flask app, the server will be running. Now, the second terminal will be used for the HTTP requests to the API.

### Requests to the API
With the container running in the other terminal, the second terminal can be used for requests to the API. To start, run the line:
#### > `curl localhost:5000/help`

This will output brief descriptions of all the available requests in the API. The output will look like:
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

#### > `curl localhost:5000/`

This first request will make a request to the Flask app to return the entire ISS Trajectory data set. An example output may look like:
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

#### > `curl localhost:5000/epochs`

This will return all the EPOCHs (time set) data. The output may look like: 
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

#### > `curl 'localhost:5000/epochs?limit=<int>&offset=<int>'`

This request gives the user the ability to input query parameters for the number of EPOCHs (limit) and beginning index (offset) to return. The user can input values in place of `<int>`. An example output for `limit=2&offset=4` may look like:
```
[
 "2023-058T12:16:00.000Z",
 "2023-058T12:20:00.000Z"
]   
```

#### > `curl localhost:5000/epochs/<epoch>`
This will return the positional and velocity data of the specified `<epoch>`. With '2023-063T12:00:00.000Z' in the place of `<epoch>` the route will output:
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

#### > `curl localhost:5000/epochs/<epoch>/speed`

This will return the speed of the specified `<epoch>`. With '2023-080T13:00:00.000Z' in place of `<epoch>`, the output will result in:
```
{
  "units": "km/s",
  "value": 7.650800966906994
}
```

#### > `curl localhost:5000/epochs/<epoch>/location`

This returns the location data of the specified `<epoch>`, including the latitude, longitude, and altitude of the ISS. Additionally, it will output the Earth ground location where the ISS is over. If the ISS is over a large body of water, the output will be `none`. With '2023-067T07:14:07.856Z' in place of `<epoch>`, the output will be:
```
{
  "altitude": {
    "units": "km",
    "value": 421.21897355423425
  },
  "geolocation": {
    "ISO3166-2-lvl4": "DZ-32",
    "country": "Algeria",
    "country_code": "dz",
    "county": "Brezina District",
    "state": "El Bayadh",
    "village": "Brezina"
  },
  "latitude": 31.84647224441941,
  "longitude": 2.123740015947945
}
```

#### > `curl localhost:5000/now`

This will return the same location data as in the request above, but for the current time position of the ISS. Additionally, the output will show which the closest EPOCH data was returned, and the time difference between the current time and EPOCH. The output may be:
```
{
  "closest_epoch": "2023-067T07:18:07.856Z",
  "location": {
    "altitude": {
      "units": "km",
      "value": 424.1789632030168
    },
    "geolocation": {
      "ISO3166-2-lvl4": "NE-1",
      "country": "Niger",
      "country_code": "ne",
      "county": "Bilma",
      "region": "Agadez Region"
    },
    "latitude": 20.659612551699656,
    "longitude": 13.140683424662214
  },
  "seconds_from_now": 105.94805455207825,
  "speed": {
    "units": "km/s",
    "value": 7.6620957205110525
  }
}
```

#### > `curl localhost:5000/comment`

This request returns the comment list from the ISS data set, which includes information regarding the events of the ISS. An example output may be:
```
[
  "Units are in kg and m^2",
  "MASS=473413.00",
  "DRAG_AREA=1421.50",
  "DRAG_COEFF=2.50",
  "SOLAR_RAD_AREA=0.00",
  "SOLAR_RAD_COEFF=0.00",
  "Orbits start at the ascending node epoch",
  "ISS first asc. node: EPOCH = 2023-03-06T15:56:39.441 $ ORBIT = 2588 $ LAN(DEG) = 73.09384",
  "ISS last asc. node : EPOCH = 2023-03-21T13:33:16.732 $ ORBIT = 2819 $ LAN(DEG) = 20.51128",
  "Begin sequence of events",
  "TRAJECTORY EVENT SUMMARY:",
  null,
  "|       EVENT        |       TIG        | ORB |   DV    |   HA    |   HP    |",
  "|                    |       GMT        |     |   M/S   |   KM    |   KM    |",
  "|                    |                  |     |  (F/S)  |  (NM)   |  (NM)   |",
  "=============================================================================",
  "GMT067 Reboost Optio  067:19:47:00.000             0.6     428.1     408.5",
  "(2.0)   (231.2)   (220.5)",
  null,
  "Crew05 Undock         068:08:00:00.000             0.0     428.7     409.9",
  "(0.0)   (231.5)   (221.3)",
  null,
  "SpX27 Launch          074:00:30:00.000             0.0     428.4     408.9",
  "(0.0)   (231.3)   (220.8)",
  null,
  "SpX27 Docking         075:12:00:00.000             0.0     428.4     408.7",
  "(0.0)   (231.3)   (220.7)",
  null,
  "=============================================================================",
  "End sequence of events"
]
```

#### > `curl localhost:5000/header`

This will return the header dictionary object, which includes information of when the data file was created. The output may be:
```
{
  "CREATION_DATE": "2023-066T03:37:31.258Z",
  "ORIGINATOR": "JSC"
}
```

#### > `curl localhost:5000/metadata`

This will output the metadata dictionary object, which contains information regarding the ISS and the start/stop time of collection of the ISS data. An example output is:
```
{
  "CENTER_NAME": "EARTH",
  "OBJECT_ID": "1998-067-A",
  "OBJECT_NAME": "ISS",
  "REF_FRAME": "EME2000",
  "START_TIME": "2023-065T15:02:07.856Z",
  "STOP_TIME": "2023-080T15:02:07.856Z",
  "TIME_SYSTEM": "UTC"
}
```

#### > `curl -X DELETE localhost:5000/delete-data`

This will delete the ISS data gathered from the source. The `-X DELETE` is required as the route accepts a `DELETE` method, and not the default `GET` method. After running this request, the previous requests will result in error as the ISS data is no longer available for usage. The output of running this request will be:
```
Deleted ISS data
```

If any of the requests above are ran after running this deleted request, the routes will return a 404 error with the message:
```
Data not loaded in
```

#### > `curl -X POST localhost:5000/post-data`

Lastly, this will restore/reload the ISS data from the source (reverse of the route above). Here, the `-X POST` is required as the route accepts a `POST` method, and not the default `GET` method. This route will allow the user to run previous routes above as the ISS data has been reloaded. The output after running this request will be:
```
Successfully reloaded ISS data 
```