#!/usr/bin/python
#
# mkbootstrap.py
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
import argparse

from bitcoin.coredefs import NETWORKS
from bitcoin.core import CBlock
from bitcoin.scripteval import *

NET_SETTINGS = {
	'mainnet' : {
		'log' : '/spare/tmp/mkbootstrap.log',
		'db' : '/spare/tmp/chaindb'
	},
	'testnet3' : {
		'log' : '/spare/tmp/mkbootstraptest.log',
		'db' : '/spare/tmp/chaintest'
	}
}

MY_NETWORK = 'mainnet'

SETTINGS = NET_SETTINGS[MY_NETWORK]

opts = argparse.ArgumentParser(description='Create blockchain datafile')
opts.add_argument('--latest', dest='latest', action='store_true')

args = opts.parse_args()

# to log to a file
# log = Log.Log(SETTINGS['log'])

# stdout logging
log = Log.Log()

mempool = MemPool.MemPool(log)
netmagic = NETWORKS[MY_NETWORK]
chaindb = ChainDb.ChainDb(SETTINGS, SETTINGS['db'], log, mempool, netmagic,
			  True)

if args.latest:
	scan_height = chaindb.getheight()
else:
	scan_height = 216116
	
out_fn = 'bootstrap.dat'
log.write("Outputting to %s, up to height %d" % (out_fn, scan_height))

outf = open(out_fn, 'wb')

scanned = 0
failures = 0

for height in xrange(scan_height+1):
	heightidx = ChainDb.HeightIdx()
	heightstr = str(height)
	try:
		heightidx.deserialize(chaindb.db.Get('height:'+heightstr))
	except KeyError:
		log.write("Height " + str(height) + " not found.")
		continue

	blkhash = heightidx.blocks[0]

	block = chaindb.getblock(blkhash)

	ser_block = block.serialize()

	outhdr = netmagic.msg_start
	outhdr += struct.pack("<i", len(ser_block))

	outf.write(outhdr)
	outf.write(ser_block)

	scanned += 1
	if (scanned % 1000) == 0:
		log.write("Scanned height %d (%d failures)" % (
			height, failures))

log.write("Scanned %d blocks (%d failures)" % (scanned, failures))

