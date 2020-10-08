#!/bin/bash

telegram_chats_id=()

while [ "$1" != "" ]; do
    case $1 in
        -h   | --help )                  shift
                                  cat docker-run-help-command.txt
                                  echo
                                  exit 1
                                  ;;
        -rpc | --rpc-host )                shift
                                  export RPC_HOST=$1
                                  ;;
        -pk  | --address-private-key )   shift
                                  export ETH_PRIVATE_KEY=$1
                                  ;;
        -a   | --eth-from )              shift
                                  export ETH_FROM=$1
                                  ;;
        -n   | --network )               shift
                                  export NETWORK=$1
                                  ;;
        --rpc-timeout )                  shift
                                  export RPC_TIMEOUT=$1
                                  ;;
        --from-block )                   shift
                                  export FROM_BLOCK=$1
                                  ;;
        --max-errors )                   shift
                                  export MAX_ERRORS=$1
                                  ;;
#        --ethgasstation-api-key )           shift
#                                  export ETHGASSTATION_API_KEY=$1
#                                  ;;
        --fixed-gas-price )              shift
                                  export FIXED_GAS_PRICE=$1
                                  ;;
        --telegram-bot-token )           shift
                                  export TELEGRAM_BOT_TOKEN=$1
                                  ;;
        --keeper-name )                  shift
                                  export PROJECT_NAME=$1
                                  ;;
        --telegram-chat-id )              shift
                                  telegram_chats_id+=( "$1" )
                                  ;;

        * )                       shift
                                  ;;
    esac
                                  shift
done

export  TELEGRAM_CHAT_IDS="${telegram_chats_id[*]}"

if [[ -z $RPC_HOST || \
      -z $ETH_PRIVATE_KEY || \
      -z $NETWORK || \
      -z $ETH_FROM ]] ;
then
    cat docker-run-required-params.txt
    echo
    exit 1
fi

python keeper.py
