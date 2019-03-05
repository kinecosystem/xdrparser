import pytest


@pytest.fixture('session')
def xdr_data():
    with open('tests/transactions-0043733f.xdr.gz', 'rb') as f:
        data = f.read()
    return data


def test_init_unpacker(xdr_data):
    from xdrparser.parser import init_unpacker
    unpacker, methods = init_unpacker(xdr_data)
    assert len(unpacker._Unpacker__buf) == 414129
    for xdr_type in ['bucket', 'ledger', 'transactions', 'results', 'scp']:
        assert xdr_type in methods


def test_unpack_file():
    from xdrparser.parser import unpack_file
    unpacked = unpack_file('tests/transactions-0043733f.xdr.gz')
    assert len(unpacked) == 64
