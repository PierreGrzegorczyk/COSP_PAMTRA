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

Run_spectra=False

Write_output=True

ok_bs=False

Scattering='Ori2021_mix_column_dendrites'
#_________LMDZ data___________________
nc_file = '../Cosp_input_from_LMDZ.nc'
nc_data = Dataset(nc_file, "r")

lon = nc_data.variables['lon'][:]
lat = nc_data.variables['lat'][:]
Alt = nc_data.variables['height'][:,0] #if 'Alt' in nc_data.variables else None
T = nc_data.variables['T_abs'][:].T     
RH = nc_data.variables['rh'][:].T
p = nc_data.variables['pfull'][:].T
tke_dissip = nc_data.variables['tke_dissip'][:].T
w = nc_data.variables['vitw'][:].T
u = nc_data.variables['vitu'][:].T
v = nc_data.variables['vitv'][:].T
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
Qbs=nc_data['I_BS'][:][::-1,:,:]

Qi_cv=nc_data['I_CVCICE'][:][::-1,:,:]
Ql_cv=nc_data['I_CVCLIQ'][:][::-1,:,:]
Qr_cv=nc_data['I_CVRAIN'][:][::-1,:,:]
Qs_cv=nc_data['I_CVSNOW'][:][::-1,:,:]


ncol=np.shape(Qs)[1]
    
Qi=np.transpose(Qi, (2, 1, 0))
Qs=np.transpose(Qs, (2, 1, 0))
Qbs=np.transpose(Qbs, (2, 1, 0))
Qr=np.transpose(Qr, (2, 1, 0))
Ql=np.transpose(Ql, (2, 1, 0))

Qi_cv=np.transpose(Qi_cv, (2, 1, 0))
Qs_cv=np.transpose(Qs_cv, (2, 1, 0))
Ql_cv=np.transpose(Ql_cv, (2, 1, 0))
Qr_cv=np.transpose(Qr_cv, (2, 1, 0))

Qi+=Qi_cv
Ql+=Ql_cv
Qr+=Qr_cv
Qs+=Qs_cv

#_________format the shape of data_____

T=np.repeat(T[:, np.newaxis, :], ncol, axis=1)
RH=np.repeat(RH[:, np.newaxis, :], ncol, axis=1)
p=np.repeat(p[:, np.newaxis, :], ncol, axis=1)
z=np.repeat(z[:, np.newaxis, :], ncol, axis=1)
tke_dissip=np.repeat(tke_dissip[:, np.newaxis, :], ncol, axis=1)
w=np.repeat(w[:, np.newaxis, :], ncol, axis=1)
u=np.repeat(u[:, np.newaxis, :], ncol, axis=1)
v=np.repeat(v[:, np.newaxis, :], ncol, axis=1)
lon=np.repeat(lon[:, np.newaxis], ncol, axis=1)
lat=np.repeat(lat[:, np.newaxis], ncol, axis=1)

#air density
Rd=287.
Rho_air=p/(Rd*T)
w=w/Rho_air/9.81

#______Definition hydrometeors_____
id_liq=0
id_rain=1
id_snow=2
id_bs=3

## Define bins ofr the ice particles

Nbin_ice=12
r_ice_max=160

D_ice_bins_bounds=np.linspace(0,r_ice_max,Nbin_ice+1)
dD_ice=D_ice_bins_bounds[1]-D_ice_bins_bounds[0]
D_ice_bins_center=np.linspace(dD_ice/2,r_ice_max-dD_ice/2,Nbin_ice)

## Define array of q_hydro
q_hydro=np.zeros(np.shape(T))
q_hydro=np.repeat(q_hydro[:,:,:,np.newaxis],4+Nbin_ice, axis=3)

q_hydro[:,:,:,id_liq]=Ql
q_hydro[:,:,:,id_rain]=Qr
q_hydro[:,:,:,id_snow]=Qs
q_hydro[:,:,:,id_bs]=Qbs

#________load PAMTRA______________
imp.reload(pyPamtra)
pam = pyPamtra.pyPamtra()

#_______Create profile_______
pamData = dict()

#Index for data selection
end = 'end'
jsel=end
isel=0

if jsel == end:
    jsel = len(time) 
#________________Quicklook for data before running__________________

