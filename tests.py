import pandas as pd
params_from_dataset_list = pd.read_feather('/home/grzegorc/Downloads/params_from_dataset_10spec.feather')

for i in range(len(params_from_dataset_list)):
    params_from_dataset = params_from_dataset_list.iloc[i]





vel0 = np.linspace(-params_from_dataset['v_nyq_W'],params_from_dataset['v_nyq_W'],params_from_dataset['fft_len_W'],endpoint=False)
dv0 = vel0[1]-vel0[0]

    vel0 = np.linspace(-params_from_dataset['v_nyq_W'],params_from_dataset['v_nyq_W'],params_from_dataset['fft_len_W'],endpoint=False)
    dv0 = vel0[1]-vel0[0]
    pam.nmlSet['radar_pnoise0'] = 10*np.log10(np.array(params_from_dataset['noise_level_Ka']))+10*np.log10(dv0*params_from_dataset['fft_len_Ka'])

    pred = {}



## me


    v_max=13.29 #vit nyq
    n_fft=512


    vel0 = np.linspace(-v_max,v_max,n_fft,endpoint=False)
    dv0 = vel0[1]-vel0[0]

    Z_sensi=-60.3
    dv0 = vel0[1]-vel0[0]
    pam.nmlSet['radar_pnoise0'] = Z_sensi+10*np.log10(dv0*n_fft)
