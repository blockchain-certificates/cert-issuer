const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

function saveFileToUnsignedCertificates (data) {
  const targetPath = path.join(__dirname, '..', 'data/unsigned_certificates', 'sample.json');
  fs.writeFile(targetPath, JSON.stringify(data), (err) => {
    if (err) {
      throw err;
    }
    console.log('The file has been saved!');
  });
}

async function getGeneratedCertificate () {
  const targetPath = path.join(__dirname, '..', 'data/blockchain_certificates', 'sample.json');
  return new Promise((resolve, reject) => {
    fs.readFile(targetPath, 'utf8', (err, data) => {
      if (err) {
        reject(err);
      }
      resolve(JSON.parse(data));
    });
  });
}

function verify (req, res) {
  const cert = req.body.certificate;
  console.log('now processing', cert);

  saveFileToUnsignedCertificates(cert);

  return new Promise((resolve, reject) => {
    let stdout = [];
    let stderr = [];
    const verificationProcess = spawn('python3', ['cert_issuer/__main__.py', '-c', 'conf.ini']);
    verificationProcess.stdout.pipe(process.stdout);

    verificationProcess.on('error', err => reject(new Error(err)));
    verificationProcess.stdout.on('error', err => reject(new Error(err)));
    verificationProcess.stderr.on('error', err => reject(new Error(err)));
    verificationProcess.stdin.on('error', err => reject(new Error(err)));

    verificationProcess.stdout.on('data', data => stdout.push(data));
    verificationProcess.stderr.on('data', data => stderr.push(data));

    verificationProcess.stdin.end('');

    verificationProcess.on('close', async code => {
      stdout = stdout.join('').trim();
      stderr = stderr.join('').trim();

      if (code === 0) {
        console.log(stdout, stderr);
        console.log('success');
        const certificate = await getGeneratedCertificate();
        console.log(certificate);
        res.send({
          success: true,
          certificate
        });
        return resolve({ successResolve: true });
      }

      let error = new Error(`command exited with code: ${code}\n\n ${stdout}\n\n ${stderr}`);

      // emulate actual Child Process Errors
      error.path = 'python3';
      error.syscall = 'spawn python3';
      error.spawnargs = ['cert_issuer', '-c', 'conf.ini'];

      res.send({
        success: false,
        error,
        stderr
      });
      return reject(error);
    })
  });
}


module.exports = verify;
