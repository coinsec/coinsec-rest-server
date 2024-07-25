# encoding: utf-8

from pydantic import BaseModel
from starlette.responses import PlainTextResponse

from endpoints import mainnet_only
from helper import get_sec_price, get_sec_market_data
from server import app


class PriceResponse(BaseModel):
    price: float = 0.025235


@app.get("/info/price", response_model=PriceResponse | str, tags=["Coinsec network info"])
@mainnet_only
async def get_price(stringOnly: bool = False):
    """
    Returns the current price for Coinsec in USD.
    """
    if stringOnly:
        return PlainTextResponse(content=str(await get_sec_price()))

    return {"price": await get_sec_price()}


@app.get("/info/market-data",
         tags=["Coinsec network info"],
         include_in_schema=False)
@mainnet_only
async def get_market_data():
    """
    Returns market data for coinsec.
    """
    return await get_sec_market_data()
