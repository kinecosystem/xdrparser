"""Contains methods to decode and parse stellar's history xdr files."""

import gzip
from hashlib import sha256
import base64
from decimal import Decimal, getcontext
from typing import List, Any

from kin_base.stellarxdr import Xdr
from kin_base.stellarxdr import StellarXDR_const
from kin_base.stellarxdr.StellarXDR_type import Transaction
from kin_base import utils


# This is needed in order to calculate transaction hash.
# It is the xdr representation of XDR.const.ENVELOP_TYPE_TX (2)
PACKED_ENVELOP_TYPE = b'\x00\x00\x00\x02'

# Each asset amount is encoded as a signed 64-bit integer in the XDR structures.
# An asset amount unit (that which is seen by end users) is scaled down by a factor of ten million (10,000,000)
# to arrive at the native 64-bit integer representation.
# https://www.stellar.org/developers/guides/concepts/assets.html#amount-precision-and-representation
from kin_base.operation import ONE as AMOUNT_SCALE_FACTOR
getcontext().prec = 5


def init_unpacker(data: bytes) -> (Xdr.StellarXDRUnpacker, dict):
    """
    Initialize the stellar xdr unpacker.

    Return an unpacker with the received data as buffer
    and the relevant methods that should be used for each file type.
    https://github.com/stellar/stellar-core/blob/master/docs/history.md#individual-file-contents
    """
    unpacker = Xdr.StellarXDRUnpacker(data)
    unpacker_methods = {
        'bucket': unpacker.unpack_BucketEntry,
        'ledger': unpacker.unpack_LedgerHeaderHistoryEntry,
        'transactions': unpacker.unpack_TransactionHistoryEntry,
        'results': unpacker.unpack_TransactionHistoryResultEntry,
        'scp': unpacker.unpack_SCPHistoryEntry
    }

    return unpacker, unpacker_methods


def unpack_file(file_name: str) -> List:
    """Unpack an xdr file."""
    # xdr files are always gzipped in the archive, unzip it if the user didn't do it yet
    if file_name.endswith('.gz'):
        with gzip.open(file_name) as gzippedfile:
            data = gzippedfile.read()
    else:
        with open(file_name, 'rb') as xdr_file:
            data = xdr_file.read()

    # Get the file type from the file name
    # 'path/to/ledger-00abc53f.xdr' > 'ledger'
    # or 'path\to\ledger-00abc53f.xdr' > 'ledger on a Windows os
    file_type = file_name.split('-')[-2]
    file_type = file_type.split('\\')[-1]
    file_type = file_type.split('/')[-1]

    # Init the unpacker and get the relevant method for unpacking
    unpacker, unpacker_methods = init_unpacker(data)
    unpack_struct = unpacker_methods.get(file_type)

    parsed_structs = []

    # Ledger files should always have 64 structures in them, apart from the very first one where its 63.
    expected_ledgers = 63 if '0000003f' in file_name else 64
    current_ledger = 0
    while True:
        # Each structure in the XDR files is prefixed with the length of the structure,
        # there is no use for it for parsing the file
        try:
            _ = unpacker.unpack_uint32()
        except EOFError:
            if file_type == 'ledger' and current_ledger != expected_ledgers:
                print("ERROR: Found only {} ledgers in {}, expected {}".format(current_ledger,
                                                                               file_name, expected_ledgers))
                quit(1)
            else:
                break

        parsed_structs.append(unpack_struct())
        current_ledger += 1

    return parsed_structs


def parse(file_name: str, raw_amount: bool = False, with_hash: bool = False, network_id: str = None) -> dict:
    """Unpack and parse a file."""
    unpacked = unpack_file(file_name)

    # If 'with_hash' is set to true, go over every transaction and calculate its hash
    if with_hash:
        network_hash = sha256(bytearray(network_id, 'utf-8')).digest()
        for tx_history_entry in unpacked:
            for transaction in tx_history_entry.txSet.txs:
                transaction.hash = calculate_hash(transaction.tx, network_hash)

    # Create a json-compatible dictionary
    unpacked = todict(unpacked, raw_amount=raw_amount)

    return unpacked


