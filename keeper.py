import os
import uuid
import json

import web3

from chief_keeper.chief_keeper import ChiefKeeper


BASE_PATH = os.path.dirname(__file__)

NETWORK = os.environ.get("NETWORK", "mainnet")


def generate_params_line(param_group: list):
    args = []
    for param in param_group:
        if param[1] is not None and not isinstance(param[1], (bool, list)):
            args.append(param[0])
            args.append(str(param[1]))
        elif isinstance(param[1], bool) and param[1]:
            args.append(param[0])
        elif isinstance(param[1], list) and len(param[1]) > 0 and param[1][0] is not None:

            for item in param[1]:
                args.append(param[0])
                args.append(str(item))
    return args


class EnvParam:
    value = None

    def __init__(self, env_name: str, cast_type, required, default=None):
        try:
            if cast_type in (list, set, tuple):
                self.value = cast_type(os.environ[env_name].split())
            else:
                self.value = cast_type(os.environ[env_name])
        except (TypeError, KeyError) as e:
            if required:
                raise Exception(f'Param {env_name} is required and must be cast to {str(cast_type)}')
            if cast_type in (list, set, tuple) and default is not None:
                self.value = cast_type([default])
            else:
                self.value = cast_type(default) if default is not None else None


def get_telegram_params():
    telegram_bot_token = EnvParam(env_name="TELEGRAM_BOT_TOKEN", cast_type=str, required=False).value

    if telegram_bot_token:
        chat_ids = {}
        ids = EnvParam(env_name="TELEGRAM_CHAT_IDS", cast_type=list, required=False, default=[]).value
        list(map(lambda x: chat_ids.update({x: x}), ids))
        telegram_conf_file = os.path.join(BASE_PATH, "telegram_conf.json")
        telegram_conf = {
            "bot_token": telegram_bot_token,
            "project_name": EnvParam(env_name="PROJECT_NAME", cast_type=str, required=False, default="monolithos_market_maker_keeper").value,
            "use_proxy": False,
            "request_kwargs": {
                "proxy_url": "",
                "urllib3_proxy_kwargs": {
                    "username": "",
                    "password": ""
                }
            },
            "chat_ids": chat_ids
        }
        with open(telegram_conf_file, "w") as file:
            file.write(json.dumps(telegram_conf))

        return [('--telegram-log-config-file', telegram_conf_file)]
    else:
        return []


if __name__ == '__main__':
    telegram_params = get_telegram_params()
    password = str(uuid.uuid4())
    pk = EnvParam(env_name="ETH_PRIVATE_KEY", cast_type=str, required=True).value
    encrypt_pk = web3.Web3().eth.account.encrypt(private_key=pk, password=password)

    ETH_FROM = web3.Web3.toChecksumAddress(encrypt_pk["address"])
    P_ETH_FROM = EnvParam(env_name="ETH_FROM", cast_type=str, required=True).value

    if P_ETH_FROM.upper() != ETH_FROM.upper():
        raise Exception(f"private key does not match the ETH_FROM address ({P_ETH_FROM})")

    key_file = os.path.join(BASE_PATH, "key.json")
    pass_file = os.path.join(BASE_PATH, "pass.pass")
    with open(key_file, "w") as file:
        file.write(json.dumps(encrypt_pk))
    with open(pass_file, "w") as file:
        file.write(password)

    ETH_KEY = f'key_file={key_file},pass_file={pass_file}'

    required_params = [
        ('--rpc-host', EnvParam(env_name="RPC_HOST", cast_type=str, required=True).value),
        ('--network', NETWORK),
        ('--eth-from', str(ETH_FROM)),
        ('--eth-key', str(ETH_KEY)),
        ('--dss-deployment-file', str(os.path.join(BASE_PATH, 'addresses', f'{NETWORK}-addresses.json'))),
    ]

    optional_params = [
        ('--rpc-timeout', EnvParam(env_name="RPC_TIMEOUT", cast_type=int, required=False).value),
        ('--chief-deployment-block', EnvParam(env_name="FROM_BLOCK", cast_type=int, required=False, default=10310344).value),

        ('--ethgasstation-api-key', EnvParam(env_name="ETHGASSTATION_API_KEY", cast_type=str, required=False).value),
        ('--fixed-gas-price', EnvParam(env_name="FIXED_GAS_PRICE", cast_type=float, required=False).value),

        ('--max-errors', EnvParam(env_name="MAX_ERRORS", cast_type=int, required=False).value),
        # ('--debug', True),
    ]

    keeper_args = generate_params_line(required_params) + generate_params_line(optional_params)
    keeper_args += generate_params_line(telegram_params)
    ChiefKeeper(keeper_args).main()
    print(f"ChiefKeeper {keeper_args}")
