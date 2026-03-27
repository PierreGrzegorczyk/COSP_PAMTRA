import yaml
with open("config_test.yaml") as f:
    config = yaml.safe_load(f)


#_________for LMDZ_to_COSP.py______
with open("LMDZ_to_COSP_ini.py") as f:
    template = f.read()

output = template.format(**config)

with open("LMDZ_to_COSP.py", "w") as f:
    f.write(output)


#_________________COSP___________________
with open("COSP/driver/run/cosp2_input_ini.txt") as f:
    template = f.read()

output = template.format(**config)                      

with open("COSP/driver/run/cosp2_input.txt", "w") as f:
    f.write(output)

#_________________PAMTRA_________________
#with open("PAMTRA/PAMTRA_lmdz_MRR_ini.py") as f:
#with open("PAMTRA/PAMTRA_lmdz_MIRA35C_ini.py") as f:
#with open("PAMTRA/PAMTRA_lmdz_BASTA_ini.py") as f:
with open("PAMTRA/PAMTRA_lmdz_global_ini_test.py") as f:
    template = f.read()

output = template.format(**config)

with open("PAMTRA/PAMTRA_lmdz.py", "w") as f:
    f.write(output)

#___________PAMTRA post treatment________
with open("PAMTRA/Post_treatment_PAMTRA_ini.py") as f:
    template = f.read()

output = template.format(**config)

with open("PAMTRA/Post_treatment_PAMTRA.py", "w") as f:
    f.write(output)


#with open("PAMTRA/PAMTRA_lmdz_ini.py") as f:
#    template = f.read()

#output = template.format(**config)

#with open("PAMTRA/PAMTRA_lmdz.py", "w") as f:
#    f.write(output)



