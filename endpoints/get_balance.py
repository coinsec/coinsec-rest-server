# encoding: utf-8
from fastapi import Path, HTTPException
from pydantic import BaseModel

from constants import ADDRESS_EXAMPLE, REGEX_COINSEC_ADDRESS
from server import app, coinsecd_client


class BalanceResponse(BaseModel):
    address: str = ADDRESS_EXAMPLE
    balance: int = 38240000000


@app.get("/addresses/{coinsecAddress}/balance", response_model=BalanceResponse, tags=["Coinsec addresses"])
async def get_balance_from_coinsec_address(
        coinsecAddress: str = Path(
            description=f"Coinsec address as string e.g. {ADDRESS_EXAMPLE}",
            regex=REGEX_COINSEC_ADDRESS)):
    """
    Get balance for a given coinsec address
    """
    resp = await coinsecd_client.request("getBalanceByAddressRequest",
                                       params={
                                           "address": coinsecAddress
                                       })

    try:
        resp = resp["getBalanceByAddressResponse"]
    except KeyError:
        if "getUtxosByAddressesResponse" in resp and "error" in resp["getUtxosByAddressesResponse"]:
            raise HTTPException(status_code=400, detail=resp["getUtxosByAddressesResponse"]["error"])
        else:
            raise

    try:
        balance = int(resp["balance"])

    # return 0 if address is ok, but no utxos there
    except KeyError:
        balance = 0

    return {
        "address": coinsecAddress,
        "balance": balance
    }
