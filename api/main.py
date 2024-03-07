from flask import Flask, render_template, request, send_file
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import math

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

@app.route('/patternscaling')
def calculate():
    try:
        filename = 'PatternScalingCoefficients_ssp370r1i1p1f1-ssp585r1i1p1f1_Regridded.nc'
        tbar              = float(request.args.get('tbar', 0))
        flat, flon, ftemp = patternscaling( tbar, filename )
        # Calculate global average from pattern scaling temperature map 
        # -- Should match the Tbar input (both if it is anomaly or absolute temperature)
        coslat        = np.cos( np.deg2rad( flat ) )
        weight_factor = coslat / coslat.mean() 
        zonalavg      = np.mean( ftemp, axis=1 )

        plt.switch_backend('Agg')
        # Set monospaced font properties using rcParams
        plt.rcParams['font.family'] = 'monospace'  # Choose the 'monospace' family
        # Plot
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.Robinson()})
        ax.coastlines()
        c = ax.contourf( flon, flat, ftemp, transform=ccrs.PlateCarree(), cmap='gist_ncar', levels=np.linspace(math.floor( ftemp.min() ), math.ceil( ftemp.max() ), 150) )
        cbar = plt.colorbar(c, ax=ax, label='Temperature Anomaly [K]', shrink = 0.5,  format="%.1f")
        plt.title('Multi-Model Estimate', fontsize=16)
        # Save the plot as an image file
        image_path = 'static/plot.png'
        plt.savefig( image_path )
        plt.close()
        # Display the result along with the plot
        return render_template('result_with_plot.html', tbarcalc=np.mean( zonalavg * weight_factor ), image_path=image_path)

    except ValueError:
        return 'Please enter valid numbers in the URL.'