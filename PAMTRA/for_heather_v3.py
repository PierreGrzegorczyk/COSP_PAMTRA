from __future__ import print_function

import pyPamtra
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd



#_______ssrga scattering

#kappa_beta_gamma_zeta

###Leinonen et al. (2018) 0.2 kg m2
#AR_snow=0.63
#ssrg_coefs = [0.2,7.,3.5,0.03]

#Billault-Roux et al. (2023) from Ori et al. (2020)
AR_snow=0.62
ssrg_coefs = [0.23,2.,2.66,1.]

#Nowell et al. (2013) aggregation model
#AR_snow=0.82
#ssrg_coefs = [0.25,0.21,2.33,0.13]

#Westbrook et al. (2004) aggregation model
#AR_snow=0.83
#ssrg_coefs = [0.09,0.68,2.0,0.23]




spl_beta_agg = np.load('/home/grzegorc/AWACA/ssrga_coeffs/spl_beta_agg.npy',allow_pickle=True)
print(spl_beta_agg)


verbosity = 0

Radar_type_list=["BASTA","MIRA35C","MRR"]
r_snow_list=np.arange(0.0001,0.010,0.0001)

dBZ=np.zeros((len(Radar_type_list),len(r_snow_list)))

#df = pd.read_csv("ssrga_coeffs_simultaneous_"+str(riming_deg)+".csv")
#print(df.head())  # first 5 rows


i=0
for r_snow in r_snow_list:
    j=0
    for Radar_type in Radar_type_list: 
        pam = pyPamtra.pyPamtra()
        Rho_snow = 1.e3 * 0.178 * ( r_snow * 2 * 1000. )**(-0.922)
        Rho_snow=np.min((Rho_snow,97))
        pam.df.addHydrometeor(("snow",AR_snow, -1 ,Rho_snow, -99,-99, np.pi/4, 2. ,  3 ,1,"mono",-99.0, -99.0, -99.0, -99.0,2*r_snow,-99.0,"ss-rayleigh-gans_%.3f_%.3f_%.3f_%.3f"%tuple(ssrg_coefs),'lmdz_snow',0.0))
        pam = pyPamtra.importer.createUsStandardProfile(pam,hgt_lev=np.arange(1000,1300,200))

#______Different radar characteristics______
#MRR PRO
    
        if Radar_type=="MRR":
            freq=24.23 
            v_max=5.85 #vit nyq
            nfft=30#1024#512
            Z_noise=-8.0
            Beam_width=1.5
            time_resolution=1.0

        if Radar_type=='BASTA': #12.5m 
            freq=95.0
            v_max=10.#9.9 #vit nyq
            nfft=512#1024#512
            Z_noise=-30. #depends on the mode: https://sirta.ipsl.polytechnique.fr/documents/JSS2016/posters/JSS2016_PosterS6_Delanoe.pdf
            Beam_width=0.8
            time_resolution=1.0
    
        if Radar_type=='MIRA35C':
            freq=35.1
            v_max=13.29 #vit nyq
            nfft=512
            Z_noise=-48.
            Beam_width=0.52
            time_resolution=3

        vel0 = np.linspace(-v_max,v_max,nfft,endpoint=False)
        dv0 = vel0[1]-vel0[0]

#__________namelist___________

        pam.nmlSet["radar_mode"] = "simple"
        pam.nmlSet['obs_height'] = 0
        pam.nmlSet["passive"] = False
        pam.nmlSet['radar_integration_time']=time_resolution
        pam.nmlSet["radar_fwhr_beamwidth_deg"] = Beam_width #mira beamwidth
        pam.nmlSet['radar_pnoise0'] = Z_noise+10*np.log10(dv0*nfft)
        pam.nmlSet['radar_attenuation']='bottom-up'
        pam.nmlSet["radar_noise_distance_factor"] = -2 #r^k noise increse
        pam.nmlSet["radar_use_hildebrand"] = True
        pam.nmlSet["radar_nfft"]=nfft
        pam.nmlSet["radar_aliasing_nyquist_interv"] = 1 #allow nyquiest folding after 1 interv
        pam.nmlSet['radar_max_v']= v_max
        pam.nmlSet['radar_min_v']= -v_max

        pam.nmlSet["randomseed"] = 10

        pam.set["verbose"] = 0
        pam.set["pyVerbose"] =0

        pam.p["hydro_q"][:] = 0.1*1e-3

        pam.set['verbose'] = verbosity
        pam.set['pyVerbose'] = verbosity
        pam.runPamtra(freq,checkData=False)


        print("r_snow in  mm: ",np.round(r_snow*1e3,1),"  freq",freq,pam.r["Ze"][0][0][0][0][0][0])
        print(i,j)
        dBZ[j,i]=pam.r["Ze"]
    
        j+=1
    i+=1
plt.figure('Ze')
plt.plot(r_snow_list*1000,dBZ[0,:],label="Basta")
plt.plot(r_snow_list*1000,dBZ[1,:],label="Mira")
plt.plot(r_snow_list*1000,dBZ[2,:],label="MRR")
plt.xlabel('Ice particle size [mm]')
plt.ylabel('Ze [dBZ]')
plt.legend()
plt.show()

plt.figure('DFR')
plt.plot(r_snow_list*1000,dBZ[1,:]-dBZ[0,:],label="Z$_{Ka}$-Z$_{W}$ (Mira-Basta)")
plt.plot(r_snow_list*1000,dBZ[2,:]-dBZ[1,:],label="Z$_{K}$-Z$_{Ka}$ (MRR-Mira)")
plt.xlabel('Ice particle size [mm]')
plt.ylabel('DFR [dB]')
plt.xlim(r_snow_list[0]*1000,r_snow_list[-1]*1000)
plt.plot([0,10],[0,0],linestyle="--",alpha=0.5,color='k')
plt.text(8,-5+.2,"Ar = "+str(AR_snow))
plt.text(8,-4+.2,"$\kappa$ = "+str(ssrg_coefs[0]))
plt.text(8,-3+.2,"β = "+str(ssrg_coefs[1]))
plt.text(8,-2+.2,"$\gamma$ = "+str(ssrg_coefs[2]))
plt.text(8,-1+.2,"$\zeta$ = "+str(ssrg_coefs[3]))
plt.ylim(-5,10)
plt.legend()
plt.show()

