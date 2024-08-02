# encoding: utf-8
from typing import List

from pydantic import BaseModel

from server import app, coinsecd_client


class NetworkResponse(BaseModel):
    networkName: str = "coinsec-testnet-10"
    blockCount: str = "1028"
    headerCount: str = "1028"
    tipHashes: List[str] = [
        "84a9d698f28035defeb2796c53af88bc7cc2f0d732abf1c8b44570f471daa2f6"
    ]
    difficulty: float = 65536.01
    pastMedianTime: str = "1722579749081"
    virtualParentHashes: List[str] = [
        "84a9d698f28035defeb2796c53af88bc7cc2f0d732abf1c8b44570f471daa2f6"
    ]
    pruningPointHash: str = "f896a3034873be1739fc4359236899fd3d65d2bc94f9780df0d0da3eb1cc4370"
    virtualDaaScore: str = "1027"


@app.get("/info/network", response_model=NetworkResponse, tags=["Coinsec network info"])
async def get_network():
    """
    Get some global coinsec network information
    """
    resp = await coinsecd_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]