plt.figure('Input mixing ratios',figsize=(14,6))
plt.subplot(221)
plt.title('a) Q ice',loc='left')
plt.imshow(np.mean(Qi[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1000*np.nanmax(Qi[isel:jsel,:,::-1]),interpolation='none')
plt.colorbar()

plt.subplot(222)
plt.title('b) Q liquid',loc='left')
plt.imshow(np.mean(Ql[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1000*np.nanmax(Ql[isel:jsel,:,::-1]),interpolation='none')
plt.colorbar()

plt.subplot(223)
plt.title('c) Q Snow',loc='left')
plt.imshow(np.mean(Qs[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1000*np.nanmax(Qs[isel:jsel,:,::-1]),interpolation='none')
plt.colorbar()

plt.subplot(224)
plt.title('d) Q rain',loc='left')
plt.imshow(np.mean(Qr[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1000*np.nanmax(Qr[isel:jsel,:,::-1]),interpolation='none')
plt.colorbar()
plt.tight_layout()


if True==True:
    plt.figure('Input convective mixing ratios',figsize=(14,6))
    plt.subplot(221)
    plt.title('a) Q ice',loc='left')
    plt.imshow(np.mean(Qi_cv[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1000*np.nanmax(Qi_cv[isel:jsel,:,::-1]),interpolation='none')
    plt.colorbar()

    plt.subplot(222)
    plt.title('b) Q liquid',loc='left')
    plt.imshow(np.mean(Ql_cv[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1000*np.nanmax(Ql_cv[isel:jsel,:,::-1]),interpolation='none')
    plt.colorbar()

    plt.subplot(223)
    plt.title('c) Q Snow',loc='left')
    plt.imshow(np.mean(Qs_cv[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1000*np.nanmax(Qs_cv[isel:jsel,:,::-1]),interpolation='none')
    plt.colorbar()

    plt.subplot(224)
    plt.title('d) Q conv rain',loc='left')
    plt.imshow(np.mean(Qr_cv[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1000*np.nanmax(Qr_cv[isel:jsel,:,::-1]),interpolation='none')
    plt.colorbar()
    plt.tight_layout()

if False==True:
    plt.figure('Blowing snow',figsize=(6.5,3))
    plt.title('Q blowing snow',loc='left')
    plt.imshow(np.mean(Qbs[isel:jsel,:,::-1],1).T*1000,aspect='auto',cmap="jet",vmin=0.01,vmax=1000*np.nanmax(Qbs[isel:jsel,:,::-1]),interpolation='none')
    plt.colorbar()
    plt.tight_layout()



print("Show Mixing ratios")
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
plt.title('tke_dissip')
plt.plot(tke_dissip[isel:jsel,0,:][0],z[isel:jsel,0,:][0]/1000)
plt.ylim(0,10)
plt.xlabel('$\epsilon$ $m^2$ $s-2$')
plt.xlim(1e-2,1e2)
plt.xscale('log')
plt.ylabel('Altitude (km)')

## Add convetive content to large scale content




#_______ssrga scattering parameters (see the table of Billault-Roux and Berne 2025)
#kappa_beta_gamma_zeta

AR_snow=0.65

if Scattering=='Ori2021_mix_column_dendrites':
    ssrg_coefs = [0.22,2.52,2.36,0.049]

if Scattering=='Ori2021_rimed_aggregate_dendrites':
    ssrg_coefs = [0.15,4.98,3.53,0.036]

if Scattering=='Hogan2017_v1_aggregate_bullet_rosettes':
#    AR_snow=0.82
    ssrg_coefs = [0.09,0.15,2.33,0.22]

if Scattering=='Hogan2017_v2_aggregate_bullet_rosettes':
#AR_snow=0.82
    ssrg_coefs = [0.16,0.15,2.33,0.22]

#________hydrometeor input________
##___Liq_properties

r_liq=12e-6
Rho_liq=1000.
N_liq=(q_hydro[isel:jsel,:,:,id_liq]*Rho_air[isel:jsel,:,:])/(Rho_liq*4/3*np.pi*r_liq**3)
pam.df.addHydrometeor(("liq", 1., 1, Rho_liq, -99., -99., -99., -99. , 3, 1, "mono", -99., -99., -99., -99.,2*r_liq, -99.,"mie-sphere", "khvorostyanov01_drops", 0.))

##___Rain_properties___

r_rain=0.0005
Rho_rain=1000.
N_rain=q_hydro[isel:jsel,:,:,id_rain]/(Rho_rain*4/3*np.pi*r_rain**3)
pam.df.addHydrometeor(("rain",1.,  1 , Rho_rain , -99., -99., -99., -99. , 3, 1, "mono",-99.0, -99.0, -99.0, -99.0,2*r_rain,-99.0,"mie-sphere","lmdz_rain", 0.))
#pam.df.addHydrometeor(("rain",1.,  1 , Rho_rain , -99., -99., -99., -99. , 3, 1, "mono",-99.0, -99.0, -99.0, -99.0,2*r_rain,-99.0,"khvorostyanov01_drops","lmdz_rain", 0.))

##___Snow_properties___
r_snow=0.001
Rho_snow = 1.e3 * 0.178 * ( r_snow * 2 * 1000. )**(-0.922)
N_snow=(q_hydro[isel:jsel,:,:,id_snow]*Rho_air[isel:jsel,:,:])/(Rho_snow*4/3*np.pi*r_snow**3)

#pam.df.addHydrometeor(("snow",AR_snow, -1 , Rho_snow, -99., -99., np.pi/4., 2. ,  3 ,1,"mono",-99.0, -99.0, -99.0, -99.0,2*r_snow,-99.0,"mie-sphere","lmdz_snow",0.))
pam.df.addHydrometeor(("snow",AR_snow, -1 , Rho_snow, -99., -99., np.pi/4., 2. ,  3 ,1,"mono",-99.0, -99.0, -99.0, -99.0,2*r_snow,-99.0,"ss-rayleigh-gans_%.3f_%.3f_%.3f_%.3f"%tuple(ssrg_coefs),"lmdz_snow",0.))


##___Blowing_snow_properties___
r_bs=50e-6
AR_bs=1.
Rho_bs = 917.
N_bs=(q_hydro[isel:jsel,:,:,id_bs]*Rho_air[isel:jsel,:,:])/(Rho_snow*4/3*np.pi*r_snow**3)

pam.df.addHydrometeor(("bs",AR_bs, -1 , Rho_bs, -99., -99., np.pi/4., 2. ,  3 ,1,"mono",-99.0, -99.0, -99.0, -99.0,2*r_bs,-99.0,"ss-rayleigh-gans_%.3f_%.3f_%.3f_%.3f"%tuple(ssrg_coefs),"lmdz_bs",0.))

print("pam.df",pam.df)
##___Ice_properties___
Rho_ice=917.
AR_ice=1.#
r_ice=1e-6*(45.8966*(Qi*Rho_air*1e3)**0.2214 + 0.7957*(Qi*Rho_air*1e3)**0.2535*(T - 273.15 + 190.))/2 #as in lmdz physics from Sun and Rikus 1999
N_ice=(Qi[isel:jsel,:,:]*Rho_air[isel:jsel,:,:])/(Rho_ice*4/3*np.pi*r_ice[isel:jsel,:,:]**3)


for i in range(len(D_ice_bins_center)):
    Qi_tmp=Qi.copy()

    mask=np.logical_and(2*r_ice*1e6<=D_ice_bins_bounds[i+1],2*r_ice*1e6>D_ice_bins_bounds[i])
    Qi_tmp[mask==False]=0.

    id_ice=i+4
    q_hydro[:,:,:,id_ice]=Qi_tmp

    #pam.df.addHydrometeor(("ic"+str(i), AR_ice, -1 , Rho_ice,  -99,-99 ,np.pi/4, 2.  , 3 ,1, "mono", -99., -99., -99., -99., D_ice_bins_center[i]*1e-6, -99., "ss-rayleigh-gans_%.3f_%.3f_%.3f_%.3f"%tuple(ssrg_coefs), "heymsfield10_particles",0.))
    pam.df.addHydrometeor(("ic"+str(D_ice_bins_center[i]), AR_ice, -1 , Rho_ice,  -99,-99 ,np.pi/4, 2.  , 3 ,1, "mono", -99., -99., -99., -99., D_ice_bins_center[i]*1e-6, -99., "mie-sphere", "heymsfield10_particles",0.))
# Data input
pamData["lon"] = lon[isel:jsel,:]
pamData["lat"] = lat[isel:jsel,:]
pamData["temp"] = T[isel:jsel,:,:]
pamData["relhum"] = RH[isel:jsel,:,:]
pamData["hgt"] = z[isel:jsel,:,:]
pamData["press"] = p[isel:jsel,:,:]
pamData["hydro_q"] = q_hydro[isel:jsel,:,:]
pamData["turb_edr"]=tke_dissip[isel:jsel,:,:]#/T[isel:jsel,:,:]
pamData["wind_w"] =-w[isel:jsel,:,:]#/T[isel:jsel,:,:]*0.1
pamData["wind_uv"] = (u[isel:jsel,:,:]**2+v[isel:jsel,:,:]**2)**0.5#/T[isel:jsel,:,:]*0.1

pam.createProfile(**pamData)

#______Different radar characteristics______

#MRR PRO

if Radar_type=="MRR":
    freq=24.23 
    v_max=5.85 #vit nyq
    nfft=30#1024#512
    Z_noise=12
    Beam_width=1.5
    time_resolution=1.0
    Noise_factor=-2

if Radar_type=='BASTA': #12.5m 
    freq=95.0
    v_max=10.#9.9 #vit nyq
    nfft=512#1024#512
    Z_noise=-30. #depends on the mode: https://sirta.ipsl.polytechnique.fr/documents/JSS2016/posters/JSS2016_PosterS6_Delanoe.pdf
    Beam_width=0.8
    time_resolution=9.0
    Noise_factor=-2

if Radar_type=='MIRA35C':
    freq=35.1
    v_max=13.29 #vit nyq
    nfft=512
    Z_noise=-48.
    Beam_width=0.52
    time_resolution=3
    Noise_factor=-2

if Radar_type=='WPROF':
    freq=94.0
    v_max=7.2 #vit nyq: chnage depending on the altitude ! 
    nfft=512#1024#512
    Z_noise=-50
    Beam_width=0.48
    time_resolution=0.1
    Noise_factor=-2

if Radar_type=='STXPOL':
    freq=9.335
    v_max=8.45 #vit nyq: chnage depending on the altitude ! 
    nfft=256#1024#512
    Z_noise=-50
    Beam_width=1.3
    time_resolution=0.1
    Noise_factor=-2

if Radar_type=='EarthCARE_cpr':  
    freq=94.05
    v_max=10.
    nfft=512
    Z_noise=-300.
    Beam_width=0.095
    time_resolution=0.67
    Noise_factor=-2

if False==True:
    freq=95.0
    v_max=10
    nfft=512
    Z_noise=-200
    Beam_width=0.8
    time_resolution=9
    Noise_factor=-2

#__________namelist___________

if "Ground"=="Ground":
    pam.nmlSet['radar_attenuation']='bottom-up'
    pam.p['obs_height'][:,1] = 0.0

if "Ground"=="Sat":
    pam.nmlSet['radar_attenuation']='top-down'
    pam.p['obs_height'][:,0] = 390000

if "Ground"=="Aircraft":
    nc_aircraft = Dataset("/home/grzegorc/AWACA/LMDZ/OUT_golden_case_v8/Flight_altitude.nc", "r")
    
    if 'up'=='down' or 'up'=='both':
        pam.nmlSet['radar_attenuation']='top-down'
        pam.p['obs_height'][:,:,0] = np.repeat(nc_aircraft['radar_altitude'][:][isel:jsel, np.newaxis], ncol, axis=1)#0.0

    elif 'up'=='up':
        pam.nmlSet['radar_attenuation']='bottom-up'
        pam.p['obs_height'][:,:,1] = np.repeat(nc_aircraft['radar_altitude'][:][isel:jsel, np.newaxis], ncol, axis=1)#0.0

    
    print("pam.p['obs_height']",pam.p['obs_height'][:,:,:])

pam.nmlSet["passive"] = False
pam.nmlSet['radar_integration_time']=time_resolution
pam.nmlSet["radar_fwhr_beamwidth_deg"] = Beam_width #mira beamwidth
#pam.nmlSet['radar_pnoise0'] = Z_noise 
pam.nmlSet["radar_noise_distance_factor"] = Noise_factor 
pam.nmlSet["randomseed"] = 10
pam.nmlSet["radar_use_hildebrand"] = True

#For doppler
if Run_spectra==True:
    pam.nmlSet['radar_airmotion']=True
    pam.nmlSet["radar_mode"] = "spectrum"
    pam.nmlSet["hydro_adaptive_grid"] = False
    pam.nmlSet["conserve_mass_rescale_dsd"] = False
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

pam.set["pyVerbose"] = 1

print("pam nml",pam.nmlSet)
if Run_pamtra==True:
    print("Start to run")

    if Run_parall==True:
        pam.runParallelPamtra(freq,
                      pp_deltaX=3,    # profiles in X per worker
                      pp_deltaY=2,    # profile in Y per worker
                      pp_deltaF=1,    # frequency per worker
                      pp_local_workers="auto")  # detect CPU cores

    else:
        pam.runPamtra(freq,checkData=False)

    print("Run end")
    print("Pam.r keys",pam.r.keys())

    #print('Moments', pam.r['radar_moments'])
    #print('Moments', np.shape(pam.r['radar_moments']))
    #print('SNR', np.shape(pam.r['radar_snr']),pam.r['radar_snr'])
    #print('radarpol', pam.r["radar_pol"])
    #print('radar_n', pam.r["psd_n"])
    #print('radar_area', pam.r["psd_area"])
    #print('radar_d', pam.r["psd_d"])
    #print('radar_vel', pam.r["radar_vel"],np.shape(pam.r["radar_vel"][0]),len(pam.r["radar_vel"][0]))


    plt.figure('Quicklook reflectivity in subcol 0')
    plt.pcolormesh(time[isel:jsel],pam.r["radar_hgt"][0,0,:]/1000,pam.r["Ze"][:,0,:,0,0,0].T,vmin=-30,vmax=30,cmap="jet")
    plt.ylim(0,12)
    plt.colorbar()

    plt.figure('Quicklook max reflectivity')
    plt.pcolormesh(time[isel:jsel],pam.r["radar_hgt"][0,0,:]/1000,np.max(pam.r["Ze"][:,:,:,0,0,0].T,1),vmin=-30,vmax=30,cmap="jet")
    plt.ylim(0,12)
    plt.colorbar()

    plt.figure('First time index reflectivity profile')
    plt.plot(pam.r["Ze"][0,0,:,0,0,0],pam.r["radar_hgt"][0,0,:]/1000)
    plt.ylabel('Altitude (km)')
    plt.xlabel('Reflectivity (dBZ)')
    plt.xlim(-30,30) 
    plt.ylim(0,12)



    if Run_spectra==True:
        #print('Shape Spectra',np.shape(pam.r["radar_vel"]),np.shape(pam.r["radar_spectra"]))
        plt.figure('Snr in subcol 0')
        plt.imshow(pam.r["radar_snr"][0,:,:,0,0,0].T,vmin=-30,vmax=80,cmap="jet")
        plt.colorbar()

        plt.figure('Radar moments',figsize=(8,8))

        plt.subplot(221)
        plt.plot(pam.r["radar_moments"][0,0,:,0,0,0,0],pam.r["radar_hgt"][0,0,:]/1000)
        plt.xlabel('MDV (m s-1)')
        plt.ylabel('Altitude (km)')
        plt.xlim(-2,2)
        plt.ylim(0,10)

        plt.subplot(222)
        plt.plot(pam.r["radar_moments"][0,0,:,0,0,0,1],pam.r["radar_hgt"][0,0,:]/1000)
        plt.xlabel('$\sigma$ (m s-1)')
        plt.ylabel('Altitude (km)')
        plt.xlim(0,3)
        plt.ylim(0,10)

        plt.subplot(223)
        plt.plot(pam.r["radar_moments"][0,0,:,0,0,0,2],pam.r["radar_hgt"][0,0,:]/1000)
        plt.xlabel('Skewness')
        plt.ylabel('Altitude (km)')
        plt.xlim(-1,1)
        plt.ylim(0,10)

        plt.subplot(224)
        plt.plot(pam.r["radar_moments"][0,0,:,0,0,0,3],pam.r["radar_hgt"][0,0,:]/1000)
        plt.xlabel('Kurtosis')
        plt.ylabel('Altitude (km)')
        plt.xlim(-3,3)
        plt.ylim(0,10)



        plt.figure('Quicklook doppler spectra subcol 1')
        plt.pcolormesh(pam.r["radar_vel"][:],pam.r["radar_hgt"][0,0,:]/1000,pam.r["radar_spectra"][0,0,:,0,0,:],vmin=-30,vmax=30,cmap="plasma")
        plt.ylim(0,10)
        plt.colorbar()



        plt.figure('Quicklook doppler spectra all subcol')
        plt.pcolormesh(pam.r["radar_vel"][:],pam.r["radar_hgt"][0,0,:]/1000,np.max(pam.r["radar_spectra"][0,:,:,0,0,:],0),vmin=-30,vmax=30,cmap="plasma")
        plt.ylim(0,10)
        plt.colorbar()
    plt.show()


# Output NetCDF file path
#output_file = "../Ouput_golden_case_D17_v6_ssrga_spectra_Ka.nc"
output_file = "../output/BENCH_exclude_new.nc"#../Ouput_golden_case_D17_v6_ssrga_spectra_Ka.nc"

if Write_output==True and Run_pamtra==True:
    with Dataset(output_file, "w", format="NETCDF4") as nc_out:

    # Dimensions
        nc_out.createDimension("time", len(time[isel:jsel]))
        nc_out.createDimension("col", ncol)
        #nc_out.createDimension("level", len(pam.r["radar_hgt"][0,0,:]))
        nc_out.createDimension("level", T.shape[2])

        if ok_bs==True:
            nc_out.createDimension("hydro", 5)
        else:
            nc_out.createDimension("hydro", 4)
    # Variables simples

        nc_out.createVariable("time", "f8", ("time",))[:] = time[isel:jsel]
        nc_out.createVariable("col", "i4", ("col",))[:] = np.arange(ncol)
        nc_out.createVariable("level", "f4", ("time","level"))[:] = pam.r["radar_hgt"][:,0,:]
        if ok_bs==True:
            nc_out.createVariable("hydro", "i4", ("hydro",))[:] = np.arange(5)

        else:
            nc_out.createVariable("hydro", "i4", ("hydro",))[:] = np.arange(4)


    # Écriture des champs
        nc_out.createVariable("lon", "f4", ("time", "col"))[:] = pamData["lon"]
        nc_out.createVariable("lat", "f4", ("time", "col"))[:] = pamData["lat"]
        nc_out.createVariable("temp", "f4", ("time", "col", "level"))[:] = pamData["temp"]
        nc_out.createVariable("relhum", "f4", ("time", "col", "level"))[:] = pamData["relhum"]
        nc_out.createVariable("hgt", "f4", ("time", "col", "level"))[:] = pamData["hgt"]
        nc_out.createVariable("press", "f4", ("time", "col", "level"))[:] = pamData["press"]

        if ok_bs==True:
            merged_hydro_q=np.zeros(np.shape(pamData["hydro_q"][:,:,:,:5]))
            merged_hydro_q[:,:,:,:4] = pamData["hydro_q"][:,:,:,:4]
            merged_hydro_q[:,:,:,4] = np.sum(pamData["hydro_q"][:,:,:,4:],-1)
        else:
            merged_hydro_q=np.zeros(np.shape(pamData["hydro_q"][:,:,:,:4]))
            merged_hydro_q[:,:,:,:3] = pamData["hydro_q"][:,:,:,:3]
            merged_hydro_q[:,:,:,3] = np.sum(pamData["hydro_q"][:,:,:,3:],-1)

        nc_out.createVariable("hydro_q", "f4", ("time", "col", "level", "hydro"))[:] = merged_hydro_q
        nc_out.createVariable("N_ice", "f4", ("time", "col", "level"))[:] = N_ice
        nc_out.createVariable("N_liq", "f4", ("time", "col", "level"))[:] = N_liq
        nc_out.createVariable("N_snow", "f4", ("time", "col", "level"))[:] = N_snow
        nc_out.createVariable("N_rain", "f4", ("time", "col", "level"))[:] = N_rain
        nc_out.createVariable("Ze", "f4", ("time", "col", "level"))[:] = pam.r["Ze"][:,:,:,0,0,0]

        if Run_spectra==True: # only for spectra radar_mode
            nc_out.createDimension("bins", len(pam.r["radar_vel"][0]))
            nc_out.createVariable("bins", "f4", ("bins",))[:] = pam.r["radar_vel"][0]
            nc_out.createVariable("MDV", "f4", ("time", "col", "level"))[:] = pam.r["radar_moments"][:,:,:,0,0,0,0]
            nc_out.createVariable("Sigma", "f4", ("time", "col", "level"))[:] = pam.r["radar_moments"][:,:,:,0,0,0,1]
            nc_out.createVariable("Skewness", "f4", ("time", "col", "level"))[:] = pam.r["radar_moments"][:,:,:,0,0,0,2]
            nc_out.createVariable("Kurtosis", "f4", ("time", "col", "level"))[:] = pam.r["radar_moments"][:,:,:,0,0,0,3]
            nc_out.createVariable("Spectra", "f4", ("time", "col", "level","bins"))[:] = pam.r["radar_spectra"][:,:,:,0,0,:]
        print("PAMTRA output saved as NetCDF file  ",output_file)

# ##################### 2nd run only for Radar onboard aicraft which is pointing both up and down #################
# upward pointing 

if "Ground"=="Aircraft" and "up"=='both':
    pam.nmlSet['radar_attenuation']='bottom-up'
    pam.p['obs_height'][:,:,0] = np.repeat(nc_aircraft['radar_altitude'][:][isel:jsel, np.newaxis], ncol, axis=1)#0.0
    nc_aircraft.close()
    print("pam 2nd nml",pam.nmlSet)
    if Run_pamtra==True:
        print("Start to run")

        if Run_parall==True:
            pam.runParallelPamtra(freq,
                      pp_deltaX=4,    # profiles in X per worker
                      pp_deltaY=2,    # profile in Y per worker
                      pp_deltaF=1,    # frequency per worker
                      pp_local_workers="auto")  # detect CPU cores

        else:
            pam.runPamtra(freq,checkData=False)

    if Write_output==True:
        with Dataset(output_file[:-3]+"_upward_part.nc", "w", format="NETCDF4") as nc_out:

    # Dimensions
            nc_out.createDimension("time", len(time[isel:jsel]))
            nc_out.createDimension("col", ncol)
            nc_out.createDimension("level", T.shape[2])
            if ok_bs==True:
                nc_out.createDimension("hydro", 5)
            else:
                nc_out.createDimension("hydro", 4)

            nc_out.createDimension("bins", len(pam.r["radar_vel"][0]))

    # Variables simples
            nc_out.createVariable("time", "f8", ("time",))[:] = time[isel:jsel]
            nc_out.createVariable("col", "i4", ("col",))[:] = np.arange(ncol)
            nc_out.createVariable("level", "f4", ("time","level"))[:] = pam.r["radar_hgt"][:,0,:]
            if ok_bs==True:
                nc_out.createVariable("hydro", "i4", ("hydro",))[:] = np.arange(5)
            else:
                nc_out.createVariable("hydro", "i4", ("hydro",))[:] = np.arange(4)

            nc_out.createVariable("bins", "f4", ("bins",))[:] = pam.r["radar_vel"][0]
    # Écriture des champs
            nc_out.createVariable("lon", "f4", ("time", "col"))[:] = pamData["lon"]
            nc_out.createVariable("lat", "f4", ("time", "col"))[:] = pamData["lat"]
            nc_out.createVariable("temp", "f4", ("time", "col", "level"))[:] = pamData["temp"]
            nc_out.createVariable("relhum", "f4", ("time", "col", "level"))[:] = pamData["relhum"]
            nc_out.createVariable("hgt", "f4", ("time", "col", "level"))[:] = pamData["hgt"]
            nc_out.createVariable("press", "f4", ("time", "col", "level"))[:] = pamData["press"]

            if ok_bs==True:
                merged_hydro_q=np.zeros(np.shape(pamData["hydro_q"][:,:,:,:5]))
                merged_hydro_q[:,:,:,:4] = pamData["hydro_q"][:,:,:,:4]
                merged_hydro_q[:,:,:,4] = np.sum(pamData["hydro_q"][:,:,:,4:],-1)
 
            else:
                merged_hydro_q=np.zeros(np.shape(pamData["hydro_q"][:,:,:,:4]))
                merged_hydro_q[:,:,:,:3] = pamData["hydro_q"][:,:,:,:3]
                merged_hydro_q[:,:,:,3] = np.sum(pamData["hydro_q"][:,:,:,3:],-1)

            nc_out.createVariable("hydro_q", "f4", ("time", "col", "level", "hydro"))[:] = merged_hydro_q
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
            print("2nd PAMTRA output saved as NetCDF file",output_file[:-3]+"_upward_part.nc")
