# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2019 KentonPrescott
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


import pytest

import time
from typing import List
import logging

from web3 import Web3

from chief_keeper.spell import DSSSpell
from chief_keeper.database import SimpleDatabase

from pymaker import Address
from pymaker.deployment import DssDeployment
from pymaker.numeric import Wad

from tests.test_dss import mint_mkr



def time_travel_by(web3: Web3, seconds: int):
    assert(isinstance(web3, Web3))
    assert(isinstance(seconds, int))

    if "parity" in web3.version.node.lower():
        print(f"time travel unsupported by parity; waiting {seconds} seconds")
        time.sleep(seconds)
        # force a block mining to have a correct timestamp in latest block
        web3.eth.sendTransaction({'from': web3.eth.accounts[0], 'to': web3.eth.accounts[1], 'value': 1})
    else:
        web3.manager.request_blocking("evm_increaseTime", [seconds])
        # force a block mining to have a correct timestamp in latest block
        web3.manager.request_blocking("evm_mine", [])


def verify(addresses: List, listOrDict, leng: int):
    assert(isinstance(addresses, List))
    assert(isinstance(leng, int))

    if type(listOrDict) is list:
        assert len(listOrDict) == leng
    else:
        assert len(list(listOrDict.keys())) == leng

    for addr in addresses:
        assert addr in listOrDict


def print_out(testName: str):
    print("")
    print(f"{testName}")
    print("")

pytest.global_spell = {};

class TestSimpleDatabase:

    #TODO: Compartmentalize logic in pymaker/test_governance.py and import
    def test_setup(self, mcd: DssDeployment, our_address: Address, guy_address: Address):
        print_out("test_setup")

        # Give 1000 MKR to our_address
        amount = Wad.from_number(1000)
        mint_mkr(mcd.mkr, our_address, amount)
        assert mcd.mkr.balance_of(our_address) == amount

        #Give 2000 MKR to guy_address
        guyAmount = Wad.from_number(2000)
        mint_mkr(mcd.mkr, guy_address, guyAmount)
        assert mcd.mkr.balance_of(guy_address) == guyAmount

        # Lock MKR in DS-Chief
        assert mcd.mkr.approve(mcd.ds_chief.address).transact(from_address=our_address)
        assert mcd.mkr.approve(mcd.ds_chief.address).transact(from_address=guy_address)
        assert mcd.ds_chief.lock(amount).transact(from_address=our_address)
        assert mcd.ds_chief.lock(guyAmount).transact(from_address=guy_address)

        # Deploy spell
        self.spell = DSSSpell.deploy(mcd.web3, mcd.pause.address, mcd.vat.address)

        # Vote 1000 mkr on our address and guy_address
        # Vote 2000 mkr on global spell address
        assert mcd.ds_chief.vote_yays([our_address.address, guy_address.address]).transact(from_address=our_address)
        assert mcd.ds_chief.vote_yays([self.spell.address.address]).transact(from_address=guy_address)

        # At this point there are two yays in the chief, one to our_address and the other to the spell address

        pytest.global_spell = self.spell


    def test_unpack_slate(self, mcd: DssDeployment, simpledb: SimpleDatabase, our_address: Address, guy_address: Address):
        print_out("test_unpack_slate")

        # unpack the first etch
        etches = mcd.ds_chief.past_etch(3)
        yays = simpledb.unpack_slate(etches[0].slate, 3)
        verify([our_address.address, guy_address.address], yays, 2)


    def test_get_yays(self, mcd: DssDeployment, simpledb: SimpleDatabase, our_address: Address,  guy_address: Address):
        print_out("test_get_yays")

        yays = simpledb.get_yays(0, mcd.web3.eth.blockNumber)
        verify([our_address.address, guy_address.address, pytest.global_spell.address.address], yays, 3)


    def test_get_etas(self, mcd: DssDeployment, simpledb: SimpleDatabase, our_address: Address,  guy_address: Address):
        print_out("test_get_etas")

        block = mcd.web3.eth.blockNumber
        yays = simpledb.get_yays(0, block)
        etas = simpledb.get_etas(yays, block)

        verify([], etas, 0)


    def test_initial_query(self, mcd: DssDeployment, simpledb: SimpleDatabase, our_address: Address,  guy_address: Address):
        print_out("test_initial_query")

        simpledb.create()

        yays = simpledb.db.get(doc_id=2)["yays"]
        etas = simpledb.db.get(doc_id=3)["upcoming_etas"]

        verify([our_address.address, guy_address.address, pytest.global_spell.address.address], yays, 3)
        verify([], etas, 0)


    def test_yays_update(self, mcd: DssDeployment, simpledb: SimpleDatabase, our_address: Address,  guy_address: Address):
        print_out("test_yays_update")

        # Vote 1000 mkr on our address
        assert mcd.ds_chief.vote_yays([our_address.address]).transact(from_address=our_address)
        block = mcd.web3.eth.blockNumber

        # Updated vote should not delete yays that have had approval history
        simpledb.update_db_yays(block)
        yays = simpledb.db.get(doc_id=2)["yays"]
        DBblockNumber = simpledb.db.get(doc_id=1)["last_block_checked_for_yays"]

        verify([our_address.address, guy_address.address, pytest.global_spell.address.address], yays, 3)
        assert DBblockNumber == block


    def test_etas_update(self, mcd: DssDeployment, simpledb: SimpleDatabase, our_address: Address,  guy_address: Address):
        print_out("test_etas_update")

        assert mcd.ds_chief.lift(pytest.global_spell.address).transact(from_address=our_address)
        assert pytest.global_spell.schedule().transact(from_address=our_address)
        block = mcd.web3.eth.blockNumber

        # Although pause.delay is 0, uddate_db_etas also catches etas that can be casted on the next block
        simpledb.update_db_etas(block)
        etas = simpledb.db.get(doc_id=3)['upcoming_etas']

        verify([pytest.global_spell.address.address], etas, 1)
