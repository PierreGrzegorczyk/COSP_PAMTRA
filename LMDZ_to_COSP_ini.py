from netCDF4 import Dataset
import matplotlib.pylab as plt
import numpy as np
import matplotlib
from mycolorpy import colorlist as mcp
from matplotlib import cm
import matplotlib.colors as colors

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np



# ___________________________________________

## Path and data input
import csv
plt.rcParams['font.size'] = 13

nc_file = '{LMDZ_output1D}'

nc_data = Dataset(nc_file, "r")

print("Shape of input data",np.shape(nc_data.variables["pres"]))

npres = np.shape(nc_data.variables["pres"])[1] #number of vertical presels
npoint = np.shape(nc_data.variables["pres"])[0] #number of points in x (i.e. the time)

print("Test for correct data shape")
try:
    nc_data.variables["pres"][:].reshape(npres,npoint)
except Exception as e:
    print("Problem in your input data shape")
else:
    print("Ok for data shape")

pres=nc_data.variables["pres"][:].reshape(npoint,npres)
pres=pres.T

# Input variables needed for cosp
var_list=["lon","lat","oliq","oice","zfull","zhalf","temp","rhl","rneb",'pfraclr','pfracld','pr_lsc_i','pr_lsc_l','ref_liq','ref_ice',"ovap","tke","vitw",'time_counter'] #don't forget pres



for var in var_list:
    globals()[var]=nc_data.variables[var][:]
    if len(np.shape(globals()[var]))>1:
        globals()[var]=globals()[var].reshape(npoint,npres)
        globals()[var]=globals()[var].T


if len(lon)==1: #fix 1D profile
    lat = np.array(list(nc_data.variables["lat"][:])*npoint)
    lon = np.array(list(nc_data.variables["lon"][:])*npoint)

else: #moving 1D profile (e.g. aircraft)
    lon = nc_data.variables['lon'][:]
    lat = nc_data.variables['lat'][:]


## read variables to check the dataset

# pres = nc_data.variables["pres"][:]
#
# T = nc_data.variables['temp'][:]
# RH=nc_data.variables['rhl'][:]
# p=nc_data.variables['pres'][:]
# z=nc_data.variables['zfull'][:]
# t=nc_data.variables['time_counter'][:]
# zhalf=nc_data.variables['zhalf'][:]
#
# pr_lsc_i=nc_data.variables['pr_lsc_i'][:] #Large scale precipitation snow
# pr_lsc_l=nc_data.variables['pr_lsc_l'][:] #Large scale precipitation rain
#
# ref_liq=nc_data.variables['ref_liq'][:] #Cloud droplet effective radius
# ref_ice=nc_data.variables['ref_ice'][:] #Ice particle effective radius
#
# oliq=nc_data.variables['oliq'][:] #ql
# ocond=nc_data.variables['ocond'][:] #ql+qi
# oice=nc_data.variables['oice'][:] #qi
#
# frac_ls=nc_data.variables['rneb'][:] #cloud fraction
#
# RHL=nc_data.variables['rhl'][:] #RH wrt liq
# RHI=nc_data.variables['rhi'][:] #RH wrt ice
#
# Qv = nc_data.variables['q2m'][:][:,0]
#
# RHl = nc_data.variables['rhl'][:][:,0]
# RHi = nc_data.variables['rhi'][:][:,0]
# RHi = nc_data.variables['rhi'][:][:,0]
#
# pfraclr = nc_data.variables['pfraclr'][:,:,0,0] # Precipitation fraction in clear sky
# pfracld = nc_data.variables['pfracld'][:,:,0,0] # Precipitation fraction in cloudy sky
#
# cmap = plt.get_cmap('jet', 50)
# cmap.set_under('white')
#
#
#
# #Some data have to be set to 0 for input in COSP (could also be chnaged in COSP but require some important changes in COSP code...)
# pr_con_i=np.zeros(np.shape(pr_lsc_i)) #Convective precipitation snow: set to 0
# pr_con_l=np.zeros(np.shape(pr_lsc_l)) #Convective precipitation rain: set to 0


## Create .nc input for COSP
def create_var(name, dtype, dims, data=None):
    v = dst.createVariable(name, dtype, dims)
    if data is not None:
        v[:] = data
    else:
        shape = [dst.dimensions[d].size for d in dims]
        v[:] = np.zeros(shape, dtype=np.float32)
    return v

from netCDF4 import Dataset
import numpy as np


# === OUTPUT FILE ===
outfile = "Cosp_input_from_LMDZ.nc"  # COSP example input file

# === CREATE DESTINATION FILE ===
dst = Dataset(outfile, "w", format="NETCDF3_CLASSIC")
dst.title = "COSP inputs generated from ICOLMDZ"
dst.Conventions = "CF-1.0"
dst.history = "2025-10-23"
dst.description = "LMDZ to COSP"

