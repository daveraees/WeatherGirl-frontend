from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter




def plot_param(city,country,plot_parameter='main.temp'):
    from modules.datalink import extract_json_data
    city_found = False # indicator whether the city was found among cities in the given country
    graph_filename = 'blank.png' # filename of the weather prediciton graph
    hourly_14 = extract_json_data('data/hourly_14.json.gz')
    for item in hourly_14:
        if item['city']['country'] == country:
            if item['city']['name'] == city:
                city_found = True
                forecast_date = dt.datetime.fromtimestamp(item['time']).isoformat() # forecast date
                break
    hourly_14_city_df = pd.json_normalize(item['data'])
    tsIndex = [dt.datetime.fromtimestamp(ts) for ts in pd.to_datetime(hourly_14_city_df['dt']).values]
    hourly_14_city_df['timestamp'] =tsIndex
    hourly_14_city_df.set_index('timestamp',inplace=True);
    
    # extract the data to plot
    temps = hourly_14_city_df[plot_parameter]
    t = temps.index
    s = temps.values
    
    # create the figure
    fig=Figure()
    ax=fig.add_subplot(111)
    ax.plot_date(t, s,'-')
    fig.autofmt_xdate(rotation=45)
    ax.set(xlabel='dates', ylabel=plot_parameter,
           title=('weather forecast ISO date: %s' % forecast_date))
    ax.grid()
    # generate the picture  data 
    canvas=FigureCanvas(fig)
    png_output =   BytesIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    #fig.savefig("graphics/test.png")
    return response
