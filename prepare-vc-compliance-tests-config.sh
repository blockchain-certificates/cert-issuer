echo "chain=mockchain" >> conf.ini
echo "usb_name=${PWD}" >> conf.ini
touch pk.txt
echo "key_file=pk.txt" >> conf.ini

echo "Prepared config file for VC compliance test suite"
cat conf.ini