# === DIMENSIONS ===
dst.createDimension("point", npoint)
dst.createDimension("level", npres)
dst.createDimension("hydro", 9)

# === FUNCTION ===


# === 1. GEOMETRY ===
create_var("time_counter", "f4", ("point",), time_counter)

create_var("lon", "f4", ("point",), lon)
create_var("lat", "f4", ("point",), lat)

create_var("orography", "f4", ("point",),np.zeros(len(lon)))
create_var("landmask", "f4", ("point",), np.zeros(len(lon)))

# === 2. PRESSURE AND HEIGHT ===

#intermediate pressure levels
phalf = pres
phalf = np.zeros((npres, pres.shape[1]))
phalf[1:npres] = 0.5 * (pres[:-1] + pres[1:])
dp_bottom = pres[1, :] - pres[2, :]
phalf[0, :] = pres[0, :] + dp_bottom

create_var("pfull", "f4", ("level", "point"),pres)
create_var("phalf", "f4", ("level", "point"),phalf)

create_var("height", "f4", ("level", "point"),zfull)
create_var("height_half", "f4", ("level", "point"),zhalf)

# === 3. MAIN FIELDS ===

# Temperature
create_var("T_abs", "f4", ("level", "point"),temp)

# Humidity
create_var("qv", "f4", ("level", "point"),ovap)
create_var("rh", "f4", ("level", "point"),rhl)

#tke
create_var("tke", "f4", ("level", "point"),tke)

#vertical wind speed
create_var("vitw", "f4", ("level", "point"),vitw)

# cloud fraction

create_var("tca", "f4", ("level", "point"),rneb)
create_var("cca", "f4", ("level", "point"),np.zeros(np.shape(rneb))) #convective variable which needs to be set to 0
create_var("precip_frac", "f4", ("level","point"), pfraclr+pfracld) #in cloud + clear sky precipitation fraction from the new physics

# === 4. CLOUD WATER & ICE CONTENTS ===

create_var("mr_lsliq", "f4", ("level", "point"),oliq)
create_var("mr_lsice", "f4", ("level", "point"),oice)
create_var("mr_ccliq", "f4", ("level", "point"),np.zeros(np.shape(oliq))) #no convective clouds
create_var("mr_ccice", "f4", ("level", "point"),np.zeros(np.shape(oliq))) #no convective clouds


# === 5. PRECIPITATION FLUXES ===

create_var("fl_lsrain", "f4", ("level", "point"),pr_lsc_l)
create_var("fl_lssnow", "f4", ("level", "point"),pr_lsc_i)

create_var("fl_ccrain", "f4", ("level", "point"),np.zeros(np.shape(pr_lsc_i)))
create_var("fl_ccsnow", "f4", ("level", "point"),np.zeros(np.shape(pr_lsc_i)))
create_var("fl_lsgrpl", "f4", ("level", "point"),np.zeros(np.shape(pr_lsc_i)))


# === SURFACE FIELDS ==> empty
create_var("psfc", "f4", ("point",), np.zeros(npoint))

create_var("skt", "f4", ("point",), np.zeros(npoint))
create_var("sunlit", "f4", ("point",),np.zeros(npoint))

create_var("u_wind", "f4", ("point",),np.zeros(npoint))
create_var("v_wind", "f4", ("point",),np.zeros(npoint))

# === OZONE ==> empty
create_var("mr_ozone", "f4", ("level", "point"),np.zeros(np.shape(pr_lsc_l)))

# === EMISSIVITY ==> empty
create_var("emsfc_lw", "f4", ("point",), np.zeros(npoint))

# === OPTICAL VARIABLES ==> empty
array=np.zeros(np.shape(pr_lsc_l[:,:]))
array[:,:]=1e-30
for v in ["dtau_s", "dtau_c", "dem_s", "dem_c"]:
    create_var(v, "f4", ("level", "point"),array)

# === EFFECTIVE RADIUS ===

  # integer,parameter :: &
  #      I_LSCLIQ = 1, & ! Large-scale (stratiform) liquid
  #      I_LSCICE = 2, & ! Large-scale (stratiform) ice
  #      I_LSRAIN = 3, & ! Large-scale (stratiform) rain
  #      I_LSSNOW = 4, & ! Large-scale (stratiform) snow
  #      I_CVCLIQ = 5, & ! Convective liquid
  #      I_CVCICE = 6, & ! Convective ice
  #      I_CVRAIN = 7, & ! Convective rain
  #      I_CVSNOW = 8, & ! Convective snow
  #      I_LSGRPL = 9    ! Large-scale (stratiform) groupel


array2=np.zeros((9,npres,npoint))
array2[:,:,:]=1e-30
# array2[0,:,:]=ref_liq*1e-6
# array2[1,:,:]=ref_ice*1e-6
# array2[2,:,:]=0.5/1000
# array2[3,:,:]=1/1000

