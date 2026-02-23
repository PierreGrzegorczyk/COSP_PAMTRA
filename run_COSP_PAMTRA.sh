echo "_________________________________________________"
echo "LOAD config.yaml : "
echo "important parameters as input"
echo "_________________________________________________"
python3 config_init.py


echo "_________________________________________________"
echo "RUN LMDZ_to_COSP.py : "
echo "Read and write LMDZ data as .nc readable by COSP"
echo "_________________________________________________"
python3 LMDZ_to_COSP.py

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



