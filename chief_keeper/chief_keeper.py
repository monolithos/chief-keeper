# This file is part of the Maker Keeper Framework.
#
# Copyright (C) 2020 KentonPrescott
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging
import sys

from web3 import Web3, HTTPProvider

from chief_keeper.database import SimpleDatabase
from chief_keeper.spell import DSSSpell
from chief_keeper.firebase import FBDatabase

from pymaker import Address
from pymaker.util import is_contract_at
from pymaker.gas import DefaultGasPrice
from pymaker.keys import register_keys
from pymaker.lifecycle import Lifecycle
from pymaker.deployment import DssDeployment

class ChiefKeeper:
    """Keeper that lifts the hat and streamlines executive actions"""

    logger = logging.getLogger('chief-keeper')

    def add_arguments(self, parser):
        """Pass in arguements assign necessary variables/objects and instantiate other Classes"""

        parser.add_argument("--rpc-host", type=str, default="http://localhost:8545",
                            help="JSON-RPC host (default: `http://localhost:8545')")

        parser.add_argument("--rpc-timeout", type=int, default=10,
                            help="JSON-RPC timeout (in seconds, default: 10)")

        parser.add_argument("--network", type=str, required=True,
                            help="Network that you're running the Keeper on (options, 'mainnet', 'kovan', 'testnet')")

        parser.add_argument("--eth-from", type=str, required=True,
                            help="Ethereum address from which to send transactions; checksummed (e.g. '0x12AebC')")

        parser.add_argument("--eth-key", type=str, nargs='*',
                            help="Ethereum private key(s) to use (e.g. 'key_file=/path/to/keystore.json,pass_file=/path/to/passphrase.pass')")

        parser.add_argument("--dss-deployment-file", type=str, required=False,
                            help="Json description of all the system addresses (e.g. /Full/Path/To/configFile.json)")

        parser.add_argument("--chief-deployment-block", type=int, required=False, default=0,
                            help=" Block that the Chief from dss-deployment-file was deployed at (e.g. 8836668")

        parser.add_argument("--max-errors", type=int, default=100,
                            help="Maximum number of allowed errors before the keeper terminates (default: 100)")

        parser.add_argument("--debug", dest='debug', action='store_true',
                            help="Enable debug output")
    def __init__(self, args: list, **kwargs):
        parser = argparse.ArgumentParser("chief-keeper")
        self.add_arguments(parser)
        parser.set_defaults(cageFacilitated=False)
        self.arguments = parser.parse_args(args)

        provider = HTTPProvider(endpoint_uri=self.arguments.rpc_host,
                                request_kwargs={'timeout': self.arguments.rpc_timeout})
        self.web3: Web3 = kwargs['web3'] if 'web3' in kwargs else Web3(provider)

        self.web3.eth.defaultAccount = self.arguments.eth_from
        register_keys(self.web3, self.arguments.eth_key)
        self.our_address = Address(self.arguments.eth_from)

        if self.arguments.dss_deployment_file:
            self.dss = DssDeployment.from_json(web3=self.web3, conf=open(self.arguments.dss_deployment_file, "r").read())
        else:
            self.dss = DssDeployment.from_node(web3=self.web3)

        self.deployment_block = self.arguments.chief_deployment_block

        self.max_errors = self.arguments.max_errors
        self.errors = 0

        self.confirmations = 0

        logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s',
                            level=(logging.DEBUG if self.arguments.debug else logging.INFO))

    def main(self):
        """ Initialize the lifecycle and enter into the Keeper Lifecycle controller.

        Each function supplied by the lifecycle will accept a callback function that will be executed.
        The lifecycle.on_block() function will enter into an infinite loop, but will gracefully shutdown
        if it recieves a SIGINT/SIGTERM signal.
        """

        with Lifecycle(self.web3) as lifecycle:
            self.lifecycle = lifecycle
            lifecycle.on_startup(self.check_deployment)
            lifecycle.on_block(self.process_block)

    def check_deployment(self):
        self.logger.info('')
        self.logger.info('Please confirm the deployment details')
        self.logger.info(f'Keeper Balance: {self.web3.eth.getBalance(self.our_address.address) / (10**18)} ETH')
        self.logger.info(f'DS-Chief: {self.dss.ds_chief.address}')
        self.logger.info(f'DS-Pause: {self.dss.pause.address}')
        self.logger.info('')
        self.initial_query()

    def initial_query(self):
        """ Updates a locally stored database with the DS-Chief state since its last update.
        If a local database is not found, create one and query the DS-Chief state since its deployment.
        """
        self.logger.info('')
        self.logger.info('Querying DS-Chief state since last update ( !! Could take up to 15 minutes !! )')

        self.database = SimpleDatabase(self.web3,
                                       self.deployment_block,
                                       self.arguments.network,
                                       self.dss)
        result = self.database.create()

        self.logger.info(result)

    def process_block(self):
        """ Callback called on each new block. If too many errors, terminate the keeper.
        This is the entrypoint to the Keeper's monitoring logic
        """
        if self.errors >= self.max_errors:
            self.lifecycle.terminate()
        else:
            self.check_hat()
            self.check_eta()

    def check_hat(self):
        """ Ensures the Hat is on the proposal (spell, EOA, multisig, etc) with the most approval.

        First, the local database is updated with proposal addresses (yays) that have been `etched` in DSChief between
        the last block reviewed and the most recent block receieved. Next, it simply traverses through each address,
        checking if its approval has surpased the current Hat. If it has, it will `lift` the hat.

        If the current or new hat hasn't been casted nor plotted in the pause, it will `schedule` the spell
        """
        blockNumber = self.web3.eth.blockNumber
        self.logger.info(f'Checking Hat on block {blockNumber}')

        self.database.update_db_yays(blockNumber)
        yays = self.database.db.get(doc_id=2)["yays"]

        hat = self.dss.ds_chief.get_hat().address
        hatApprovals = self.dss.ds_chief.get_approvals(hat)

        contender, highestApprovals = hat, hatApprovals

        for yay in yays:
            contenderApprovals = self.dss.ds_chief.get_approvals(yay)
            if contenderApprovals > highestApprovals:
                contender = yay
                highestApprovals = contenderApprovals

        print(self.arguments.network)
        key = FBDatabase().getKey(self.arguments.network,contender)
        if contender != hat:
            self.logger.info(f'Lifting hat')
            self.logger.info(f'Old hat ({hat}) with Approvals {hatApprovals}')
            self.logger.info(f'New hat ({contender}) with Approvals {highestApprovals}')
            end_approvals = highestApprovals.__float__()
            FBDatabase().setValue(self.arguments.network, key, "end_approvals", end_approvals)
            
            self.dss.ds_chief.lift(Address(contender)).transact(gas_price=self.gas_price())
            spell = DSSSpell(self.web3, Address(contender))
            FBDatabase().setValue(self.arguments.network, key, "end_timestamp", self.database.get_eta_inUnix(spell))
        elif hat != "0x0000000000000000000000000000000000000000":
            self.logger.info(f'Current hat ({hat}) with Approvals {hatApprovals}')
            spell = DSSSpell(self.web3, Address(hat))
        else:
            return True
        self.check_schedule(spell, yay)        

        return True

    def check_schedule(self, spell: DSSSpell, yay: str):
        """ Schedules spells that haven't been scheduled nor casted """
        if is_contract_at(self.web3, Address(yay)):

            # Functional with DSSSpells but not DSSpells (not compatiable with DSPause)
            if spell.done() == False and self.database.get_eta_inUnix(spell) == 0:
                self.logger.info(f'Scheduling spell ({yay})')
                spell.schedule().transact(gas_price=self.gas_price())

    def check_eta(self):
        """ Cast spells that meet their schedule.

        First, the local database is updated with spells that have been scheduled between the last block
        reviewed and the most recent block receieved. Next, it simply traverses through each spell address,
        checking if its schedule has been reached/passed. If it has, it attempts to `cast` the spell.
        """
        blockNumber = self.web3.eth.blockNumber
        now = self.web3.eth.getBlock(blockNumber).timestamp
        self.logger.info(f'Checking scheduled spells on block {blockNumber}')

        self.database.update_db_etas(blockNumber)
        etas = self.database.db.get(doc_id=3)["upcoming_etas"]

        yays = list(etas.keys())

        for yay in yays:
            if etas[yay] <= now:
                spell = DSSSpell(self.web3, Address(yay))

                if spell.done() == False:
                    receipt = spell.cast().transact(gas_price=self.gas_price())

                    if receipt is None or receipt.successful == True:
                        del etas[yay]

                else:
                    del etas[yay]

        self.database.db.update({'upcoming_etas': etas}, doc_ids=[3])

    def gas_price(self):
        """ DefaultGasPrice """
        return DefaultGasPrice()


if __name__ == '__main__':
    ChiefKeeper(sys.argv[1:]).main()
