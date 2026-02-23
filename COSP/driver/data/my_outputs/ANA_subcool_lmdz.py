from netCDF4 import Dataset
import matplotlib.pylab as plt
import numpy as np
import matplotlib
# from mycolorpy import colorlist as mcp
from matplotlib import cm
import matplotlib.colors as colors
from datetime import datetime
import matplotlib.pyplot as plt

import pandas as pd

## Output from cosp
nc_out = "C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0_lmdz_hillman\\driver\\data\\my_outputs\\Output.nc"
nc_out = Dataset(nc_out, "r")
z=np.array(nc_out.variables['lev'][:])/1000

# ## vertical grid lmdz
#
# path="C:\\Users\\grzegorczyk\\AWACA\\COSP\\output_lmdz"
# nc_file = path+"\\histhf.nc"
# nc_data = Dataset(nc_file, "r")
#
# z=np.array(nc_data.variables['zfull'][:][0,:,0,0])/1000

nb_subcol=100
subcol_grid=1+np.arange(0,100,1)
## Cloud
path="C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0_lmdz_hillman\\driver\\data\\my_outputs\\"
# path="C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0_lmdz_hillman\\driver\\data\\my_outputs\\Most_cloud_and_variability_nsamples1000\\"
# path="C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0_lmdz\\driver\\data\\my_outputs\\old_outputs\\"

Data_sub=pd.read_csv(path+"Output_subcolumns.csv")

nlvl=95
ncol=100
Cloud_column=np.array(Data_sub["column"]).reshape(nlvl,ncol)
# level=np.array(Data_sub["level"]).reshape(nlvl,ncol)
frac=np.array(Data_sub["frac"]).reshape(nlvl,ncol)
fracprec=np.array(Data_sub["fracprec"]).reshape(nlvl,ncol)

plt.figure('fig subcols',figsize=(10,4))
plt.subplot(121)
plt.title('Cloud subcol')
plt.pcolormesh(subcol_grid,z,frac)
plt.ylim(0,14)

plt.xlabel('Subcol')
plt.ylabel('Altitude (km)')
plt.colorbar(label="Cloud type index")

plt.subplot(122)
plt.title('Precipitation subcol')
plt.pcolormesh(subcol_grid,z,fracprec)
plt.colorbar(label="Precip index")
plt.xlabel('Subcol')
plt.ylim(0,14)
plt.ylabel('Altitude (km)')
plt.tight_layout()
plt.savefig(path+"subgrid_col.png",dpi=600)


Data_sub_mr=pd.read_csv(path+"Output_subcolumns_mratio.csv")


I_CVCLIQ=np.array(Data_sub_mr["I_CVCLIQ"]).reshape(nlvl,ncol)
I_CVCICE=np.array(Data_sub_mr["I_CVCICE"]).reshape(nlvl,ncol)
I_LSCLIQ=np.array(Data_sub_mr["I_LSCLIQ"]).reshape(nlvl,ncol)
I_LSCICE=np.array(Data_sub_mr["I_LSCICE"]).reshape(nlvl,ncol)

I_CVRAIN=np.array(Data_sub_mr["I_CVRAIN"]).reshape(nlvl,ncol)
I_CVSNOW=np.array(Data_sub_mr["I_CVSNOW"]).reshape(nlvl,ncol)
I_LSRAIN=np.array(Data_sub_mr["I_LSRAIN"]).reshape(nlvl,ncol)
I_LSSNOW=np.array(Data_sub_mr["I_LSSNOW"]).reshape(nlvl,ncol)

arrays = [I_CVCLIQ, I_CVCICE, I_LSCLIQ, I_LSCICE,I_CVRAIN, I_CVSNOW, I_LSRAIN, I_LSSNOW]
titles = ["I_CVCLIQ", "I_CVCICE", "I_LSCLIQ", "I_LSCICE","I_CVRAIN", "I_CVSNOW", "I_LSRAIN", "I_LSSNOW"]

arrays = [I_LSCLIQ, I_LSCICE, I_LSRAIN, I_LSSNOW]
titles = ["I_LSCLIQ", "I_LSCICE", "I_LSRAIN", "I_LSSNOW"]

labels=["Large scale ql (g kg-1)","Large scale qi (g kg-1)","Large scale qr (g kg-1)","Large scale qs (g kg-1)"]

# Create figure and subplots (3 rows x 3 cols to leave one empty if desired)
cmap = plt.get_cmap('viridis', 50)
cmap.set_under('white')

fig, axes = plt.subplots(2, 2, figsize=(8, 8))
axes = axes.flatten()

for i, (ax, arr, title,label) in enumerate(zip(axes, arrays, titles,labels)):
    if i>2:
        vmax=0.03
    else:
        vmax=0.1
    im = ax.pcolormesh(subcol_grid,z,arr*1000,vmax=vmax,vmin=1e-25,cmap="viridis")

    ax.set_title(label[:-8], fontsize=10)
    fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.046, pad=0.04,label=label)
    ax.set_xlabel('Subcol')
    ax.set_ylabel('Altitude (km)')
    ax.set_ylim(0,14)
plt.suptitle("Cloud and precip subcolumns", fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(path+"subgrid_mr.png",dpi=600)




pfrac_test=[0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.334711879,0.355284542,0.357359231,0.358069956,0.357114583,0.355228513,0.353848785,0.352313101,0.317387968,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.880891204,0.899871647,0.899847448,0.772919655,0.760382414,0.884870231,0.780659139,0.300000012,0.775534272,0.351571470,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012]





plt.figure('precip fraction profile',figsize=(4,5))
plt.xlabel('Precipitation fraction in gridbox')
plt.plot(pfrac_test,z)
plt.ylabel('Altitude (km)')
plt.ylim(0,14)
plt.xlim(0,1)
plt.tight_layout()
plt.savefig(path+"Precip_fraction_test_profiles.png",dpi=600)

## Full read of subcols

path="C:\\Users\\grzegorczyk\\AWACA\\COSP\\COSPv2.0_lmdz_hillman\\driver\\run"
nc_file = path+"\\hydro_output.nc"
nc_data = Dataset(nc_file, "r")

Qi=nc_data['I_LSCICE'][:]
Ql=nc_data['I_LSCLIQ'][:]
Qr=nc_data['I_LSRAIN'][:]
Qs=nc_data['I_LSSNOW'][:]

plt.figure('test')
plt.imshow(np.mean(Qi[:,:,:]*1000,1))
plt.show()
