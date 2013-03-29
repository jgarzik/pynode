#!/usr/bin/python
#
# q_avg_size.py
#
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
#


import sys
import Log
import MemPool
import ChainDb
import cStringIO
import struct

from bitcoin.coredefs import NETWORKS
from bitcoin.core import CBlock
from bitcoin.scripteval import *

NET_SETTINGS = {
	'mainnet' : {
		'log' : '/spare/tmp/q_avg_size.log',
		'db' : '/spare/tmp/chaindb'
	},
	'testnet3' : {
		'log' : '/spare/tmp/q_avg_sizetest.log',
		'db' : '/spare/tmp/chaintest'
	}
}

MY_NETWORK = 'mainnet'

SETTINGS = NET_SETTINGS[MY_NETWORK]

log = Log.Log(SETTINGS['log'])
mempool = MemPool.MemPool(log)
netmagic = NETWORKS[MY_NETWORK]
chaindb = ChainDb.ChainDb(SETTINGS, SETTINGS['db'], log, mempool, netmagic,
			  True)

outf = open('bootstrap.dat', 'wb')

scanned = 0
failures = 0

n_sizes = 0
size_total = 0

for height in xrange(chaindb.getheight()+1):
	if height < 200000:
		continue

	heightidx = ChainDb.HeightIdx()
	heightstr = str(height)
	try:
		heightidx.deserialize(chaindb.db.Get('height:'+heightstr))
	except KeyError:
		log.write("Height " + str(height) + " not found.")
		continue

	blkhash = heightidx.blocks[0]

	block = chaindb.getblock(blkhash)

	byte_size = 80 + (len(block.vtx) * 32)
	n_sizes += 1
	size_total += byte_size

	scanned += 1
	if (scanned % 1000) == 0:
		log.write("Scanned height %d (%d failures)" % (
			height, failures))

log.write("Scanned %d blocks (%d failures)" % (scanned, failures))

avg_size = 1.0 * size_total / n_sizes

log.write("Average block summary size: %.2f" % (avg_size,))

