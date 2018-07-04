# xdrparser
Command line tool to parse the .xdr files written to the history archive of a stellar-core and print their data as json.


## Compatibility
* Python >= 3.4
* Tested on Linux and Mac OS, should work on Windows as well.

## Installation

### From PyPI:
1. Edit this when its up

### From the repository:
1. Clone the repository
2. Use ```pip install .```

## Usage
```
$ xdrparser --help

Usage: xdrparser [OPTIONS] XDR_FILE

  Command line tool to parse Stellar's xdr history files.

Options:
  --with-hash        Calculate tx hashes, only for a 'transactions' xdr file,
                     must be used with --network-id
  --network-id TEXT  Network-id/network paraphrase, needed for --with-hash
  --indent INTEGER   Number of spaces to indent the json output with
  --help             Show this message and exit.

```
