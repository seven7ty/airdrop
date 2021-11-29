import re

ETH_ADDRESS_RE: re.Pattern = re.compile(r'^(?P<prefix>0x)?(?P<actual>[0-9a-fA-F]){40}$')
