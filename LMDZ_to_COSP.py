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


ok_bs=False
ok_poprecip=False
ok_conv=True
# ___________________________________________

## Path and data input
import csv
plt.rcParams['font.size'] = 13

nc_file = '/home/grzegorc/AWACA/COSP_PAMTRAdev/Bench_conv.nc'

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
var_list=["lon","lat","oliq","oice","zfull","zhalf","temp","rhl","rneb",'pr_lsc_i','pr_lsc_l','ref_liq','ref_ice',"ovap","tke","tke_dissip","vitw","vitu","vitv",'time_counter'] #don't forget pres


if ok_bs==True:
    var_list.append('qbs')

if ok_poprecip==True:
    var_list.append('pfraclr')
    var_list.append('pfracld')

if ok_conv==True:
    var_list.append('rnebcon')
    var_list.append('pr_con_i')
    var_list.append('pr_con_l')
    var_list.append('clwcon')


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
n_hydro=10
# === DIMENSIONS ===
dst.createDimension("point", npoint)
dst.createDimension("level", npres)
dst.createDimension("hydro", n_hydro)

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

#tke
create_var("tke_dissip", "f4", ("level", "point"),tke_dissip)


#vertical wind speed
create_var("vitw", "f4", ("level", "point"),vitw)

#horizontal wind speed
create_var("vitu", "f4", ("level", "point"),vitu)
create_var("vitv", "f4", ("level", "point"),vitv)

# cloud fraction

create_var("tca", "f4", ("level", "point"),rneb)

if ok_poprecip==True:
    create_var("precip_frac", "f4", ("level","point"), pfraclr+pfracld) #in cloud + clear sky precipitation fraction from the new physics
    create_var("precip_fracclr", "f4", ("level","point"), pfraclr) #in cloud + clear sky precipitation fraction from the new physics

# === 4. LS CLOUD WATER & ICE CONTENTS ===

create_var("mr_lsliq", "f4", ("level", "point"),oliq)
create_var("mr_lsice", "f4", ("level", "point"),oice)

if ok_bs==True:
    create_var("mr_bs", "f4", ("level", "point"),qbs)
else:
    create_var("mr_bs", "f4", ("level", "point"),np.zeros(np.shape(oliq)))

# === 5. LS PRECIPITATION FLUXES ===

create_var("fl_lsrain", "f4", ("level", "point"),pr_lsc_l)
create_var("fl_lssnow", "f4", ("level", "point"),pr_lsc_i)


# === 5. CONV CLOUD AND PRECIP ===


if ok_conv==True:
    create_var("fl_ccrain", "f4", ("level", "point"),pr_con_l)
    create_var("fl_ccsnow", "f4", ("level", "point"),pr_con_i)
    create_var("cca", "f4", ("level", "point"),rnebcon) #Convetice cloud fraction

    #Liq and ice fraction from Madeleine et al. (2020) paper about clouds in LMDZ
    Tmin=273.15-30
    Tmax=273.15
    n=0.5

    xliq=((temp-Tmin)/(Tmax-Tmin))**n
    xliq=np.array(xliq,dtype=float)
    xliq[temp<Tmin]=0.
    xliq[temp>Tmax]=1.
    oliq_conv=clwcon*xliq*rnebcon
    oice_conv=clwcon*(1-xliq)*rnebcon

    create_var("mr_ccliq", "f4", ("level", "point"),oliq_conv)
    create_var("mr_ccice", "f4", ("level", "point"),oice_conv)
else:
    create_var("fl_ccrain", "f4", ("level", "point"),np.zeros(np.shape(pr_lsc_i)))
    create_var("fl_ccsnow", "f4", ("level", "point"),np.zeros(np.shape(pr_lsc_i)))
    create_var("cca", "f4", ("level", "point"),np.zeros(np.shape(rneb)))
    create_var("mr_ccliq", "f4", ("level", "point"),np.zeros(np.shape(oliq)))
    create_var("mr_ccice", "f4", ("level", "point"),np.zeros(np.shape(oliq)))



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


array2=np.zeros((n_hydro,npres,npoint))
#array2[:,:,:]=1e-30
array2[0,:,:]=ref_liq*1e-6
array2[1,:,:]=ref_ice*1e-6
array2[2,:,:]=0.5/1000
array2[3,:,:]=1/1000
array2[9,:,:]=50*1e-6#1/1000

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


#______auto input of array length________
npoint = len(lon)

with open("COSP/driver/run/cosp2_input_ini2.txt", "r") as f:
    content = f.read()


content = content.replace("NPOINTS=npoint", f"NPOINTS="+str(npoint))
# Write back
with open("COSP/driver/run/cosp2_input.txt", "w") as f:
    f.write(content)
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
