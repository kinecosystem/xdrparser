import pytest
from decimal import Decimal\

FILE_LOCATION = './transactions-0043733f.xdr.gz'


@pytest.fixture('session')
def xdr_data():
    with open(FILE_LOCATION, 'rb') as f:
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
    unpacked = unpack_file(FILE_LOCATION)
    assert len(unpacked) == 64


def test_parse():
    from xdrparser.parser import parse
    parse(FILE_LOCATION)


def test_parse_with_hash():
    from xdrparser.parser import parse
    parse(FILE_LOCATION, with_hash=True, network_id='test')


def test_todict():
    from kin_base.stellarxdr.StellarXDR_type import PublicKey
    from kin_base.stellarxdr.StellarXDR_const import PUBLIC_KEY_TYPE_ED25519
    from xdrparser.parser import todict

    public_key = PublicKey(type=PUBLIC_KEY_TYPE_ED25519,
                           ed25519=b'\x0e\xb4\xc8\x9e$1\r\xdc\x9e\xa0(kH?\xfar\xd5}A\xa7$\x84"\xdcn4`j\xbdc\t^')
    expected_value = {'type': 0, 'ed25519': 'GAHLJSE6EQYQ3XE6UAUGWSB77JZNK7KBU4SIIIW4NY2GA2V5MMEV4LRB'}

    assert todict(public_key, False) == expected_value


def test_parse_value_int_starting_balance_raw_amount():
    from xdrparser.parser import parse_value
    assert parse_value(20000000, '.0.txSet.txs.0.tx.operations.0.body.createAccountOp.startingBalance',
                       True) == 20000000


def test_parse_value_int_starting_balance_default():
    from xdrparser.parser import parse_value
    assert parse_value(20000000, '.0.txSet.txs.0.tx.operations.0.body.createAccountOp.startingBalance') == Decimal(200)


def test_parse_value_int_starting_balance_not_raw_amount():
    from xdrparser.parser import parse_value
    assert parse_value(20000000, '.0.txSet.txs.0.tx.operations.0.body.createAccountOp.startingBalance',
                       False) == Decimal(200)


def test_parse_value_int_starting_balance_less_than_1():
    from xdrparser.parser import parse_value
    assert parse_value(200, '.0.txSet.txs.0.tx.operations.0.body.createAccountOp.startingBalance') == \
           Decimal((0, (0, 0, 2), -3))


def test_parse_value_int_payment_amount_default():
    from xdrparser.parser import parse_value
    assert parse_value(60000000, '.0.txSet.txs.8.tx.operations.0.body.paymentOp.amount') == Decimal(600)


def test_parse_value_int_other():
    from xdrparser.parser import parse_value
    assert parse_value(1000000, '.0.ledgerSeq') == 1000000


def test_parse_value_bytes_text_final_key():
    from xdrparser.parser import parse_value
    assert parse_value(b'1-kik', '.0.txSet.txs.0.tx.memo.text') == '1-kik'


def test_parse_value_regular_bytes_hash():
    from xdrparser.parser import parse_value
    bytes_value = b'\x1cM\xa7~\xb28\x9f%\x04G~n\xfa\x80\xcd\x1b0T\xae\xe3>\xb6\xa4\xa3\x96\xb6\xfdJ\xbb(s\xb2'
    expected_result = '1c4da77eb2389f2504477e6efa80cd1b3054aee33eb6a4a396b6fd4abb2873b2'
    assert parse_value(bytes_value, '.0.txSet.previousLedgerHash') == expected_result


def test_parse_value_bytes_account():
    from xdrparser.parser import parse_value
    bytes_value = b'\x0e\xb4\xc8\x9e$1\r\xdc\x9e\xa0(kH?\xfar\xd5}A\xa7$\x84"\xdcn4`j\xbdc\t^'
    expected_result = 'GAHLJSE6EQYQ3XE6UAUGWSB77JZNK7KBU4SIIIW4NY2GA2V5MMEV4LRB'
    assert parse_value(bytes_value, '.0.txSet.txs.0.tx.sourceAccount.ed25519') == expected_result


def test_parse_value_bytes_hint():
    from xdrparser.parser import parse_value
    expected_result = 'G______________________________________________F5MME____'
    assert parse_value(b'\xbdc\t^', '.0.txSet.txs.0.signatures.0.hint') == expected_result


def test_parse_value_bytes_signature():
    from xdrparser.parser import parse_value
    signature = b'r\xc9\xd5\x8d\x16\x9c\x0e\t&\xf97\x08\xa8\x98i\xc4\x95\xab\xaf\xbc\x82Q\xad\xef,\x1d\xf2\xd2mS\xbau\x07\xd1\xacw\x97\xee-\xeb\x96\xc8\xaaX\x13\x87Zb\xc2\xc02i\xd1\x82\xd9\x00c\x90-Q\xc2l\xa3\n'
    expected_result = 'csnVjRacDgkm+TcIqJhpxJWrr7yCUa3vLB3y0m1TunUH0ax3l+4t65bIqlgTh1piwsAyadGC2QBjkC1RwmyjCg=='
    assert parse_value(signature, '.0.txSet.txs.0.signatures.0.signature') == expected_result


def test_parse_account():
    from xdrparser.parser import parse_account
    assert parse_account(b'\x0e\xb4\xc8\x9e$1\r\xdc\x9e\xa0(kH?\xfar\xd5}A\xa7$\x84"\xdcn4`j\xbdc\t^') == \
           'GAHLJSE6EQYQ3XE6UAUGWSB77JZNK7KBU4SIIIW4NY2GA2V5MMEV4LRB'
    return 0


