import os

NETWORK_TYPE = os.getenv('NETWORK_TYPE', 'testnet').lower()

match NETWORK_TYPE:
    case "mainnet":
        address_prefix = "coinsec"
        address_example = "coinsec:qqkqkzjvr7zwxxmjxjkmxxdwju9kjs6e9u82uh59z07vgaks6gg62v8707g73"
    case "testnet":
        address_prefix = "coinsectest"
        address_example = "coinsectest:qpqz2vxj23kvh0m73ta2jjn2u4cv4tlufqns2eap8mxyyt0rvrxy6ejkful67"
    case "simnet":
        address_prefix = "coinsecsim"
        address_example = "coinsecsim:qpqz2vxj23kvh0m73ta2jjn2u4cv4tlufqns2eap8mxyyt0rvrxy6ejkful67"
    case "devnet":
        address_prefix = "coinsecdev"
        address_example = "coinsecdev:qpqz2vxj23kvh0m73ta2jjn2u4cv4tlufqns2eap8mxyyt0rvrxy6ejkful67"
    case _:
        raise ValueError(f'Network type {NETWORK_TYPE} not supported.')

ADDRESS_PREFIX = address_prefix
ADDRESS_EXAMPLE = address_example

REGEX_COINSEC_ADDRESS = "^" + ADDRESS_PREFIX + ":[a-z0-9]{61,63}$"
