from __future__ import print_function

import pyPamtra
import shutil
import netCDF4
import matplotlib.pyplot as plt
import numpy as np
import imp
from netCDF4 import Dataset

#________Switch on different options

Radar_type='BASTA'

Run_pamtra=True

Run_parall=True

Run_spectra=True

Write_output=False

#_________LMDZ data___________________
nc_file = '../Cosp_input_from_LMDZ.nc'
nc_data = Dataset(nc_file, "r")

lon = nc_data.variables['lon'][:]
lat = nc_data.variables['lat'][:]
Alt = nc_data.variables['height'][:,0] #if 'Alt' in nc_data.variables else None
T = nc_data.variables['T_abs'][:].T     
RH = nc_data.variables['rh'][:].T
p = nc_data.variables['pfull'][:].T
tke = nc_data.variables['tke'][:].T
w = nc_data.variables['vitw'][:].T
p[p<1.]=1. #minimum value accepted by PAMTRA for the pressure
z = nc_data.variables['height'][:].T
time = nc_data.variables['time_counter'][:]

#_________COSP DATA subcolumns________
path="../COSP/driver/data/my_outputs"
nc_file = path+"/COSP_to_PAMTRA.nc"
nc_data = Dataset(nc_file, "r")

Qi=nc_data['I_LSCICE'][:][::-1,:,:]
Ql=nc_data['I_LSCLIQ'][:][::-1,:,:]
Qr=nc_data['I_LSRAIN'][:][::-1,:,:]
Qs=nc_data['I_LSSNOW'][:][::-1,:,:]

ncol=np.shape(Qs)[1]
ncol=np.shape(Qs)[1]
    
Qi=np.transpose(Qi, (2, 1, 0))
Qs=np.transpose(Qs, (2, 1, 0))
Qr=np.transpose(Qr, (2, 1, 0))
Ql=np.transpose(Ql, (2, 1, 0))

#_________format the shape of data_____

T=np.repeat(T[:, np.newaxis, :], ncol, axis=1)
RH=np.repeat(RH[:, np.newaxis, :], ncol, axis=1)
p=np.repeat(p[:, np.newaxis, :], ncol, axis=1)
z=np.repeat(z[:, np.newaxis, :], ncol, axis=1)
tke=np.repeat(tke[:, np.newaxis, :], ncol, axis=1)
w=np.repeat(w[:, np.newaxis, :], ncol, axis=1)
lon=np.repeat(lon[:, np.newaxis], ncol, axis=1)
lat=np.repeat(lat[:, np.newaxis], ncol, axis=1)

#air density
Rd=287.
Rho_air=p/(Rd*T)

q_hydro=np.zeros(np.shape(T))
q_hydro=np.repeat(q_hydro[:,:,:,np.newaxis],4, axis=3)


#______Definition hydrometeors_____
id_liq=0
id_rain=1
id_snow=2
id_ice=3 

## Define array of q_hydro
q_hydro=np.zeros(np.shape(T))
q_hydro=np.repeat(q_hydro[:,:,:,np.newaxis],4, axis=3)

q_hydro[:,:,:,id_liq]=Ql
q_hydro[:,:,:,id_rain]=Qr
q_hydro[:,:,:,id_snow]=Qs
q_hydro[:,:,:,id_ice]=Qi

#________load PAMTRA______________
imp.reload(pyPamtra)
pam = pyPamtra.pyPamtra()

#_______Create profile_______
pamData = dict()

#Index for data selection
jsel=576
isel=288

