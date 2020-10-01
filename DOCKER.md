#  Dockerized Chief-Keeper

# Build and Run the chief-keeper locally

## Prerequisite:
- docker installed: https://docs.docker.com/install/
- Git

## Installation
Clone the project and install required third-party packages:
```
git clone git@github.com:monolithos/chief-keeper.git
cd chief-keeper
```

## Build
### Build the docker image locally
From within the `chief-keeper` directory, run the following command:
```
docker build . -t chief-keeper
```

## Run
### Run the chief-keeper
Running the chief-keeper requires you to pass the environment file to the container, map a volume to the secrets directory to allow the chief-keeper to access your keystore files, and map a volume for the DB files.

From within the `chief-keeper` directory, run the following command:

```
docker run --name "Chief_keeper" --rm -d monolithos/chief-keeper \
    --rpc-host https://kovan.infura.io/v3/0000000_API_KEY_000000000 \
    --address-private-key 0x874FE5000000000_PRIVATE_KEY_00000000000000000E1F0E2E1E37CD525F2339A79F8 \
    --eth-from 0xC0CCab743000000_ADDRESS_000C3bdD82932 \
    --network kovan \
```

view output: 
```
docker run --name "Chief_keeper" --rm monolithos/chief-keeper \
    --rpc-host https://kovan.infura.io/v3/0000000_API_KEY_000000000 \
    --address-private-key 0x874FE5000000000_PRIVATE_KEY_00000000000000000E1F0E2E1E37CD525F2339A79F8 \
    --eth-from 0xC0CCab743000000_ADDRESS_000C3bdD82932 \
    --network kovan \
```

### View all parameters
 - Run `docker run --name "Chief_keeper" --rm monolithos/chief-keeper --help`
