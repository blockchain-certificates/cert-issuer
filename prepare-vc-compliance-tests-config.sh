echo "chain=mockchain" >> conf.ini
echo "usb_name=${PWD}" >> conf.ini
touch pk.txt
echo "key_file=pk.txt" >> conf.ini
mkdir data/unsigned_certificates
mkdir data/blockchain_certificates
echo "unsigned_certificates_dir=${PWD}/data/unsigned_certificates" >> conf.ini
echo "blockchain_certificates_dir=${PWD}/data/blockchain_certificates" >> conf.ini

echo "Prepared config file for VC compliance test suite"
cat conf.ini