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

## Input for cosp
path0="/home/grzegorc/AWACA/LMDZ/OUT_golden_case_v5/"

Cosp_in=path0+"cosp_input_from_lmdz_golden_case_v5.nc"
Cosp_in = Dataset(Cosp_in, "r")

z=np.array(Cosp_in.variables['height'][:])/1000
time=np.arange(0,0.25*len(Cosp_in.variables['t'][:]),0.25)


## Output from cosp
nc_out = "/home/grzegorc/AWACA/COSP/COSPv2.0_lmdz_hillman_precip/driver/run/hydro_output_golden_case_v5.nc"
nc_out = Dataset(nc_out, "r")

nb_subcol=100
subcol_grid=1+np.arange(0,100,1)

I_LSCLIQ=nc_out["I_LSCLIQ"][:]
I_LSCICE=nc_out["I_LSCICE"][:]#np.array(Data_sub_mr[""]).reshape(nlvl,ncol)


I_LSRAIN=nc_out["I_LSRAIN"][:]
I_LSSNOW=nc_out["I_LSSNOW"][:]

## Plot Subcols

#
#
# plt.figure('fig subcols',figsize=(10,4))
# plt.subplot(121)
# plt.title('Cloud subcol')
# plt.pcolormesh(subcol_grid,z,frac)
# plt.ylim(0,14)
#
# plt.xlabel('Subcol')
# plt.ylabel('Altitude (km)')
# plt.colorbar(label="Cloud type index")
#
# plt.subplot(122)
# plt.title('Precipitation subcol')
# plt.pcolormesh(subcol_grid,z,fracprec)
# plt.colorbar(label="Precip index")
# plt.xlabel('Subcol')
# plt.ylim(0,14)
# plt.ylabel('Altitude (km)')
# plt.tight_layout()
# plt.savefig(path+"subgrid_col.png",dpi=600)
#
#
# Data_sub_mr=pd.read_csv(path+"Output_subcolumns_mratio.csv")
#


#
# arrays = [I_CVCLIQ, I_CVCICE, I_LSCLIQ, I_LSCICE,I_CVRAIN, I_CVSNOW, I_LSRAIN, I_LSSNOW]
# titles = ["I_CVCLIQ", "I_CVCICE", "I_LSCLIQ", "I_LSCICE","I_CVRAIN", "I_CVSNOW", "I_LSRAIN", "I_LSSNOW"]

arrays = [I_LSCLIQ, I_LSCICE, I_LSRAIN, I_LSSNOW]
titles = ["I_LSCLIQ", "I_LSCICE", "I_LSRAIN", "I_LSSNOW"]

labels=["Large scale ql (g kg-1)","Large scale qi (g kg-1)","Large scale qr (g kg-1)","Large scale qs (g kg-1)"]

# Create figure and subplots (3 rows x 3 cols to leave one empty if desired)
cmap = plt.get_cmap('viridis', 50)
cmap.set_under('white')

fig, axes = plt.subplots(2, 2, figsize=(8, 8))
axes = axes.flatten()
t=450

for i, (ax, arr, title,label) in enumerate(zip(axes, arrays, titles,labels)):
    if i>2:
        vmax=0.25
    else:
        vmax=0.25
    im = ax.pcolormesh(subcol_grid,z[::-1,t],arr[:,:,t]*1000,vmax=vmax,vmin=1e-25,cmap="viridis")

    ax.set_title(label[:-8], fontsize=10)
    fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.046, pad=0.04,label=label)
    ax.set_xlabel('Subcol')
    ax.set_ylabel('Altitude (km)')
    ax.set_ylim(0,14)
plt.suptitle("Cloud and precip subcolumns", fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.95])
# plt.savefig(path+"subgrid_mr.png",dpi=600)
plt.show()

#time plot
fig, axes = plt.subplots(2, 2, figsize=(8, 8))
axes = axes.flatten()
col=4
for i, (ax, arr, title,label) in enumerate(zip(axes, arrays, titles,labels)):
    if i>2:
        vmax=1.5
    else:
        vmax=1.5
    im = ax.pcolormesh(time,z[::-1,t],arr[:,col,:]*1000,vmax=vmax,vmin=1e-25,cmap="viridis")

    ax.set_title(label[:-8], fontsize=10)
    fig.colorbar(im, ax=ax, orientation='vertical', fraction=0.046, pad=0.04,label=label)
    ax.set_xlabel('Subcol')
    ax.set_ylabel('Altitude (km)')
    ax.set_ylim(0,14)
plt.suptitle("Cloud and precip subcolumns", fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.95])
# plt.savefig(path+"subgrid_mr.png",dpi=600)
plt.show()










## investigate extreme values with the nex precip scheme



plt.figure('test',figsize=(18,8))

plt.subplot(311)
plt.pcolormesh(np.arange(0,len(z[0,:]),1),z[::-1,t],Cosp_in.variables["tca"][::-1,:],)
plt.ylim(0,14)

plt.subplot(312)
plt.pcolormesh(np.arange(0,len(z[0,:]),1),z[::-1,t],Cosp_in.variables["fl_lssnow"][::-1,:]*1000,vmax=1,cmap='jet')
plt.ylim(0,14)


plt.subplot(313)
plt.pcolormesh(np.arange(0,len(z[0,:]),1),z[::-1,t],np.sum(I_LSSNOW,1)*1000/100,vmax=1,cmap='jet')
plt.ylim(0,14)
plt.show()




#
#
# pfrac_test=[0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.334711879,0.355284542,0.357359231,0.358069956,0.357114583,0.355228513,0.353848785,0.352313101,0.317387968,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.880891204,0.899871647,0.899847448,0.772919655,0.760382414,0.884870231,0.780659139,0.300000012,0.775534272,0.351571470,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012,0.300000012]
#
#
#
#
#
# plt.figure('precip fraction profile',figsize=(4,5))
# plt.xlabel('Precipitation fraction in gridbox')
# plt.plot(pfrac_test,z)
# plt.ylabel('Altitude (km)')
# plt.ylim(0,14)
# plt.xlim(0,1)
# plt.tight_layout()
# plt.savefig(path+"Precip_fraction_test_profiles.png",dpi=600)

## Full read of subcols


