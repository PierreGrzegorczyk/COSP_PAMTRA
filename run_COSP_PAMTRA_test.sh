echo "_________________________________________________"
echo "LOAD config.yaml : "
echo "important parameters as input"
echo "_________________________________________________"
python3 my_config_init_test.py


echo "_________________________________________________"
echo "RUN LMDZ_to_COSP.py : "
echo "Read and write LMDZ data as .nc readable by COSP"
echo "_________________________________________________"
python3 LMDZ_to_COSP_test.py

echo "_________________________________________________"
echo "START RUN COSP"
echo "_________________________________________________"

cd COSP/driver/run/
./cosp2_test cosp2_input.txt 

echo "_________________________________________________"
echo "END RUN COSP"
echo "_________________________________________________"
echo ""

pwd
cd ../../../PAMTRA
source Start_Pam.sh
echo "_________________________________________________"
echo "START RUN PAMTRA from .py code"
echo "_________________________________________________"
python3 PAMTRA_lmdz.py 
#python3 PAMTRA/PAMTRA_lmdz_Awaca.py

echo "_________________________________________________"
echo "POST-TREATMENT NEEDED ?"
python3 Post_treatment_PAMTRA.py
echo "_________________________________________________"


echo "_________________________________________________"
echo "End of computation !!!"
echo "See the .nc in output repository"
echo "_________________________________________________"
