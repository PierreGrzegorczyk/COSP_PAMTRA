from netCDF4 import Dataset
import matplotlib.pylab as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.colors as colors


## functions
def CFAD(Ze_mira,Alt_mira,Zmin,Zmax,step): ################## OLD version
    levels_W=np.arange(Zmin,Zmax+step,step)

    cfad_MIRA=np.zeros((len(Alt_mira),len(levels_W)))
    cfad_MIRA_norm=np.zeros((len(Alt_mira),len(levels_W)))
    #W-band

    for k in range(len(Alt_mira)-1):
        for j in range(len(levels_W)-1):
            cfad_MIRA[k,j]=cfad_MIRA[k,j]+np.sum(np.logical_and(levels_W[j]<Ze_mira[:,k],Ze_mira[:,k]<levels_W[j+1]))

    for j in range(len(levels_W)-1):
            cfad_MIRA_norm[:,j]=cfad_MIRA[:,j]/(np.sum(cfad_MIRA,1)+1e-30)
    return(levels_W,cfad_MIRA_norm)



def CFAD(Ze_mira, Alt_mira, Zmin, Zmax, step):

    levels_W = np.arange(Zmin, Zmax + step, step)
    n_alt = len(Alt_mira)
    n_bins = len(levels_W)

    cfad = np.zeros((n_alt, n_bins))

    # Digitize once (vectorized)
    bin_index = np.digitize(Ze_mira, levels_W)

    # Remove values exactly equal to bin edges (to match strict < <)
    mask_strict = (
        (Ze_mira > levels_W[0]) &
        (Ze_mira < levels_W[-1])
    )

    bin_index[~mask_strict] = -1

    for k in range(n_alt):
        valid = (bin_index[:, k] >= 0) & (bin_index[:, k] < n_bins)
        cfad[k] = np.bincount(
            bin_index[valid, k],
            minlength=n_bins
        )

    cfad_norm = cfad / (cfad.sum(axis=1, keepdims=True) + 1e-30)

    return levels_W, cfad_norm

path_image='/home/grzegorc/AWACA/Tests_ssrga/'

## Load simulator data

path='/home/grzegorc/AWACA/COSP_PAMTRA/'

names=["BASTA_D17_Hogan2017_v1.nc","BASTA_D17_Hogan2017_v2.nc",'BASTA_D17_Ori2021_column_dendrites.nc',"BASTA_D17_Ori2021_rimed_dendrites_aggregate.nc"]
for n in names:
    nc_file = path+n
    nc_data = Dataset(nc_file, "r")
    time=nc_data["time"][:]
    ncol=nc_data["col"][:]
    level=nc_data['level'][:]
    col=nc_data['col'][:]
    globals()['Ze_LMDZ'+n[10:-3]]=nc_data['Ze'][:]
    hgt=nc_data['hgt'][:]
    nc_data.close()



time_datetime = np.array([datetime(2025,2,12) + timedelta(seconds=s) for s in time])
time_mesh=np.zeros(np.shape(hgt))
time_mesh[:] = time[:, np.newaxis, np.newaxis]  # shape becomes (71, 1, 1)

time_mesh = np.empty(hgt.shape, dtype=object)
time_mesh[:] = time_datetime[:, None, None]
time_mesh = time[:, None, None]   # (71,1,1)
base = np.datetime64('2025-02-12T00:00:00')
time_mesh_dt = base + time_mesh.astype('timedelta64[s]')
dt=time_mesh[1][0][0]-time_mesh[0][0][0]
dt_synthetic=dt/np.shape(Ze_LMDZHogan2017_v1)[1]
time_mesh_synthetic=np.arange(float(time_mesh[0][0][0]),float(time_mesh[0][0][0])+float(np.shape(np.concatenate(Ze_LMDZHogan2017_v1,0))[0]*dt_synthetic),float(dt_synthetic))
time_mesh_synthetic = time_mesh_synthetic[:, None, None]   # (71,1,1)
time_mesh_synthetic_dt = base + time_mesh_synthetic.astype('timedelta64[s]')




