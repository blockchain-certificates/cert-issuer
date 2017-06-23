# Docker Installation

To use our Docker images, first [install Docker](https://docs.docker.com/engine/installation/) for your OS, ensuring your installation includes Docker Compose

The installation details will vary depending on your OS. For example, if you use Mac OSX, then you can simply install [Docker for Mac](https://docs.docker.com/docker-for-mac/#/download-docker-for-mac), which will include all the tools you need

Before moving on, ensure you have all the tools you need by running these 3 commands. Your details may vary depending on the version you installed; you just want to make sure these tools are available on your system
```
$ docker --version
Docker version 1.12.0, build 8eab29e

$ docker-compose --version
docker-compose version 1.8.0, build f3628c7

$ docker-machine --version
docker-machine version 0.8.0, build b85aac1
```

If any of the above steps fail, then your Docker installation needs to be fixed before proceeding. You can look for help at Docker's sites, for example the [Docker Forums](https://forums.docker.com/).