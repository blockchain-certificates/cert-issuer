echo "chain=mockchain" >> conf.ini
echo "usb_name=${PWD}" >> conf.ini
echo "5JwtrfUV5ZZe9z3q62whK4mQduxYpa7f25UXAKJCLTN1qTiRBSF" >> pk.txt #1KeZVz9iqpD9YeiExY2Wxu6XXexZ3pdxwe
echo "key_file=pk.txt" >> conf.ini
mkdir data/unsigned_certificates
mkdir data/blockchain_certificates
mkdir data/work
echo "unsigned_certificates_dir=${PWD}/data/unsigned_certificates" >> conf.ini
echo "blockchain_certificates_dir=${PWD}/data/blockchain_certificates" >> conf.ini
echo "work_dir=${PWD}/data/work" >> conf.ini
echo "no_safe_mode" >> conf.ini

echo "Prepared config file for VC compliance test suite"
cat conf.ini