## Figure quicklook Ze
Alt_D17=374/1000

vmin=-30
vmax=30
cmap = plt.get_cmap('jet', 50)
cmap.set_under('white')
plt.rcParams['font.size'] = 12

plt.figure('Ze',figsize=(12,7))
plt.subplot(221)
plt.title('a) '+names[0][10:-3],loc='left')
plt.pcolormesh(time_mesh_synthetic_dt[:,0,0],hgt[0,0]/1000-Alt_D17,np.concatenate(globals()['Ze_LMDZ'+names[0][10:-3]],0).T,cmap=cmap,vmax=vmax, vmin=vmin)
plt.ylim(0,10)
plt.colorbar(label='Z$_{W}$ [dBZ]')

plt.subplot(222)
plt.title('b) '+names[1][10:-3],loc='left')
plt.pcolormesh(time_mesh_synthetic_dt[:,0,0],hgt[0,0]/1000-Alt_D17,np.concatenate(globals()['Ze_LMDZ'+names[1][10:-3]],0).T,cmap=cmap,vmax=vmax, vmin=vmin)
plt.tight_layout()
plt.ylim(0,10)
plt.colorbar(label='Z$_{W}$ [dBZ]')

plt.subplot(223)
plt.title('c) '+names[2][10:-3],loc='left')
plt.pcolormesh(time_mesh_synthetic_dt[:,0,0],hgt[0,0]/1000-Alt_D17,np.concatenate(globals()['Ze_LMDZ'+names[2][10:-3]],0).T,cmap=cmap,vmax=vmax, vmin=vmin)
plt.ylim(0,10)
plt.colorbar(label='Z$_{W}$ [dBZ]')

plt.subplot(224)
plt.title('d) '+names[3][10:-3],loc='left')
plt.pcolormesh(time_mesh_synthetic_dt[:,0,0],hgt[0,0]/1000-Alt_D17,np.concatenate(globals()['Ze_LMDZ'+names[3][10:-3]],0).T,cmap=cmap,vmax=vmax, vmin=vmin)
plt.tight_layout()
plt.ylim(0,10)
plt.colorbar(label='Z$_{W}$ [dBZ]')

plt.savefig(path_image+"/Ze.png",dpi=600)
plt.show()

##CFAD Ze

levels_W,globals()['cfad_LMDZ'+names[0][10:-3]]=CFAD(np.concatenate(globals()['Ze_LMDZ'+names[0][10:-3]],0),hgt[0,0]/1000-Alt_D17,-50,50,1.5)
levels_W,globals()['cfad_LMDZ'+names[1][10:-3]]=CFAD(np.concatenate(globals()['Ze_LMDZ'+names[1][10:-3]],0),hgt[0,0]/1000-Alt_D17,-50,50,1.5)
levels_W,globals()['cfad_LMDZ'+names[2][10:-3]]=CFAD(np.concatenate(globals()['Ze_LMDZ'+names[2][10:-3]],0),hgt[0,0]/1000-Alt_D17,-50,50,1.5)
levels_W,globals()['cfad_LMDZ'+names[3][10:-3]]=CFAD(np.concatenate(globals()['Ze_LMDZ'+names[3][10:-3]],0),hgt[0,0]/1000-Alt_D17,-50,50,1.5)

vmin=10**-3
vmax=1
cmap='jet'

plt.figure('DBZ cfad',figsize=(14,10))


plt.subplot(221)
plt.title('a) '+names[0][10:-3],loc='left')
plt.pcolormesh(levels_W,hgt[0,0,:]/1000-Alt_D17,globals()['cfad_LMDZ'+names[0][10:-3]],norm=colors.LogNorm(vmin=vmin,vmax=vmax),cmap=cmap)
plt.ylabel('Altitude [km]')
plt.xlabel('Z$_{W}$ [dBZ]')
plt.colorbar(label='Normalized frequency')
plt.ylim(0,14)