def todict(obj: Any, raw_amount: bool, current_path: str = ''):
    """
    Recursively walk over an object and convert it to a dictionary.

    In addition, to make it json-compatible, parse every final value.
    """
    if hasattr(obj, '__dict__'):
        data = dict([(key, todict(value, raw_amount, current_path + '.' + key))
                     for key, value in obj.__dict__.items()])
        return data
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        return [todict(value, raw_amount, current_path + '.' + str(key)) for key, value in enumerate(obj)]
    else:
        return parse_value(obj, current_path, raw_amount)


def parse_value(value: Any, path: str, raw_amount: bool = False):
    """Parse a value to make it human-readable and json-compatible."""
    split_path = path.split('.')
    final_key = split_path[-1]
    second_to_last_key = split_path[-2]
    if isinstance(value, int):
        # Check if the value from this attribute should be parsed.
        if final_key == 'amount' or final_key == 'startingBalance':
            if not raw_amount:
                return parse_amount(value)
            return value
        if final_key == 'code':
            return parse_result_code(second_to_last_key, value)

    elif isinstance(value, (bytes, bytearray)):
        if final_key == 'ed25519':
            return parse_account(value)
        elif final_key == 'assetCode':
            return parse_asset_code(value)
        # skipList is a list of hashes in a Ledger file.
        elif 'hash' in str(final_key).lower() or second_to_last_key == 'skipList':
            return parse_hash(value)
        elif final_key == 'signature':
            return parse_signature(value)
        elif final_key == 'hint':
            return parse_hint(value)
        elif final_key == 'text':
            return parse_text(value)
        # If there is no specific way to parse this attribute, create a list from the bytes object.
        return list(value)

    # If the value is fine as it is, return it without any changes.
    return value


def parse_account(value: bytes) -> str:
    """Return the address from the address bytes."""
    return utils.encode_check('account', value).decode()


def parse_text(value: bytes) -> str:
    """Decode a byte string."""
    return value.decode()


def parse_asset_code(value: bytes) -> str:
    r"""
    Decode a byte string an remove any extra bytes.

    Example: b'KIN\x00' > 'KIN'
    """
    return value.decode().replace('\x00', '')


def parse_hash(value: bytes) -> str:
    """Return an hex representation of the hash."""
    return value.hex()


def parse_signature(value: bytes) -> str:
    """
    Return a base64 encoded signature.

    Since the signatures dont really have any representation apart from bytes,
    encode the bytes to a b64 string similar to stellar's xdr viewer.
    """
    return base64.b64encode(value).decode()


def parse_hint(value: bytes) -> str:
    """
    Return a hint for a signature.

    An address is built by:
    1. Prefix byte (0x30 - G)
    2. 32 bytes public key
    3. 2 bytes checksum

    The hint contains the last 4 bytes of the public key, so we can construct a partial address from it.
    More info: https://github.com/stellar/laboratory/blob/master/src/utilities/extrapolateFromXdr.js#L101
    """
    partial_address = utils.encode_check('account', bytes(28) + value)
    partial_address = 'G' + '_' * 46 + partial_address[46:51].decode() + '_' * 4
    return partial_address


def parse_amount(value: int) -> Decimal:
    """Return a scaled down amount."""
    return Decimal(value) / Decimal(AMOUNT_SCALE_FACTOR)


def parse_result_code(second_to_last_key, value):
    """Parse a result code"""
    # If its a transaction result
    if second_to_last_key == 'result':
        return StellarXDR_const.TransactionResultCode.get(value)

    # If its an operation result code
    try:
        # Check if the string is numeric
        int(second_to_last_key)
        return StellarXDR_const.OperationResultCode.get(value)
    except ValueError:
        # Its an specific operation type result code
        # second to last key will be the type (for example 'paymentResult')
        # so we need to get 'PaymentResultCode' from stellar_xdr_const
        enum_name = second_to_last_key[0].capitalize() + second_to_last_key[1:] + 'Code'
        status_code_dict = getattr(StellarXDR_const, enum_name)
        return status_code_dict.get(value)


def calculate_hash(transaction: Transaction, network_hash: bytes) -> bytes:
    """
    Return the hash for a transaction.

    A tx hash is a sha256 hash of:
    1. A sha256 hash of the network_id
    2. The xdr representation of ENVELOP_TYPE_TX
    3. The xdr representation of the transaction
    """
    # Pack the transaction to xdr
    packer = Xdr.StellarXDRPacker()
    packer.pack_Transaction(transaction)
    packed_tx = packer.get_buffer()

    final_hash = sha256(network_hash + PACKED_ENVELOP_TYPE + packed_tx).digest()

    return final_hash
