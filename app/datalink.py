import os
import sys
import pathlib
import pandas as pd
# for config saving and data download
import urllib
import gzip, json
import datetime as dt    

def extract_json_data(jsonfilename):
    with gzip.GzipFile(jsonfilename, 'r') as fin:
        #print('enc', json.detect_encoding(fin.read()))
        data = [json.loads(line,encoding='utf-8') for line in fin.readlines()]
        #data = json.loads(fin.read().decode('utf-8'),encoding='utf-8')
    return data
def get_dict_from_json_gzip_http(record_fname):
    """
    retrieves stored gzipped file from S3  
    """
    try:
        with urllib.request.urlopen(record_fname) as jf_gz:
            with gzip.open(jf_gz, 'r') as jf:
                data = json.loads(jf.read(),encoding='utf-8') 
    #except urllib.error.HTTPError as err:
    except:
        data = None
    return data
def save_appconfig(filename, config):
    """
    helper for saving the app config
    inputs : 
    file: filename for saving the configuration
    config: configuration object
    
    returns:
    None
    """
    
    remote_link  = os.environ['WG_CONFIG_PATH']
    print('saving config to file:', remote_link)
    data_json = gzip.compress (json.dumps(config).encode('utf-8'))
    req = urllib.request.Request(url=remote_link, data=data_json,method='PUT')
    with urllib.request.urlopen(req) as f:
        pass
    return

    #data_json = json.dumps(config)
    #with gzip.GzipFile(jsonfilename, 'r') as fin
    #with open(filename,'w') as cfile:
    #    cfile.write(data_json)
    return

def load_appconfig(filename, config=None):
    """
    helper for loading the app config
    loads the dictionary from the file and updates a config, or creates new config
    inputs : 
    file: filename for saving the configuration
    config: configuration object
    
    returns:
    None
    """
    new_config = get_dict_from_json_gzip_http(filename)
    
    if type(config) == type(None):
            response = new_config
    else:
        config.update(new_config)
        response = None
    return response

def init_config_file(local_data_folder, config_path, count_limit=3):
    # setup the application configuration
    config = dict()
    
    DATA_STORE = local_data_folder # this will point to the folder in the compute server in the cloud
    cities_Fname = os.path.join(DATA_STORE, 'weather_14.json.gz') # where the list of cities for initialization is stored
    country_retireve = 'CZ' # download data for cities in this country

    config['DATA_STORE'] = DATA_STORE
    config['WG_REMOTE_DATA_STORE'] = os.environ['WG_REMOTE_DATA_STORE'] # this will point to the AWS S3 

    config['OPENWEATHER_ONECALL_URL'] = 'https://api.openweathermap.org/data/2.5/onecall?'
    config['OPENWEATHER_QUERY'] = {'lat':None,
                                      'lon':None,
                                      'units':'metric'}
    config['CITY_LIST'] = [item['city'] for item in extract_json_data(cities_Fname)] # list of cities, links to their records and retrieval status

    # configure retrieval of weather information (staticaly, for all CZ cities from the list)
    limit = count_limit # for testing purposes, download only 3 cities

    for city in config['CITY_LIST']:
        if (city['country'] == country_retireve) and (limit>=0):
            city['retrieve'] = True
            #city['retrieval_interval(s)'] = 3600
            limit -=1
            print(city['name'])
        else:
            city['retrieve'] = False

    # save the config in a json file
    save_appconfig(config_path,config)
    return


def get_updated_city_list(form_location):
    # reload config
    new_config = load_appconfig(form_location)
    return new_config['CITY_LIST']

def get_city_latlon (city,country,city_list):
    lat=None
    lon=None
    for item in city_list:
            if item['country'] == country:
                if item['name'] == city:
                    city_found = True
                    lat=item['coord']['lat']
                    lon=item['coord']['lon']
                    break
    return (lat,lon)

def get_city_coord (city,country,city_list):
    response = None
    for item in city_list:
            if item['country'] == country:
                if item['name'] == city:
                    city_found = True
                    response = item['coord']
                    break
    return response

def query_for_city(city,country,url,query_template,city_list):
    (lat, lon) = get_city_latlon(city,country,city_list)
    query_dict = {}
    for key in query_template:
        query_dict[key] = query_template[key]
        if key == 'lat':
            query_dict[key] = lat
        if key == 'lon':
            query_dict[key] = lon
    queryS = url+"&".join([('%s=%s'% (qid,val)) for (qid, val) in query_dict.items()])     
    return queryS

def get_dict_from_data(record_fname):
    with open(record_fname) as jf:
        data = [json.loads(line,encoding='utf-8') for line in jf.readlines()]
    return data


def fetch_records_table_for_coord(engine,coord,units='metric'):
    """
    fetches metadata with links to the stored files, and related information
    """
    table_name = format_SQLtable_name(coord,units)
    response = None
    if  table_exists (engine,coord,units):
        query = ("SELECT * FROM %s;" % table_name)
        response = pd.read_sql(query,engine,index_col='timestamp')
    return response

def get_dict_from_data_http(record_fname):
    """
    retrieves stored file from S3  
    """
    with urllib.request.urlopen(record_fname) as jf:
        data = [json.loads(line,encoding='utf-8') for line in jf.readlines()]
    return data