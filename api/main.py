from flask import Flask, render_template, request, send_file
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from flask_cors import CORS\

#####################################
def patternscaling( Tbar, filename ):
    # Tbar can be either absolute temperature or anomaly
    # The function checks if Tbar is lower than 100 to determine which one is which
    n4obj      = nc.Dataset( filename, 'r' )
    lon        = n4obj.variables['lon']
    lat        = n4obj.variables['lat']
    alpha      = n4obj.variables['slope']
    beta       = n4obj.variables['intercept']
    if Tbar < 100:
      # User likely passed temperature anomaly
      pstemp = alpha[:]*Tbar # Temperature Anomaly [K]
    else: 
      # User likely passed absolute temperatre
      pstemp = alpha[:]*Tbar + beta[:] # Absolute Temperature [K]
    # Return 
    return lat[:], lon[:], pstemp[:]
#####################################

app = Flask(__name__)
CORS(app)
# todo how many simultaneous requests can this handle
@app.route('/temperature')
def get_temperature():
    # try: 
    filename = 'PatternScalingCoefficients_ssp370r1i1p1f1-ssp585r1i1p1f1_Regridded.nc'
    tbar              = float(request.args.get('tbar', 0))
    flat, flon, ftemp = patternscaling( tbar, filename )

    return {
        "lats": flat.tolist(),
        "lons": flon.tolist(),
        "temps": ftemp.tolist(),
        "minTemperature": str(np.min(ftemp)), 
        "maxTemperature": str(np.max(ftemp))
    }
    # except:
    #     return 'Please enter valid numbers in the URL.'