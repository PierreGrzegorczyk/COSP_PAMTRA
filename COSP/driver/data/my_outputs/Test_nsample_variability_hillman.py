from netCDF4 import Dataset
import matplotlib.pylab as plt
import numpy as np
import matplotlib
from mycolorpy import colorlist as mcp
from matplotlib import cm
import matplotlib.colors as colors
from datetime import datetime
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 13

import pandas as pd

## Output from cosp
nc_out = "C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0_lmdz_hillman\\driver\\data\\my_outputs\\Output.nc"
nc_out = Dataset(nc_out, "r")
z=np.array(nc_out.variables['lev'][:])/1000

ncol=100
nlvl=95

subcol_grid=1+np.arange(0,ncol,1)
## Cloud
path="C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0_lmdz_hillman\\driver\\data\\my_outputs\\Most_cloud_and_variability_nsamples1000\\"
Data_sub_mr=pd.read_csv(path+"Output_subcolumns_mratio.csv")
I_LSCICE_large=np.array(Data_sub_mr["I_LSCICE"]).reshape(nlvl,ncol)


path="C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0_lmdz_hillman\\driver\\data\\my_outputs\\Most_cloudy\\"
Data_sub_mr=pd.read_csv(path+"Output_subcolumns_mratio.csv")
I_LSCICE_novar=np.array(Data_sub_mr["I_LSCICE"]).reshape(nlvl,ncol)

plt.figure('Plot sample',figsize=(5,8))
plt.plot(np.mean(I_LSCICE_novar,1)*1000,z,label='Grid mean: no variability')
plt.plot(np.mean(I_LSCICE_large,1)*1000,z,label='Grid mean: variability Hillman')
plt.xlabel('qi mean (g kg-1)')
plt.ylim(0,14)
plt.ylabel('Altitude (km)')
plt.legend()
plt.tight_layout()
plt.savefig(path+"Mean_compare.png",dpi=600)
plt.show()