#________________Quicklook for data before running__________________
plt.figure('Qs quicklook')
plt.imshow(np.mean(Qs[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1)
plt.colorbar()
print("Show Qs")
plt.show()

plt.figure('Profiles for first time index',figsize=(12,8))
plt.subplot(131)
plt.title('qhydro')
plt.plot(np.sum(q_hydro[isel:jsel,0,:],-1)[0]*1000,z[isel:jsel,0,:][0]/1000)
plt.ylim(0,10)
plt.xlabel('Mixing ratio (g kg^-1)')
plt.ylabel('Altitude (km)')

plt.subplot(132)
plt.title('vertical wind speed')
plt.plot(w[isel:jsel,0,:][0],z[isel:jsel,0,:][0]/1000)
plt.xlabel('w (m s-1)')
plt.ylim(0,10)
plt.ylabel('Altitude (km)')

plt.subplot(133)
plt.title('tke')
plt.plot(tke[isel:jsel,0,:][0],z[isel:jsel,0,:][0]/1000)
plt.ylim(0,10)
plt.xlabel('$e$ $m^2$ $s-2$')
plt.xlim(1e-2,1e2)
plt.xscale('log')
plt.ylabel('Altitude (km)')

# Data input 
pamData["lon"] = lon[isel:jsel,:]
pamData["lat"] = lat[isel:jsel,:]
pamData["temp"] = T[isel:jsel,:,:]
pamData["relhum"] = RH[isel:jsel,:,:]
pamData["hgt"] = z[isel:jsel,:,:]
pamData["press"] = p[isel:jsel,:,:]
pamData["hydro_q"] = q_hydro[isel:jsel,:,:]
pamData["airturb"] = T[isel:jsel,:,:]/T[isel:jsel,:,:]*0.01

#max of tke: to avoid problem with doppler spectra

if Radar_type=='MRR':
    tke[tke>1]=1
else:
    tke[tke>3]=3

#min of tke: to slightly inccrese de width of the spectra and avoid nan for the integration of radar moments
tke[tke<0.01]=0.01

pamData["airturb"] = tke[isel:jsel,:,:]#/T[isel:jsel,:,:]*0.011
print('keys pamdata',pamData.keys())
pamData["wind_w"] =-w[isel:jsel,:,:]#/T[isel:jsel,:,:]*0.1
#pamData["airturb"] = T[isel:jsel,:,:]/T[isel:jsel,:,:]*0.11
#pamData["wind_w"] = T[isel:jsel,:,:]/T[isel:jsel,:,:]*0.001

#_______ssrga scattering

#kappa_beta_gamma_zeta

###Leinonen et al. (2018) 0.2 kg m2
#AR_snow=0.63
#ssrg_coefs = [0.2,7.,3.5,0.03]

#Billault-Roux et al. (2023) from Ori et al. (2020)
#AR_snow=0.82
#ssrg_coefs = [0.23,9.,1.66,1]

#Nowell et al. (2013) aggregation model
AR_snow=0.82
ssrg_coefs = [0.25,0.21,2.33,0.13]

#Westbrook et al. (2004) aggregation model
#AR_snow=0.83
#ssrg_coefs = [0.09,0.68,2.0,0.23]

#________hydrometeor input________
##___Liq_properties

r_liq=12e-6
Rho_liq=1000.
N_liq=(q_hydro[isel:jsel,:,:,id_liq]*Rho_air[isel:jsel,:,:])/(Rho_liq*4/3*np.pi*r_liq**3)
pam.df.addHydrometeor(("liq", 1., 1, Rho_liq, -99., -99., -99., -99. , 3, 1, "mono", -99., -99., -99., -99.,2*r_liq, -99.,"mie-sphere", "khvorostyanov01_drops", 0.))

##___Rain_properties___

r_rain=0.0005
rain_fallspeed=4.
Rho_rain=1000.
N_rain=q_hydro[isel:jsel,:,:,id_rain]/(Rho_rain*4/3*np.pi*r_rain**3)
pam.df.addHydrometeor(("rain",1.,  1 , Rho_rain , -99., -99., -99., -99. , 3, 1, "mono",-99.0, -99.0, -99.0, -99.0,2*r_rain,-99.0,"mie-sphere","lmdz_rain", 0.))

##___Snow_properties___
r_snow=0.001
snow_fallspeed=1.
Rho_snow = 1.e3 * 0.178 * ( r_snow * 2 * 1000. )**(-0.922)
N_snow=(q_hydro[isel:jsel,:,:,id_snow]*Rho_air[isel:jsel,:,:])/(Rho_snow*4/3*np.pi*r_snow**3)

pam.df.addHydrometeor(("snow",AR_snow, -1 , Rho_snow, -99., -99., np.pi/4., 2. ,  3 ,1,"mono",-99.0, -99.0, -99.0, -99.0,2*r_snow,-99.0,"ss-rayleigh-gans_%.3f_%.3f_%.3f_%.3f"%tuple(ssrg_coefs),"lmdz_snow",0.))


#pam.df.addHydrometeor(("snow",AR_snow, -1 , Rho_snow, -99., -99., np.pi/4., 2. ,  3 ,1,"mono",-99.0, -99.0, -99.0, -99.0,2*r_snow,-99.0,"ss-rayleigh-gans_%.3f_%.3f"%tuple(ssrg_coefs),"lmdz_snow",0.0)) #for BR23 only

#pam.df.addHydrometeor(("snow",AR_snow, -1 , Rho_snow, -99., -99., np.pi/4., 2. ,  3 ,1,"mono",-99.0, -99.0, -99.0, -99.0,2*r_snow,-99.0,"ss-rayleigh-gans","lmdz_snow",0.0))

#pam.df.addHydrometeor(("snow",C_snow, -1 , Rho_snow, -99., -99., np.pi/4., 2. ,  3 ,1,"mono",-99.0, -99.0, -99.0, -99.0,2*r_snow,-99.0,"ss-rayleigh-gans","heymsfield10_particles",0.0))
#pam.df.addHydrometeor(("snow",C_snow, -1 , Rho_snow, 130., 3.0 ,0.684, 2. ,  3 ,1,"mono_cosmo_ice",-99.0, -99.0, -99.0, -99.0,2*r_snow,-99.0,"ss-rayleigh-gans","heymsfield10_particles",0.0)) #gives strange things
#pam.df.addHydrometeor(("snow",C_snow, -1 , Rho_snow, 130., 3.0 ,0.684, 2. ,  3 ,1,"mono",-99.0, -99.0, -99.0, -99.0,2*r_snow*1e-3,-99.0,"mie-sphere","heymsfield10_particles",0.0))

print(pam.df)
##___Cirrus_properties___

Rho_ice=917.
AR_ice=1.#
r_ice=50e-6#((q_hydro[isel:jsel,:,:,id_cir]*Rho_air[isel:jsel,:,:])/(N_cir*Rho_cir*4/3*np.pi+1e-30))**(1/3)
N_ice=(q_hydro[isel:jsel,:,:,id_ice]*Rho_air[isel:jsel,:,:])/(Rho_ice*4/3*np.pi*r_ice**3)

#pam.df.addHydrometeor(("ice", C_ice, -1 , Rho_ice,  130., 3.0 ,0.684, 2.  , 3 ,1, "mono_cosmo_ice", -99., -99., -99., -99., 2*r_ice, -99., "ss-rayleigh-gans", "heymsfield10_particles",0.0))
pam.df.addHydrometeor(("ice", AR_ice, -1 , Rho_ice,  -99,-99 ,np.pi/4, 2.  , 3 ,1, "mono", -99., -99., -99., -99., 2*r_ice, -99., "ss-rayleigh-gans", "heymsfield10_particles",0.))
pam.createProfile(**pamData)

#______Different radar characteristics______

#MRR PRO

if Radar_type=="MRR":
    freq=24.23 
    v_max=5.85 #vit nyq
    nfft=30#1024#512
    Z_sensi=-8.0
    Beam_width=1.5
    time_resolution=1.0

if Radar_type=='BASTA':
    freq=95.0
    v_max=9.9 #vit nyq
    nfft=512#1024#512
    Z_sensi=-50. #depends on the mode: https://sirta.ipsl.polytechnique.fr/documents/JSS2016/posters/JSS2016_PosterS6_Delanoe.pdf
    Beam_width=0.8
    time_resolution=1.0

if Radar_type=='MIRA35C':
    freq=35.1
    v_max=13.29 #vit nyq
    nfft=512
    Z_sensi=-60.3
    Beam_width=0.52
    time_resolution=1

if Radar_type=='WPROF':
    freq=94.0
    v_max=7.2 #vit nyq: chnage depending on the altitude ! 
    nfft=512#1024#512
    Z_sensi=-50
    Beam_width=0.48
    time_resolution=0.1

if Radar_type=='STXPOL':
    freq=9.335
    v_max=8.45 #vit nyq: chnage depending on the altitude ! 
    nfft=256#1024#512
    Z_sensi=-50
    Beam_width=1.3
    time_resolution=0.1


#__________namelist___________

Z_noise=Z_sensi+3 #at least 3dB in SNR
pam.nmlSet['obs_height'] = 0
pam.nmlSet["passive"] = False
pam.nmlSet['radar_integration_time']=time_resolution
pam.nmlSet["radar_fwhr_beamwidth_deg"] = Beam_width #mira beamwidth
pam.nmlSet['radar_pnoise0'] = Z_noise 

pam.nmlSet["radar_noise_distance_factor"] = -2 #r^k noise increse

#pam.nmlSet['radar_polarisation']='HH'
pam.nmlSet["randomseed"] = 10
#pam.nmlSet['radar_allow_negative_dD_dU'] = True

#For doppler
if Run_spectra==True:
    pam.nmlSet['radar_airmotion']=True
    pam.nmlSet["radar_mode"] = "spectrum"
    pam.nmlSet["hydro_adaptive_grid"] = False
    pam.nmlSet["conserve_mass_rescale_dsd"] = False
    pam.nmlSet["radar_use_hildebrand"] = True
    pam.nmlSet["radar_use_wider_peak"]=True
    #pam.nmlSet["radar_peak_snr_definition"]="log"
    pam.nmlSet["radar_nfft"]=nfft
    pam.nmlSet["radar_aliasing_nyquist_interv"] = 1 #allow nyquiest folding after 1 interv
    pam.nmlSet['radar_max_v']= v_max
    pam.nmlSet['radar_min_v']= -v_max

    vel0 = np.linspace(-v_max,v_max,nfft,endpoint=False)
    dv0 = vel0[1]-vel0[0]
    pam.nmlSet['radar_pnoise0'] = Z_noise+10*np.log10(dv0*nfft)


#pam.nmlSet['radar_nPeaks']=1.
#pam.nmlSet['radar_peak_min_bins']=-2.
#pam.nmlSet['radar_pnoise0']= -38.23
#    pam.nmlSet["radar_smooth_spectrum"]=True
#pam.nmlSet["radar_noise_distance_factor"] = 0.#-2
#pam.nmlSet["save_psd"] = True

pam.set["pyVerbose"] = 2

if Run_pamtra==True:
    print("Start to run")

    if Run_parall==True:
        pam.runParallelPamtra(freq,
                      pp_deltaX=6,    # 2 profiles in X per worker
                      pp_deltaY=6,    # 1 profile in Y per worker
                      pp_deltaF=1,    # 1 frequency per worker
                      pp_local_workers="auto")  # detect CPU cores
    else:
        pam.runPamtra(freq,checkData=False)

    print("Run end")
    print("Pam.r keys",pam.r.keys())
    #print('Moments', pam.r['radar_moments'])
    #print('Moments', np.shape(pam.r['radar_moments']))
    print('SNR', np.shape(pam.r['radar_snr']),pam.r['radar_snr'])
    #print('radarpol', pam.r["radar_pol"])
    #print('radar_n', pam.r["psd_n"])
    #print('radar_area', pam.r["psd_area"])
    #print('radar_d', pam.r["psd_d"])
    #print('radar_vel', pam.r["radar_vel"],np.shape(pam.r["radar_vel"][0]),len(pam.r["radar_vel"][0]))

    plt.figure('Snr in subcol 0')
    plt.imshow(pam.r["radar_snr"][0,:,:,0,0,0].T,vmin=-30,vmax=80,cmap="jet")
    plt.colorbar()


    print("SHAPE",np.shape(pam.r["Ze"]))
    print("MAX dBZ",np.max(pam.r["Ze"]))

    plt.figure('Quicklook reflectivity in subcol 0')
    plt.pcolormesh(time[isel:jsel],Alt/1000,pam.r["Ze"][:,0,:,0,0,0].T,vmin=-30,vmax=30,cmap="jet")
    plt.ylim(0,12)
    plt.colorbar()

    plt.figure('Quicklook max reflectivity')
    plt.pcolormesh(time[isel:jsel],Alt/1000,np.max(pam.r["Ze"][:,:,:,0,0,0].T,1),vmin=-30,vmax=30,cmap="jet")
    plt.ylim(0,12)
    plt.colorbar()


    plt.figure('First time index reflectivity profile')
    plt.plot(pam.r["Ze"][0,0,:,0,0,0],Alt/1000)
    plt.ylabel('Altitude (km)')
    plt.xlabel('Reflectivity (dBZ)')
    plt.xlim(-30,30) 
    plt.ylim(0,12)

    if Run_spectra==True:
        print('Shape Spectra',np.shape(pam.r["radar_vel"]),np.shape(pam.r["radar_spectra"]))

        plt.figure('Radar moments',figsize=(8,8))

        plt.subplot(221)
        plt.plot(pam.r["radar_moments"][0,0,:,0,0,0,0],Alt/1000)
        plt.xlabel('MDV (m s-1)')
        plt.ylabel('Altitude (km)')
        plt.xlim(-2,2)
        plt.ylim(0,10)

        plt.subplot(222)
        plt.plot(pam.r["radar_moments"][0,0,:,0,0,0,1],Alt/1000)
        plt.xlabel('$\sigma$ (m s-1)')
        plt.ylabel('Altitude (km)')
        plt.xlim(0,3)
        plt.ylim(0,10)

        plt.subplot(223)
        plt.plot(pam.r["radar_moments"][0,0,:,0,0,0,2],Alt/1000)
        plt.xlabel('Skewness')
        plt.ylabel('Altitude (km)')
        plt.xlim(-1,1)
        plt.ylim(0,10)

        plt.subplot(224)
        plt.plot(pam.r["radar_moments"][0,0,:,0,0,0,3],Alt/1000)
        plt.xlabel('Kurtosis')
        plt.ylabel('Altitude (km)')
        plt.xlim(-3,3)
        plt.ylim(0,10)



        plt.figure('Quicklook doppler spectra subcol 1')
        plt.pcolormesh(pam.r["radar_vel"][:],Alt/1000,pam.r["radar_spectra"][0,0,:,0,0,:],vmin=-70,vmax=-30,cmap="plasma")
        plt.ylim(0,10)
        plt.colorbar()



        plt.figure('Quicklook doppler spectra all subcol')
        plt.pcolormesh(pam.r["radar_vel"][:],Alt/1000,np.max(pam.r["radar_spectra"][0,:,:,0,0,:],0),vmin=-70,vmax=-30,cmap="plasma")
        plt.ylim(0,10)
        plt.colorbar()
    plt.show()


# Output NetCDF file path
#output_file = "../Ouput_golden_case_D17_v6_ssrga_spectra_Ka.nc"
output_file = "../MIRA_D17.nc"#../Ouput_golden_case_D17_v6_ssrga_spectra_Ka.nc"

if Write_output==True:
    with Dataset(output_file, "w", format="NETCDF4") as nc_out:

    # Dimensions
        nc_out.createDimension("time", len(time[isel:jsel]))
        nc_out.createDimension("col", ncol)
        nc_out.createDimension("level", T.shape[2])
        nc_out.createDimension("hydro", 4)
        nc_out.createDimension("bins", len(pam.r["radar_vel"][0]))

    # Variables simples
        nc_out.createVariable("time", "f8", ("time",))[:] = time[isel:jsel]
        nc_out.createVariable("col", "i4", ("col",))[:] = np.arange(ncol)
        nc_out.createVariable("level", "i4", ("level",))[:] = Alt
        nc_out.createVariable("hydro", "i4", ("hydro",))[:] = np.arange(4)
        nc_out.createVariable("bins", "i4", ("bins",))[:] = pam.r["radar_vel"][0]
    # Écriture des champs
        nc_out.createVariable("lon", "f4", ("time", "col"))[:] = pamData["lon"]
        nc_out.createVariable("lat", "f4", ("time", "col"))[:] = pamData["lat"]
        nc_out.createVariable("temp", "f4", ("time", "col", "level"))[:] = pamData["temp"]
        nc_out.createVariable("relhum", "f4", ("time", "col", "level"))[:] = pamData["relhum"]
        nc_out.createVariable("hgt", "f4", ("time", "col", "level"))[:] = pamData["hgt"]
        nc_out.createVariable("press", "f4", ("time", "col", "level"))[:] = pamData["press"]
        nc_out.createVariable("hydro_q", "f4", ("time", "col", "level", "hydro"))[:] = pamData["hydro_q"]
        nc_out.createVariable("N_ice", "f4", ("time", "col", "level"))[:] = N_ice
        nc_out.createVariable("N_liq", "f4", ("time", "col", "level"))[:] = N_liq
        nc_out.createVariable("N_snow", "f4", ("time", "col", "level"))[:] = N_snow
        nc_out.createVariable("N_rain", "f4", ("time", "col", "level"))[:] = N_rain
        nc_out.createVariable("Ze", "f4", ("time", "col", "level"))[:] = pam.r["Ze"][:,:,:,0,0,0]

        if Run_spectra==True: # only for spectra radar_mode
            nc_out.createVariable("MDV", "f4", ("time", "col", "level"))[:] = pam.r["radar_moments"][:,:,:,0,0,0,0]
            nc_out.createVariable("Sigma", "f4", ("time", "col", "level"))[:] = pam.r["radar_moments"][:,:,:,0,0,0,1]
            nc_out.createVariable("Skewness", "f4", ("time", "col", "level"))[:] = pam.r["radar_moments"][:,:,:,0,0,0,2]
            nc_out.createVariable("Kurtosis", "f4", ("time", "col", "level"))[:] = pam.r["radar_moments"][:,:,:,0,0,0,3]
            nc_out.createVariable("Spectra", "f4", ("time", "col", "level","bins"))[:] = pam.r["radar_spectra"][:,:,:,0,0,:]
        print("PAMTRA output saved as NetCDF file  ",output_file)
