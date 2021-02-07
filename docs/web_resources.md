## Web Resources

This document describes how to run a web service which accepts web requests over port 80 (HTTP).

## HTTP Docker setup

To build a cert-issuer that accepts web requests, run the following command and substitute www.example.com
 with your domain name.  The name you substitute is used by the Nginx server block to match request domains.

```
sudo docker build . -t bc/cert-issuer-http:1.0 -f Dockerfile.web \
--build-arg NETWORK=regtest \
--build-arg SERVER=www.example.com
```

Once the build is complete, start the web service:

```
sudo docker run -it --entrypoint "/cert-issuer/start-cert-issuer.sh" -p 80:80 bc/cert-issuer-http:1.0
```

Web requests can now be sent as a JSON array of unsigned certificates with the HTTP `POST` method.

Example Request:
```
POST http://example.com/cert_issuer/api/v1.0/issue
```

Example Payload:
```
[
    { "cert": "cert data" },
    { "cert1": "more certs"},
    { "cert2": "certs for days"}
]
```

You can sign the example certs in this repo by calling:
```
curl -X POST -H "Content-Type: application/json" -d "[$(cat examples/data-testnet/unsigned_certificates/3bc1a96a-3501-46ed-8f75-49612bbac257.json), $(cat examples/data-testnet/unsigned_certificates/4e7d75c5-281c-45de-93cc-3212b1349ee9.json)]" http://example.com/cert_issuer/api/v1.0/issue
```

## Extended HTTP/HTTPS Docker setup

A named volume is useful for persisting chain state, for example:
```
sudo docker run -it -v cert-issuer:/root/.bitcoin -p 80:80 bc/cert-issuer:1.0
```

Also, a Dockerfile is provided for sending requests with TLS using `Dockerfile.web.tls` for implementations beyond reg_test

Build HTTPS docker image:
```
sudo docker build -t bc/cert-issuer-https:1.0  \
-f Dockerfile.web.tls . --build-arg NETWORK=testnet \
--build-arg SERVER=www.example.com --build-arg RPC_USER=j0hnny \
--build-arg RPC_PASSWORD=mn3m0nic \
--build-arg ISSUER=legacy_address \
--build-arg CRT=file.crt \
--build-arg KEY=file.key
```

Launch HTTPS docker container:
```
sudo docker run -it -p 443:443 bc/cert-issuer-https:1.0
```

Happy hacking =]
