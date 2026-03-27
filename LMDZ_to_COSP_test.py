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

## Path and data input
import csv
plt.rcParams['font.size'] = 13

nc_file = '/home/grzegorc/AWACA/LMDZ/OUT_golden_case_v8/TEST-amip-ERA5-LAM.01_20250212_20250218_INS_histinsD17.nc'

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

i_sel=1500
pres=nc_data.variables["pres"][:].reshape(npoint,npres)
pres=pres.T
pres=pres[:,i_sel]

# Input variables needed for cosp
var_list=["lon","lat","oliq","oice","zfull","zhalf","temp","rhl","rneb",'pfraclr','pfracld','pr_lsc_i','pr_lsc_l','ref_liq','ref_ice',"ovap","tke","tke_dissip","vitw","vitu","vitv",'time_counter'] #don't forget pres

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


npoint = 1

lon=lon[i_sel]
lat=lat[i_sel]
oliq=oliq[:,i_sel]
oice=oice[:,i_sel]
zfull=zfull[:,i_sel]
zhalf=zhalf[:,i_sel]
temp=temp[:,i_sel]
rhl=rhl[:,i_sel]
rneb=rneb[:,i_sel]
pfraclr=pfraclr[:,i_sel]
pfracld=pfracld[:,i_sel]
pr_lsc_i=pr_lsc_i[:,i_sel]
pr_lsc_l=pr_lsc_l[:,i_sel]
ref_liq=ref_liq[:,i_sel]
ref_ice=ref_ice[:,i_sel]
ovap=ovap[:,i_sel]
tke=tke[:,i_sel]
tke_dissip=tke_dissip[:,i_sel]
vitw=vitw[:,i_sel]
vitu=vitu[:,i_sel]
vitv=vitv[:,i_sel]
time_counter=time_counter[i_sel]


sigma1=0.15
sigma2=2.
zmin_i=2
zmax_i=7.25
Frac_i_prof=0.405*(np.tanh((zfull/1000-zmin_i)/sigma1)-np.tanh((zfull/1000-zmax_i)/sigma2))-0.001



sigma1=0.4


zmin_s=1.5
zmax_s=7.25
Frac_s_tot_prof=0.405*(np.tanh((zfull/1000-zmin_s)/sigma1)-np.tanh((zfull/1000-zmax_s)/sigma2))-0.001


Frac_i_prof=Frac_i_prof/np.max(Frac_i_prof)*1
Frac_s_tot_prof=Frac_s_tot_prof/np.max(Frac_s_tot_prof)*1

Frac_i_prof[Frac_i_prof<0]=0.
Frac_s_tot_prof[Frac_s_tot_prof<0]=0.






sigma1=0.2
sigma2=1.7


Qi_prof=0.23*(np.tanh((zfull/1000-zmin_i)/sigma1)-np.tanh((zfull/1000-zmax_i)/sigma2))

zmin_s=-1
zmax_s=4
sigma3=1
sigma4=2.8

Qs_prof=0.07*(np.tanh((zfull/1000+zmin_s)/sigma3)-np.tanh((zfull/1000-zmax_s)/sigma4))-0.01



Qi_prof[Qi_prof<0]=0.
Qs_prof[Qs_prof<0]=0.

Qi_prof_mesh=Qi_prof*Frac_i_prof
Qs_prof_mesh=Qs_prof*Frac_s_tot_prof

# Frac_i_prof[:]=1

plt.figure('Cloud content')
plt.plot(Qi_prof,zfull/1000-np.min(zfull)/1000,linestyle='--')
plt.plot(Qs_prof,zfull/1000-np.min(zfull)/1000,linestyle='--')
#
# plt.plot(Qi_prof_mesh,zfull/1000-np.min(zfull)/1000,linestyle='--')
# plt.plot(Qs_prof_mesh,zfull/1000-np.min(zfull)/1000,linestyle='--')
# #

plt.xlabel('Mixing ratio (g kg$^{-1}$)')
plt.ylabel('Altitude (km)')
plt.ylim(0,12)
plt.xlim(0,1)
plt.show()