def test_parse_text():
    from xdrparser.parser import parse_text
    assert parse_text(b'1-kik') == '1-kik'


def test_parse_asset_code():
    from xdrparser.parser import parse_asset_code
    assert parse_asset_code(b'KIN') == 'KIN'


def test_parse_asset_code_remove_extra_bytes():
    from xdrparser.parser import parse_asset_code
    assert parse_asset_code(b'KIN\x00') == 'KIN'


def test_parse_hash():
    from xdrparser.parser import parse_hash
    bytes_hash = b'\x1cM\xa7~\xb28\x9f%\x04G~n\xfa\x80\xcd\x1b0T\xae\xe3>\xb6\xa4\xa3\x96\xb6\xfdJ\xbb(s\xb2'
    assert parse_hash(bytes_hash) == '1c4da77eb2389f2504477e6efa80cd1b3054aee33eb6a4a396b6fd4abb2873b2'


def test_parse_signature():
    from xdrparser.parser import parse_signature
    signature = b'r\xc9\xd5\x8d\x16\x9c\x0e\t&\xf97\x08\xa8\x98i\xc4\x95\xab\xaf\xbc\x82Q\xad\xef,\x1d\xf2\xd2mS\xbau\x07\xd1\xacw\x97\xee-\xeb\x96\xc8\xaaX\x13\x87Zb\xc2\xc02i\xd1\x82\xd9\x00c\x90-Q\xc2l\xa3\n'
    expected_result = 'csnVjRacDgkm+TcIqJhpxJWrr7yCUa3vLB3y0m1TunUH0ax3l+4t65bIqlgTh1piwsAyadGC2QBjkC1RwmyjCg=='
    assert parse_signature(signature) == expected_result


def test_parse_hint():
    from xdrparser.parser import parse_hint
    assert parse_hint(b'\xbdc\t^') == 'G______________________________________________F5MME____'


def test_parse_amount_less_than_1():
    from xdrparser.parser import parse_amount
    assert parse_amount(200) == Decimal((0, (0, 0, 2), -3))


def test_parse_amount_bigger_than_1():
    from xdrparser.parser import parse_amount
    assert parse_amount(60000000) == Decimal(600)


def test_calculate_hash():
    from xdrparser.parser import calculate_hash
    from kin_base.stellarxdr.StellarXDR_type import Transaction, Operation, Memo, PublicKey, CreateAccountOp, \
        ChangeTrustOp, Asset
    from kin_base.stellarxdr.StellarXDR_const import MEMO_TEXT, PUBLIC_KEY_TYPE_ED25519, ASSET_TYPE_CREDIT_ALPHANUM4

    alpha_num4 = type('', (object,), {
        'assetCode': b'KIN\x00',
        'issuer': PublicKey(type=PUBLIC_KEY_TYPE_ED25519,
                            ed25519=b'\xcb\xcd3hy#\x01\x05v)2\xa8E_\xfaa\xee\xc8J\x9d6+o\xc7\xcdE\x7f\xde\xfd\x07a|')
    })

    operation_1_body = type('', (CreateAccountOp,), {
        'createAccountOp': CreateAccountOp(
            destination=PublicKey(type=PUBLIC_KEY_TYPE_ED25519,
                                  ed25519=b'\xc1\x99\xba\x90\xa6z\x14\x08v\x19^HA_\xf3\xd38\x07\x91\xc8E\xf1a\xbd\x11l\x83\x17\xb6m\xc0\x9e'),
            startingBalance=20000000),
        'type': 0
    })

    operation_2_body = type('', (ChangeTrustOp,), {'changeTrustOp': ChangeTrustOp(
        line=Asset(type=ASSET_TYPE_CREDIT_ALPHANUM4, alphaNum4=alpha_num4),
        limit=9223372000000000000),
        'type': 6})

    transaction = Transaction(
        sourceAccount=PublicKey(type=PUBLIC_KEY_TYPE_ED25519,
                                ed25519=b'\x0e\xb4\xc8\x9e$1\r\xdc\x9e\xa0(kH?\xfar\xd5}A\xa7$\x84"\xdcn4`j\xbdc\t^'),
        fee=200, seqNum=10991388246171497, timeBounds=[],
        memo=Memo(type=MEMO_TEXT, text=b'1-kik'), operations=[
            Operation(
                sourceAccount=[PublicKey(type=PUBLIC_KEY_TYPE_ED25519,
                                         ed25519=b'\xda\x98\xa3\xbb\x18\x1d\xed\xa6\xf0&\x84\xe7\xd0d\xd8v\x1fW\xa62\x10bv\x04\xe5s\x0c\xf6Z!\xeev')],
                body=operation_1_body),
            Operation(
                sourceAccount=[PublicKey(type=PUBLIC_KEY_TYPE_ED25519,
                                         ed25519=b'\xc1\x99\xba\x90\xa6z\x14\x08v\x19^HA_\xf3\xd38\x07\x91\xc8E\xf1a\xbd\x11l\x83\x17\xb6m\xc0\x9e')],
                body=operation_2_body)], ext=type('', (object,), {'v': 0})
    )

    network_hash = b'\x9f\x86\xd0\x81\x88L}e\x9a/\xea\xa0\xc5Z\xd0\x15\xa3\xbfO\x1b+\x0b\x82,\xd1]l\x15\xb0\xf0\n\x08'

    expected_result = b'*\xf3\x8d\xcf\xca\x10L\x82g\xe6\x0b\x08\x9b-\x17\x12\xf4W3\x99f\x1b\xeb\xd2\x06\x0cb\x04\x97\xf0\xee\xa9'
    assert calculate_hash(transaction, network_hash) == expected_result
