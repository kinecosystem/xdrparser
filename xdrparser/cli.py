"""Command line tool to parse Kin's xdr history files."""
import json
import re
from decimal import Decimal

import click

from xdrparser import parser


class DecimalEncoder(json.JSONEncoder):
    """
    Json encoder that encodes Decimals as strings
    """
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


@click.command()
@click.argument('xdr_file')
@click.option('--with-hash', is_flag=True, help="Calculate tx hashes, only for a 'transactions' xdr file,"
                                                " must be used with --network-id")
@click.option('--network-id', default=None, help="Network-id/network paraphrase, needed for --with-hash")
@click.option('--indent', default=2, help='Number of spaces to indent the json output with')
@click.option('--raw-amount', is_flag=True, help='Should the amount be shown in stroops')
def main(xdr_file, raw_amount, with_hash, network_id, indent):
    """Command line tool to parse Stellar's xdr history files."""
    verify_input(xdr_file, with_hash, network_id)

    # Parse and print the file
    data = parser.parse(xdr_file, raw_amount=raw_amount, with_hash=with_hash, network_id=network_id)
    print(json.dumps(data, indent=indent, cls=DecimalEncoder))


def verify_input(xdr_file, with_hash, network_id):
    """Validate that the input is ok."""
    if with_hash and network_id is None:
        print('Cannot use --with-hash without --network-id.')
        quit(1)

    file_name = xdr_file.split('\\')[-1]
    file_name = file_name.split('/')[-1]

    if re.fullmatch('^(transactions|results|scp|ledger)(-[0-9a-fA-F]{8}.)(xdr|xdr.gz)$', file_name) is None \
            and re.fullmatch('^(bucket-)([0-9a-fA-F]{64}.)(xdr|xdr.gz)$', file_name) is None:
        print('Invalid history archive file name')
        quit(1)

    if with_hash and file_name.split('-')[0] != 'transactions':
        print('--with-hash can only be used with a transactions file')
        quit(1)
