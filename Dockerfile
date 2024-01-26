FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

COPY ./ /app

WORKDIR /app

RUN apt update


# install go and ipfs
RUN apt install golang-go -y
RUN tar -xvzf ipfs.tar.gz
WORKDIR /app/kubo
RUN bash install.sh
RUN apt install -y git
RUN ipfs init
RUN go env -w GO111MODULE=off
RUN go get -u github.com/Kubuxu/go-ipfs-swarm-key-gen/ipfs-swarm-key-gen
RUN ~/go/bin/ipfs-swarm-key-gen  > ~/.ipfs/swarm.key
RUN ipfs bootstrap rm all
RUN ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
RUN ipfs config Addresses.API /ip4/0.0.0.0/tcp/5001
WORKDIR /app
# set the geographical area

RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone


# install python3.9

RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install python3.9 -y
RUN apt install -y python3-pip

# install python dependencies
RUN pip3 install -r requirements.txt


# install node
RUN apt install curl -y
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt install -y nodejs


# install node dependencies
RUN npm install

# web API
EXPOSE 3000

# hardhat node
EXPOSE 8545

CMD ["bash", "start.sh"]


