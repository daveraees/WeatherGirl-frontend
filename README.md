# WeatherGirl-frontend

Sample web app that displays historical weather information gathered form OpenWeatherMap.com. It is written in Python and uses Amazon Web Services (one S3 bucket and MySQL database hosted on RDS) cloud infrastructure.

The app looks-up the database to get list of filenames that contain weather information related to a specified geolocation (city, country). It then displays the data from JSON files retrieved from the S3 bucket. The application source code is ready for deployment in form of docker container.

## Prerequisites:
The app serves as a web UI to display data stored in the cloud infrastructure. The app must have access to the respective services, namely the S3 bucket and the mysql database server.
 
Another app [WeatherGirl-backend](https://github.com/daveraees/WeatherGirl-backend)  can be used to retrieve the weather info files from OpenWeatherMap and store the data files in the S3 bucket.
 
 
## Dependency requirements for running the server:

### libraries
- The app was tested and runs with python 3.7
- Libraries are specified in the file requirements.txt

### environment variables:
Before running the app itself from source code, or building of container, please make sure the following environmental variables are configured

- WG_S3BUCKET_NAME=appbucket # name of the file storage  server S3 buckeet
- WG_CONFIG_PATH=path/to/config/wg_config.json.gz # this file must be accessible also to the backend app, that uses it to execute the weather infro downloads
- WG_LOCAL_DATA_STORE=app/data # where small temporary file can be stored. No requirements for accessibility from other services
- WG_DATABASE_ENDPOINT=mysqlDB.example.com
- WG_DATABASE_USER="mysql_read_access_username"
- WG_DATABASE_PASS="mysql_password"
- WG_DATABASE_PORT: 3306
- WG_DATABASE_NAME: 'cities'
- WG_CITY_COUNT_LIMIT=60 # maximum number of cities that can be marked for download by the backend app.

## Usage:

running the web server locally from the source code in the root directory of the local git repository:

        $ python3 ./app/app.py
        
This will start the web server. The app will try to download the configuration file. If the config download fail, it will create new config, using the city locaiton database in file app/data/weather_14.json.gz

The files docker-compose.yml and Dockerfile contain instructions needed to build a docker image.

