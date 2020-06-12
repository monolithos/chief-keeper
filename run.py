from chief_keeper.chief_keeper import ChiefKeeper

RPC_HOST = "https://kovan.infura.io/v3/"
NETWORK = "kovan"

ETH_FROM = "0xC0CCab7430aEc0C30E76e1dA596263C3bdD82932"
KEY_FILE = "/home/captain/development/dss-deploy-scripts/keystore.json"
PASS_FILE = "/home/captain/development/dss-deploy-scripts/p.pass"

ADDRESSES_FILE = "/home/captain/development/makerdao_python/chief-keeper/addresses/kovan-addresses.json"


if __name__ == '__main__':
    flip_args = [
        '--rpc-host', RPC_HOST,
        '--eth-from', ETH_FROM,
        '--network', NETWORK,
        '--eth-key', f'key_file={KEY_FILE},pass_file={PASS_FILE}',
        '--dss-deployment-file', ADDRESSES_FILE,
        # '--chief-deployment-block', '1',
        # '--debug'
    ]
    ChiefKeeper(flip_args).main()
