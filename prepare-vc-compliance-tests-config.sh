# download VC examples context
mkdir data/context
curl -L https://www.w3.org/2018/credentials/examples/v1 >> ${PWD}/data/context/vc-examples-v1.json
curl -L https://www.w3.org/ns/odrl.jsonld >> ${PWD}/data/context/odrl.json
echo "context_urls=[https://www.w3.org/2018/credentials/examples/v1, https://www.w3.org/ns/odrl.jsonld]" >> conf.ini
echo "context_file_paths=[data/context/vc-examples-v1.json, data/context/odrl.json]" >> conf.ini

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
echo "multiple_proofs=concurrent" >> conf.ini

echo "Prepared config file for VC compliance test suite"
cat conf.ini