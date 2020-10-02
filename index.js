const express = require('express');
const bodyParser = require('body-parser');
const verify = require('./middlewares/verify');
const server = express();

server.use(bodyParser.json({limit: '5mb'}));
const port = 3000;

server.get('/', (req, res) => res.send('Hello World!'));

server.post('/verify', verify);

server.listen(port, () => console.log(`Example app listening at http://localhost:${port}`));