rho=pres/(287*temp)

pflux_s=Qs_prof_mesh*rho
oliq[:]=0.



plt.figure('Cloud fraction',figsize=(9,6))
plt.subplot(121)
plt.plot(Frac_i_prof,zfull/1000-np.min(zfull)/1000,color='k',label='Cloud')
plt.plot(Frac_s_tot_prof,zfull/1000-np.min(zfull)/1000,color='orange',linestyle='--',label='Precipitation')
plt.xlabel('Cloud or precipitation fraction')
plt.ylabel('Altitude (km)')
plt.legend(frameon=False, fontsize=14,loc='upper right')
plt.xlim(0,1)
plt.ylim(0,12)
plt.tight_layout()

plt.subplot(122)
plt.plot(Qi_prof,zfull/1000-np.min(zfull)/1000,color='k',label='q$_{ice}$')
plt.plot(Qs_prof,zfull/1000-np.min(zfull)/1000,color='orange',linestyle='--',label='q$_{snow}$')
#
plt.xlabel('In cloud mixing ratio (g kg$^{-1}$)')
plt.ylabel('Altitude (km)')
plt.legend(frameon=False, fontsize=14,loc='upper right')
plt.xlim(0,0.5)
plt.ylim(0,12)
plt.tight_layout()

plt.savefig("/home/grzegorc/AWACA/COSP_PAMTRAdev/Paper/Profiles_cloudfrac_mr.png",dpi=600)
plt.savefig("/home/grzegorc/AWACA/COSP_PAMTRAdev/Paper/Profiles_cloudfrac_mr.eps",dpi=600)

plt.show()

#
# plt.figure('Cloud fraction')
# plt.plot(temp-273.15,zfull/1000)
# plt.ylim(0,10)
# plt.show()




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

create_var("orography", "f4", ("point",),np.zeros(npoint))
create_var("landmask", "f4", ("point",), np.zeros(npoint))

# === 2. PRESSURE AND HEIGHT ===

#intermediate pressure levels
phalf = pres
phalf = np.zeros(pres.shape[0])
phalf[1:npres] = 0.5 * (pres[:-1] + pres[1:])
dp_bottom = pres[1] - pres[2]
phalf[0] = pres[0] + dp_bottom

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
pfraclr[:]=0.
# create_var("tca", "f4", ("level", "point"),Frac_i_prof)
create_var("tca", "f4", ("level", "point"),Frac_i_prof)
create_var("cca", "f4", ("level", "point"),np.zeros(np.shape(rneb))) #convective variable which needs to be set to 0
create_var("precip_frac", "f4", ("level","point"), Frac_s_tot_prof) #in cloud + clear sky precipitation fraction from the new physics
# create_var("precip_frac", "f4", ("level","point"), np.zeros(np.shape(rneb))) #in cloud + clear sky precipitation fraction from the new physics
create_var("precip_fracclr", "f4", ("level","point"), np.zeros(len(Frac_s_tot_prof))) #in cloud + clear sky precipitation fraction from the new physics

# === 4. CLOUD WATER & ICE CONTENTS ===
create_var("mr_lsliq", "f4", ("level", "point"),np.zeros(np.shape(oliq)))
create_var("mr_lsice", "f4", ("level", "point"),Qi_prof_mesh/1000)
create_var("mr_ccliq", "f4", ("level", "point"),np.zeros(np.shape(oliq))) #no convective clouds
create_var("mr_ccice", "f4", ("level", "point"),np.zeros(np.shape(oliq))) #no convective clouds


# === 5. PRECIPITATION FLUXES ===

create_var("fl_lsrain", "f4", ("level", "point"),np.zeros(np.shape(oliq)))
create_var("fl_lssnow", "f4", ("level", "point"),pflux_s/1000)
# create_var("fl_lssnow", "f4", ("level", "point"),np.zeros(np.shape(oliq)))

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
array=np.zeros(np.shape(pr_lsc_l[:]))
array[:]=1e-30
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