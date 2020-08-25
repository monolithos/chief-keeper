from chief_keeper.chief_keeper import ChiefKeeper
from chief_keeper.firebase import FBDatabase
from datetime import datetime

NETWORK = "kovan"
# NETWORK = "mainnet"


if NETWORK.lower() == "kovan":
    RPC_HOST = "https://kovan.infura.io/v3/84e2b94042f24cc9b111b886f9ea4c28"
    ETH_FROM = "0xC0CCab7430aEc0C30E76e1dA596263C3bdD82932"
    KEY_FILE = "/home/ubuntu/.ethereum/keystore/UTC--2020-08-13T03-10-36.646714195Z--c0ccab7430aec0c30e76e1da596263c3bdd82932"
    PASS_FILE = "/home/ubuntu/dev/pass.pass"

    ADDRESSES_FILE = "/home/ubuntu/dev/kovan-addresses.json"

elif NETWORK.lower() == "mainnet":
    RPC_HOST = "https://mainnet.infura.io/v3/*******"
    ETH_FROM = "0x000000000000000000000000000"
    KEY_FILE = "/PATH/TO/KEY/FILE.json"
    PASS_FILE = "/PATH/TO/PASS/FILE.pass"

    ADDRESSES_FILE = "/PATH/TO/ADDRESSES/FILE.json"
else:
    raise Exception('NOT SUPPORTED NETWORK')


if __name__ == '__main__':
    start_args = [
        '--rpc-host', RPC_HOST,
        '--eth-from', ETH_FROM,
        '--network', NETWORK,
        '--eth-key', f'key_file={KEY_FILE},pass_file={PASS_FILE}',
        '--dss-deployment-file', ADDRESSES_FILE,
        # '--chief-deployment-block', '1',
        # '--debug'
    ]
    ChiefKeeper(start_args).main()
    # FBDatabase().getData()
    # key = FBDatabase().getKey("0xed5357884884Ce2f640505d5BE6BB9EF7Ed4599c")
    # print(key)
    