create_var("Reff", "f4", ("hydro", "level", "point"),array2)

# === 12. TIME VARIABLES ==> random values are in input
vars_list = ["year", "month", "day", "hour", "minute", "second", "t", "tUM", "lst"]
for name in vars_list:
    var = create_var(name, "f4", ("point",))

    if name == "year":
        var[:] = np.full(npoint, 2025, dtype=np.float32)

    elif name == "month":
        var[:] = np.full(npoint, 7, dtype=np.float32)

    elif name == "day":
        var[:] = np.full(npoint, 20, dtype=np.float32)

    elif name == "hour":
        var[:] = np.random.randint(0, 24, npoint).astype(np.float32)

    elif name == "minute":
        var[:] = np.random.randint(0, 60, npoint).astype(np.float32)

    elif name == "second":
        var[:] = np.random.randint(0, 60, npoint).astype(np.float32)

    elif name == "t":
        var[:] = 280 + 10*np.random.rand(npoint).astype(np.float32)

    elif name == "tUM":
        var[:] = 280 + 10*np.random.rand(npoint).astype(np.float32)

    elif name == "lst":
        var[:] = (var[:] + np.random.rand(npoint)*0.5) % 24

# === FINALIZE ===
dst.close()
nc_data.close()
print("COSP input file created:", outfile)

#_________reading test__________
newnc = "Cosp_input_from_LMDZ.nc"
newnc = Dataset(newnc, "r")


#
#
# ## just one plot to check the dataset
# plt.figure("water profile",figsize=(10,6))
# cmap='jet'
# vmax=0.3
# vmin=0.001
# plt.subplot(221)
# plt.title('LS liquid')
# plt.pcolormesh(time_counter/60/60,zfull[:,0]/1000,1000*oliq,cmap=cmap,vmax=vmax,vmin=vmin/10)
# plt.xlabel('Time (hours)')
# plt.ylabel('Altitude (km)')
# plt.colorbar(label='Mixing ratio g kg-1')
# plt.ylim(0,10)
#
# plt.subplot(222)
# plt.title('LS ice')
# plt.pcolormesh(time_counter/60/60,zfull[:,0]/1000,1000*oice,cmap=cmap,vmax=vmax,vmin=vmin/10)
# plt.xlabel('Time (hours)')
# plt.ylabel('Altitude (km)')
# plt.colorbar(label='Mixing ratio g kg-1')
# plt.ylim(0,10)
#
# plt.subplot(223)
#
# vmax=0.5*10**-4
# vmin=10**-6
# plt.title('LS rain')
# plt.pcolormesh(time_counter/60/60,zfull[:,0]/1000,pr_lsc_l,cmap=cmap,vmax=vmax,vmin=vmin/100000)
# plt.xlabel('Time (hours)')
# plt.ylabel('Altitude (km)')
# plt.colorbar(label='Precip rate kg m-2 s-1 ?')
#
# plt.ylim(0,10)
#
# plt.subplot(224)
# plt.title('LS snow')
# plt.pcolormesh(time_counter/60/60,zfull[:,0]/1000,pr_lsc_i,cmap=cmap,vmax=vmax,vmin=vmin)
# plt.xlabel('Time (hours)')
# plt.ylabel('Altitude (km)')
# plt.ylim(0,10)
# plt.colorbar(label='Precip rate kg m-2 s-1 ?')
# plt.tight_layout()
# plt.show()
#
# # oldnc = "/home/grzegorc/AWACA/COSP/COSPv2.0/driver/data/inputs/UKMO/cosp_input_um.nc"
# # oldnc = Dataset(oldnc, "r")
#
#
#
# plt.figure("Total precip fraction",figsize=(10,6))
#
# plt.subplot(221)
# plt.title('Precip frac in clear sky')
# plt.pcolormesh(time_counter/60/60,zfull[:,0]/1000,pfraclr)
# plt.xlabel('Time (hours)')
# plt.ylabel('Altitude (km)')
# plt.ylim(0,10)
#
# plt.subplot(222)
# plt.title('Precip frac in cloud')
# plt.xlabel('Time (hours)')
# plt.ylabel('Altitude (km)')
# plt.ylim(0,10)
# plt.pcolormesh(time_counter/60/60,zfull[:,0]/1000,pfracld)
#
# plt.subplot(223)
# plt.title('Total precip frac')
# plt.xlabel('Time (hours)')
# plt.ylabel('Altitude (km)')
# plt.ylim(0,10)
# plt.pcolormesh(time_counter/60/60,zfull[:,0]/1000,pfracld+pfraclr)
#
# plt.subplot(224)
# plt.title('Cloud fraction')
# plt.xlabel('Time (hours)')
# plt.ylabel('Altitude (km)')
# plt.ylim(0,10)
# plt.pcolormesh(time_counter/60/60,zfull[:,0]/1000,rneb)
# plt.tight_layout()
# plt.show()
#
