#!/bin/bash
if [ ! -f ipfs.tar.gz ]
then
	echo Download the proper version from https://dist.ipfs.tech/ and rename it ipfs.tar.gz
	echo Check also to have GO installed!
	exit 1
fi

# to intsall download the targz from there https://dist.ipfs.tech/ and rename it ipfs.tar.gz.
tar -xvzf ipfs.tar.gz
cd kubo
sudo bash install.sh
ipfs --version

go get -u github.com/Kubuxu/go-ipfs-swarm-key-gen/ipfs-swarm-key-gen
~/go/bin/ipfs-swarm-key-gen > ~/.ipfs/swarm.key

ipfs bootstrap rm all
ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
ipfs config Addresses.API /ip4/0.0.0.0/tcp/5001

# to execute: `ipfs daemon`