plt.subplot(222)
plt.title('a) '+names[1][10:-3],loc='left')
plt.pcolormesh(levels_W,hgt[0,0,:]/1000-Alt_D17,globals()['cfad_LMDZ'+names[1][10:-3]],norm=colors.LogNorm(vmin=vmin,vmax=vmax),cmap=cmap)
plt.ylabel('Altitude [km]')
plt.xlabel('Z$_{W}$ [dBZ]')
plt.colorbar(label='Normalized frequency')
plt.ylim(0,14)

plt.subplot(223)
plt.title('c) '+names[2][10:-3],loc='left')
plt.pcolormesh(levels_W,hgt[0,0,:]/1000-Alt_D17,globals()['cfad_LMDZ'+names[2][10:-3]],norm=colors.LogNorm(vmin=vmin,vmax=vmax),cmap=cmap)
plt.ylabel('Altitude [km]')
plt.xlabel('Z$_{W}$ [dBZ]')
plt.colorbar(label='Normalized frequency')
plt.ylim(0,14)

plt.subplot(224)
plt.title('d) '+names[3][10:-3],loc='left')
plt.pcolormesh(levels_W,hgt[0,0,:]/1000-Alt_D17,globals()['cfad_LMDZ'+names[3][10:-3]],norm=colors.LogNorm(vmin=vmin,vmax=vmax),cmap=cmap)
plt.ylabel('Altitude [km]')
plt.xlabel('Z$_{W}$ [dBZ]')
plt.colorbar(label='Normalized frequency')
plt.ylim(0,14)

plt.tight_layout()
plt.savefig(path_image+"/Cfad_Ze.png",dpi=600)
plt.show()


## Percentiles



def Perc(Ze_mira,Alt_mira,percs): ################## OLD version

    Perc_out=np.zeros((len(percs),len(Alt_mira)))
    Perc_out[:,:]=np.nan
        #W-band
    for k in range(len(Alt_mira)-1):
        if np.sum(np.logical_and(~np.isnan(Ze_mira[:,k])==True,Ze_mira[:,k]>-100))>0:
            Perc_out[:,k]=np.percentile(Ze_mira[:,k][np.logical_and(~np.isnan(Ze_mira[:,k])==True,Ze_mira[:,k]>-100)],percs)
    return(Perc_out)



percs=[25,50,75]
globals()['Perc_LMDZ'+names[0][10:-3]]=Perc(np.concatenate(globals()['Ze_LMDZ'+names[0][10:-3]],0),hgt[0,0]/1000-Alt_D17,percs)
globals()['Perc_LMDZ'+names[1][10:-3]]=Perc(np.concatenate(globals()['Ze_LMDZ'+names[1][10:-3]],0),hgt[0,0]/1000-Alt_D17,percs)
globals()['Perc_LMDZ'+names[2][10:-3]]=Perc(np.concatenate(globals()['Ze_LMDZ'+names[2][10:-3]],0),hgt[0,0]/1000-Alt_D17,percs)
globals()['Perc_LMDZ'+names[3][10:-3]]=Perc(np.concatenate(globals()['Ze_LMDZ'+names[3][10:-3]],0),hgt[0,0]/1000-Alt_D17,percs)

plt.figure("Ze percentiles", figsize=(5,6))

# ----- LMDZ -----
colors=['k','r','lightblue','orange']

for k in range(0,4,1):
    plt.plot(globals()['Perc_LMDZ'+names[k][10:-3]][1],hgt[0,0]/1000 - Alt_D17,lw=2,label=names[k][10:-3],color=colors[k])
    plt.plot(globals()['Perc_LMDZ'+names[k][10:-3]][0],hgt[0,0]/1000 - Alt_D17,ls='--',lw=1,color=colors[k])
    plt.plot(globals()['Perc_LMDZ'+names[k][10:-3]][2],hgt[0,0]/1000 - Alt_D17,ls='--',lw=1,color=colors[k])



plt.xlabel(r'Ze$_{W}$ [dBZ]')
plt.ylabel('Altitude [km]')
plt.ylim(0,12)

plt.legend(frameon=False, fontsize=12)
plt.tight_layout()
plt.savefig(path_image+"Percentiles_Ze.png",dpi=600)
plt.show()