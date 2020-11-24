# imports
from flask import Flask, render_template, make_response, request
import os
import sys
import pathlib
import datetime as dt
import urllib.request

# for the data processing
import pandas as pd

# for connection to SQL database
#from sqlalchemy import create_engine

# Local imports
#sys.path.insert(0, str(pathlib.Path(__file__).parent))
from datalink import get_dict_from_data_http, get_updated_city_list, get_city_coord, load_appconfig, init_config_file
from db_access import fetch_records_table_for_coord, engine


app = Flask(__name__)
city_list = get_updated_city_list(form_location=os.environ['WG_CONFIG_PATH']) # update using the list of records stored on local disk
app.config['CITY_LIST'] = city_list


@app.route('/')
@app.route('/index')
def index():
    citiesLST = []
    display_country = 'CZ'
    for item in app.config['CITY_LIST']:
        if item['country'] == display_country:
            if item['retrieve']==True:
                citiesLST.append(item['name'])
    return render_template('list_of_cities.html', cities = citiesLST, country=display_country)
    #return render_template('index.html')

@app.route('/<country>')
def show_cities(country):
    citiesLST = []
    for item in app.config['CITY_LIST']:
        if item['country'] == country:
            citiesLST.append(item['name'])
    return render_template('list_of_cities.html', cities = citiesLST, country=country)

@app.route('/list_of_countries')
def show_countries():
    countryLST = []
    for item in app.config['CITY_LIST']:
        country=item['country']
        if not country in countryLST:
            countryLST.append(country)
        else:
            pass
    return render_template('list_of_countries.html',title='List of countries', countries=countryLST)    

@app.route('/query')
def show_city():
    """
    display the stored weather records for given city
    """
    timestamp = request.args.get('timestamp')
    country=request.args.get('country')
    city=request.args.get('city')
    coord = get_city_coord(city,country,app.config['CITY_LIST'])
    
    records_pd = fetch_records_table_for_coord(engine,coord) # list of records downloaded for this city
    if type(records_pd)!=type(None):
        record_filenames = list(records_pd['data_storage_link'].values )
        DS_link  = os.environ['WG_REMOTE_DATA_STORE']
        record_links = [urllib.parse.urljoin (DS_link,record_filename) for record_filename in record_filenames ]
        record_timestamps = list(records_pd.index.values)
        record_dates = [dt.datetime.fromtimestamp(int(ts)) for ts in record_timestamps] # formated for display in the web pages
        # select apropriate timestamp to display:
        if timestamp==None:
            record_idx = -1
        else:
            record_idx = record_timestamps.index(timestamp)
        record_link = record_links[record_idx]
        record_dict = get_dict_from_data_http(record_link)[-1]
        info_date = dt.datetime.fromtimestamp(record_dict['current']['dt']).isoformat()
        weather_info_table = pd.json_normalize(record_dict['current']).loc[:,'sunrise':'wind_deg'].to_html(index=False)
        forecast_table = pd.json_normalize(record_dict['hourly']).loc[:,'dt':'wind_deg']
        tsIndex = [dt.datetime.fromtimestamp(ts) for ts in forecast_table['dt'].values]
        forecast_table['dt'] = tsIndex
        forecast_table.set_index('dt',inplace=True)
        forecast_info_table = forecast_table.to_html(index=True)
        response = render_template('city.html', 
                                   country=country, 
                                   name=city,
                                   other_records=zip(record_dates,record_timestamps),
                                   weather_info=weather_info_table,
                                   forecast_info = forecast_info_table,
                                   info_date=info_date)
    else:
        response = render_template('city_not_found.html', 
                                   country=country, 
                                   name=city,
                                   )
    return response


#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    print ("Downloading the data from the OpenWeatherService")
    
    
    response = urllib.urlopen('https://wordpress.org/plugins/about/readme.txt')
    data = response.read()
    print(data)
    return ("nothing")

@app.route("/graphics/<city>(<country>).png")
def plot_param(city,country,plot_parameter='main.temp'):
    """
    placeholder function to put graphics generation code
    """
    response = ''
    return response

if __name__ == '__main__':
    config = load_appconfig(os.environ['WG_CONFIG_PATH'])
    if config == None:
        # initialize the config file if none is found
        local_data_folder=os.environ['WG_LOCAL_DATA_STORE']
        config_path=os.environ['WG_CONFIG_PATH']
        init_config_file(local_data_folder, config_path, count_limit=os.environ['WG_CITY_COUNT_LIMIT'])
        config = load_appconfig(os.environ['WG_CONFIG_PATH'])
    app.run(debug=True, host='0.0.0.0')
    
    