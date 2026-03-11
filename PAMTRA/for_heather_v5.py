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
#ssrg_coefs = [0.23,9.,2.66,1.]

#Nowell et al. (2013) aggregation model
#AR_snow=0.82


#name='Dendrite_aggregate'

#ssrg_coefs = [0.25,0.21,2.33,0.13]

#Westbrook et al. (2004) aggregation model
#AR_snow=0.83
#ssrg_coefs = [0.09,0.68,2.0,0.23]

#Hogan2014
AR_snow=0.62
#name='Aggregate_column_bullet_rosettes_H14_\n'
#ssrg_coefs = [0.19,0.23,1.66,1]

#name='Mix_column_dendrites_O21_\n'
#ssrg_coefs = [0.22,2.52,2.36,0.049]

#name='Aggregate_dendrites_rimed_O21_\n'
#ssrg_coefs = [0.15,4.98,3.53,0.036]

#AR_snow=0.82
#name='Aggregate_bullet_rosettes_H17v1_\n'
#srg_coefs = [0.09,0.86,2.,0.28]

AR_snow=0.82
name='Aggregate_bullet_rosettes_H17v2_\n'
ssrg_coefs = [0.16,0.15,2.33,0.22]


verbosity = 0
Radar_type_list=["BASTA","MIRA35C","MRR"]

alpha_list=np.arange(-0.003,0.01,0.003)
beta_list=np.arange(1.5,2.6,0.1)
# Order: plates, columns, dendrites, aggregates, graupel, cirrus

alpha_list = np.array([0.005, 0.007, 0.004, 0.003, 0.05, 0.0185])

dBZ=np.zeros((len(Radar_type_list),len(alpha_list)))
print('shape', np.shape(dBZ))
#df = pd.read_csv("ssrga_coeffs_simultaneous_"+str(riming_deg)+".csv")
#print(df.head())  # first 5 rows
n_ice=1*1000
q_ice=0.5/1000

i=0
for alpha in alpha_list:
    j=0
    for Radar_type in Radar_type_list:
        pam = pyPamtra.pyPamtra()
                #Rho_snow = 1.e3 * 0.178 * ( r_snow * 2 * 1000. )**(-0.922)
                #pam.df.addHydrometeor(("snow",AR_snow, -1 ,-99,0.0185,1.9, -99,-99 ,13,100,"mgamma",-99.0, -99.0, mu,gamma,1e-5,1e-2,"ss-rayleigh-gans_%.3f_%.3f_%.3f_%.3f"%tuple(ssrg_coefs),'lmdz_snow',0.0))
        pam.df.addHydrometeor(('snow', AR_snow, -1,  -99., alpha, 2,  -99.,  -99., 13, 200, 'exp', -99.0, -99.0, -99.0, -99.0, 20e-5,  0.05,"ss-rayleigh-gans_%.3f_%.3f_%.3f_%.3f"%tuple(ssrg_coefs),'lmdz_snow',0.0))
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


        pam.p["hydro_q"][:] = q_ice
        pam.p["hydro_n"][:] = n_ice

        pam.set['verbose'] = verbosity
        pam.set['pyVerbose'] = verbosity
        pam.runPamtra(freq,checkData=False)


        #print("mu,gamma",mu,gamma,"  freq",freq,pam.r["Ze"][0][0][0][0][0][0])
        print(alpha,pam.r["Ze"])
        dBZ[j,i]=pam.r["Ze"]
        j+=1
    i+=1
#
#       =j+=1
#         l+=1
#     i+=1

plt.figure('Ze',figsize=(14,5))
plt.plot(alpha_list,dBZ[2],label="MRR")
plt.plot(alpha_list,dBZ[1],label="Mira")
plt.plot(alpha_list,dBZ[0],label="Basta")
plt.xlabel('$\alpha$')
plt.ylabel("Ze [dBZ]")
plt.legend()
plt.tight_layout()
# plt.savefig("/home/grzegorc/AWACA/Tests_DFR/Ze_"+name+"_q_"+str(q_ice*1000)+"_n_"+str(n_ice)+"_kappa_"+str(ssrg_coefs[0])+"_beta_"+str(ssrg_coefs[1])+"_gamma_"+str(ssrg_coefs[2])+"_zeta_"+str(ssrg_coefs[3])+".png")




plt.figure('DFR',figsize=(10,5))
plt.plot(alpha_list,dBZ[1]-dBZ[0],label='Z$_{Ka}$-Z$_{W}$ (Mira-Basta)')
plt.plot(alpha_list,dBZ[2]-dBZ[1],label='Z$_{K}$-Z$_{Ka}$ (MRR-Mira)')
plt.legend()
plt.xlabel('$\alpha$')
plt.ylabel("Ze [dB]")
plt.tight_layout()
# plt.savefig("/home/grzegorc/AWACA/Tests_DFR/DFR_"+name+"_q_"+str(q_ice*1000)+"_n_"+str(n_ice)+"_kappa_"+str(ssrg_coefs[0])+"_beta_"+str(ssrg_coefs[1])+"_gamma_"+str(ssrg_coefs[2])+"_zeta_"+str(ssrg_coefs[3])+".png")
plt.show()

# print("min Z$_{K}$-Z$_{Ka}$",np.min(dBZ[2]-dBZ[1]))
# print("min Z$_{Ka}$-Z$_{W}$",np.min(dBZ[1]-dBZ[0]))
