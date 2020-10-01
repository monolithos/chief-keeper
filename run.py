from chief_keeper.chief_keeper import ChiefKeeper

NETWORK = "kovan"
# NETWORK = "mainnet"


if NETWORK.lower() == "kovan":
    RPC_HOST = "https://kovan.infura.io/v3/******"
    ETH_FROM = "0x000000000000000000000000000"
    KEY_FILE = "/PATH/TO/KEY/FILE.json"
    PASS_FILE = "/PATH/TO/PASS/FILE.pass"

    ADDRESSES_FILE = "PATH/TO/ADDRESS/FILE.json"

elif NETWORK.lower() == "mainnet":
    RPC_HOST = "https://mainnet.infura.io/v3/*******"
    ETH_FROM = "0x000000000000000000000000000"
    KEY_FILE = "/PATH/TO/KEY/FILE.json"
    PASS_FILE = "/PATH/TO/PASS/FILE.pass"

    ADDRESSES_FILE = "PATH/TO/ADDRESS/FILE.json"
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
