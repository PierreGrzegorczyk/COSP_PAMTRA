from netCDF4 import Dataset
import matplotlib.pylab as plt
import numpy as np
import matplotlib
from mycolorpy import colorlist as mcp
from matplotlib import cm
import matplotlib.colors as colors

from datetime import datetime
import matplotlib

import matplotlib.pyplot as plt
import numpy as np


## ECMWF
from netCDF4 import Dataset
import csv

nc_file = "C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0\\driver\\data\\inputs\\UKMO\\cosp_input.um_global.nc"

nc_data = Dataset(nc_file, "r")

lon = nc_data.variables['lon'][:]
lat = nc_data.variables['lat'][:]
Alt = nc_data.variables['height'][:] #2d and probably terrain following coordinates
qv = nc_data.variables['qv'][:]
Reff=nc_data.variables['Reff'][:]
tca=nc_data.variables['tca'][:]#total cloud amount, cloud fraction ?

fl_lssnow=nc_data.variables['fl_lssnow'][:]#flux large scale snow
fl_lsrain=nc_data.variables['fl_lsrain'][:]#flux large scale rain


mr_ccice=nc_data.variables['mr_ccice'][:]# convective mixing ratio of cloud ice
mr_ccliq=nc_data.variables['mr_ccliq'][:]# convective mixing ratio of cloud liquid
# UKMO Feb 2007

# model_level_number = nc_data.variables['model_level_number'][:]
lon_mesh = np.tile(lon, (Alt.shape[0], 1))

plt.figure('test1',figsize =(20,15))

ly=0
plt.subplot(331)
plt.pcolormesh(lon,Alt[:,ly,0]/1000,tca[:,ly,:],cmap="jet")  # Alt in km

ly=6
plt.subplot(332)
plt.pcolormesh(lon,Alt[:,ly,0]/1000,tca[:,ly,:],cmap="jet")  # Alt in km

ly=12
plt.subplot(333)
plt.pcolormesh(lon,Alt[:,ly,0]/1000,tca[:,ly,:],cmap="jet")  # Alt in km

ly=18
plt.subplot(334)
plt.pcolormesh(lon,Alt[:,ly,0]/1000,tca[:,ly,:],cmap="jet")  # Alt in km

ly=24
plt.subplot(335)
plt.pcolormesh(lon,Alt[:,ly,0]/1000,tca[:,ly,:],cmap="jet")  # Alt in km

ly=30
plt.subplot(336)
plt.pcolormesh(lon,Alt[:,ly,0]/1000,tca[:,ly,:],cmap="jet")  # Alt in km


plt.xlabel('Grid')
plt.ylabel('Altitude [km]')
plt.colorbar(label='TCA')
plt.tight_layout()
plt.show()





## Analyze outputs from cosp
nc_out = "C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0\\driver\\data\\my_outputs\\Output_global.nc"
nc_out = Dataset(nc_out, "r")
output_file = "C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0\\driver\\data\\my_outputs\\variable_standard_names_global.csv"

# Prepare list of (variable_name, standard_name)
variable_standard_list = []
for var_name in nc_out.variables:
    var = nc_out.variables[var_name]
    if 'standard_name' in var.ncattrs():
        variable_standard_list.append((var_name, var.getncattr('standard_name')))


# Write to CSV
with open(output_file, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Variable', 'Standard_Name'])  # Header
    writer.writerows(variable_standard_list)

print(f"Saved {len(variable_standard_list)} entries to {output_file}")



DBZ_cloudsat=np.array(nc_out.variables['dbze94'][:])
DBZ_cloudsat_cfad=np.array(nc_out.variables['cfadDbze94'][:])
DBZ_cloudsat=DBZ_cloudsat.reshape(54,20,36,48)

# DBZ_cloudsat[DBZ_cloudsat<-30]=np.nan
fontsize_title=15

cmap = plt.get_cmap('jet', 14)
cmap.set_under('white')
vmin_x = -30
vmax_x = 15

lvl=30
plt.figure('Cloudsat Radar DBZ (Mean over subcolumns)')
plt.title('Altitude approx '+str(np.mean(Alt[lvl])/1000)+ ' km')
plt.pcolormesh(lon,lat,DBZ_cloudsat[lvl,10,:,:],vmin=vmin_x,vmax=vmax_x,cmap=cmap) #315
plt.colorbar(label='Cloudsat radar reflectivity (dBZ)')
plt.show()
















