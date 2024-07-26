from flask import Flask, request
import netCDF4 as nc
import numpy as np

from flask_cors import CORS

# ################ OLD PS #####################
# def patternscaling( Tbar, filename ):
#     # Tbar can be either absolute temperature or anomaly
#     # The function checks if Tbar is lower than 100 to determine which one is which
#     n4obj      = nc.Dataset( filename, 'r' )
#     lon        = n4obj.variables['lon']
#     lat        = n4obj.variables['lat']
#     alpha      = n4obj.variables['slope']
#     beta       = n4obj.variables['intercept']
#     if Tbar < 100:
#         # User likely passed temperature anomaly
#         pstemp = alpha[:]*Tbar # Temperature Anomaly [K]
#     else: 
#         # User likely passed absolute temperatre
#         pstemp = alpha[:]*Tbar + beta[:] # Absolute Temperature [K]
#     # Return 
#     return lat[:], lon[:], pstemp[:]
# #####################################

#####################################
def patternscaling( Tbar, filename ):
    # Tbar can be either absolute temperature or anomaly
    # The function checks if Tbar is lower than 100 to determine which one is which
    n4obj      = nc.Dataset( filename, 'r' )
    lon        = n4obj.variables['lon']
    lat        = n4obj.variables['lat']
    alpha      = n4obj.variables['slope']
    # preindustrial climatology
    # i.e. on average what the temperature (or precipitation) was everywhere in preindustrial conditions
    climo      = n4obj.variables['climatology']
    pspred     = alpha[:]*Tbar # Anomaly
    # relative change in percentage compared to climatology 
    # (e.g. value of 50% means that in that location PS predicts that it would rain 50% more than the preindustrial average)    
    relchange  = pspred/climo * 100
    # Return 
    return lat[:], lon[:], pspred[:], relchange, climo[:]
#####################################

app = Flask(__name__)
CORS(app)
# todo how many simultaneous requests can this handle
@app.route('/temperature')
def get_temperature():
    # try: 
    filename = 'PatternScalingCoefficients_tas_ssp245-ssp370__r180x90.nc'
    tbar              = float(request.args.get('tbar', 0))
    flat, flon, ftemp, _, _ = patternscaling( tbar, filename )
    
    return {
        "lats": flat.tolist(),
        "lons": flon.tolist(),
        "temps": ftemp.tolist(),
        "minTemperature": str(np.min(ftemp)), 
        "maxTemperature": str(np.max(ftemp))
    }
    # except:
    #     return 'Please enter valid numbers in the URL.'

@app.route('/precipitation')
def get_precipitation():
    # try: 
    filename = 'PatternScalingCoefficients_pr_ssp245-ssp370__r180x90.nc'
    tbar              = float(request.args.get('tbar', 0))
    flat, flon, fprecipitation, fprel, _  = patternscaling( tbar, filename )
    print('lat', flat)
    print('lon', flat)
    print('len', len(flat), len(flon))
    
    return {
        "lats": flat.tolist(),
        "lons": flon.tolist(),
        "changes": fprel.tolist(),
        # "minPrecipitation": str(np.min(fprecipitation)), 
        # "maxPrecipitation": str(np.max(fprecipitation))
    }
    # except:
    #     return 'Please enter valid numbers in the URL.'




if __name__ == '__main__':  
    app.run(debug = True, host = "0.0.0.0", port=5002)
