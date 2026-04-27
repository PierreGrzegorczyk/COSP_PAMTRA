from netCDF4 import Dataset
import matplotlib.pylab as plt
import numpy as np

#_________LMDZ data___________________
nc_file = '../Cosp_input_from_LMDZ.nc'
nc_data = Dataset(nc_file, "r")

time = nc_data.variables['time_counter'][:]
nc_data.close()

end = 'end'
jsel={jsel}
isel={isel}

if jsel == end:
    jsel = len(time)

## config parameters

Run_pamtra={Run_pamtra}
Run_spectra={Run_spectra}
Write_output={Write_output}

output_file = "{FOUTPUTpamtra}"
output_file2 = output_file[:-3]+"_upward_part.nc"

if "{Where_is_radar}"=="Aircraft" and "{Pointing}"=='both' and Write_output==True:
    print("YES: Starts post .nc treatment to merge both radar pointing directions")

    path="/home/grzegorc/AWACA/COSP_PAMTRA/output/"

    Down = Dataset(output_file, "r")

    Up = Dataset(output_file2, "r")

    nc_aircraft = Dataset("{Aircraft_alt_file}", "r")

    Z_plane=nc_aircraft['radar_altitude'][:][isel:jsel]

    variables_common=["time","col","level","hydro","bins","lon","lat", "temp","relhum", "hgt", "press", "hydro_q","N_ice","N_liq","N_snow","N_rain"]

    if Run_spectra==True:
        variables_to_crop=["Ze", "MDV", "Sigma", "Skewness", "Kurtosis", "Spectra"]
    else:
        variables_to_crop=["Ze"]

    for n in variables_common:
        globals()[n]=Up[n][:]

    mask=level.T>Z_plane # All model levels higher than the plane
    mask=np.repeat(mask[:,np.newaxis,:].T,len(col),axis=1)==True
    mask2=np.repeat(mask[:,:,:,np.newaxis],len(bins),axis=3)==True


    for n in variables_to_crop:
        globals()[n+"_up"]=Up[n][:]
        globals()[n+"_down"]=Down[n][:]
        globals()[n]=globals()[n+"_down"].copy()
        if len(np.shape(globals()[n]))==4:
            globals()[n] = np.where(mask2, globals()[n+"_up"],globals()[n+"_down"])
        else:
            globals()[n] = np.where(mask, globals()[n+"_up"],globals()[n+"_down"])

    Down.close()
    Up.close()
    nc_aircraft.close()

# ######## write new .nc file

    ncol=np.shape(temp)[1]
    with Dataset(output_file, "w", format="NETCDF4") as nc_out:

    # Dimensions
        nc_out.createDimension("time", len(time))
        nc_out.createDimension("col", ncol)
        #nc_out.createDimension("level", len(pam.r["radar_hgt"][0,0,:]))
        nc_out.createDimension("level", temp.shape[2])
        nc_out.createDimension("hydro", 4)
        nc_out.createDimension("bins", len(bins))

    # Variables simples
        nc_out.createVariable("time", "f8", ("time",))[:] = time
        nc_out.createVariable("col", "i4", ("col",))[:] = np.arange(ncol)
        nc_out.createVariable("level", "f4", ("time","level"))[:] = level
        nc_out.createVariable("hydro", "i4", ("hydro",))[:] = np.arange(4)
        nc_out.createVariable("bins", "f4", ("bins",))[:] = bins
    # Écriture des champs
        nc_out.createVariable("lon", "f4", ("time", "col"))[:] = lon
        nc_out.createVariable("lat", "f4", ("time", "col"))[:] = lat
        nc_out.createVariable("temp", "f4", ("time", "col", "level"))[:] = temp
        nc_out.createVariable("relhum", "f4", ("time", "col", "level"))[:] = relhum
        nc_out.createVariable("hgt", "f4", ("time", "col", "level"))[:] = hgt
        nc_out.createVariable("press", "f4", ("time", "col", "level"))[:] = press
        nc_out.createVariable("hydro_q", "f4", ("time", "col", "level", "hydro"))[:] = hydro_q
        nc_out.createVariable("N_ice", "f4", ("time", "col", "level"))[:] = N_ice
        nc_out.createVariable("N_liq", "f4", ("time", "col", "level"))[:] = N_liq
        nc_out.createVariable("N_snow", "f4", ("time", "col", "level"))[:] = N_snow
        nc_out.createVariable("N_rain", "f4", ("time", "col", "level"))[:] = N_rain
        nc_out.createVariable("Ze", "f4", ("time", "col", "level"))[:] = Ze

        if Run_spectra==True: # only for spectra radar_mode
            nc_out.createVariable("MDV", "f4", ("time", "col", "level"))[:] = MDV
            nc_out.createVariable("Sigma", "f4", ("time", "col", "level"))[:] = Sigma
            nc_out.createVariable("Skewness", "f4", ("time", "col", "level"))[:] = Skewness
            nc_out.createVariable("Kurtosis", "f4", ("time", "col", "level"))[:] = Kurtosis
            nc_out.createVariable("Spectra", "f4", ("time", "col", "level","bins"))[:] = Spectra
    print("New PAMTRA output saved as NetCDF file  ",output_file)
    print("Finished post .nc treatment")

else:
    print("No post .nc treatment")
