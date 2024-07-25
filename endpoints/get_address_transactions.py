# encoding: utf-8
import os
from enum import Enum
from fastapi import Path, Query
from pydantic import BaseModel
from sqlalchemy import text, func
from sqlalchemy.future import select
from typing import List

from constants import ADDRESS_EXAMPLE, REGEX_COINSEC_ADDRESS
from dbsession import async_session
from endpoints import sql_db_only
from endpoints.get_transactions import search_for_transactions, TxSearch, TxModel
from models.TxAddrMapping import TxAddrMapping
from server import app

DESC_RESOLVE_PARAM = "Use this parameter if you want to fetch the TransactionInput previous outpoint details." \
                     " Light fetches only the address and amount. Full fetches the whole TransactionOutput and " \
                     "adds it into each TxInput."


class TransactionsReceivedAndSpent(BaseModel):
    tx_received: str
    tx_spent: str | None
    # received_amount: int = 38240000000


class TransactionForAddressResponse(BaseModel):
    transactions: List[TransactionsReceivedAndSpent]


class TransactionCount(BaseModel):
    total: int


class PreviousOutpointLookupMode(str, Enum):
    no = "no"
    light = "light"
    full = "full"


@app.get("/addresses/{coinsecAddress}/transactions",
         response_model=TransactionForAddressResponse,
         response_model_exclude_unset=True,
         tags=["Coinsec addresses"],
         deprecated=True)
@sql_db_only
async def get_transactions_for_address(
        coinsecAddress: str = Path(
            description=f"Coinsec address as string e.g. {ADDRESS_EXAMPLE}",
            regex=REGEX_COINSEC_ADDRESS)):
    """
    Get all transactions for a given address from database
    """
    # SELECT transactions_outputs.transaction_id, transactions_inputs.transaction_id as inp_transaction FROM transactions_outputs
    #
    # LEFT JOIN transactions_inputs ON transactions_inputs.previous_outpoint_hash = transactions_outputs.transaction_id AND transactions_inputs.previous_outpoint_index::int = transactions_outputs.index
    #
    # WHERE "script_public_key_address" = 'coinsec:qp7d7rzrj34s2k3qlxmguuerfh2qmjafc399lj6606fc7s69l84h7mrj49hu6'
    #
    # ORDER by transactions_outputs.transaction_id
    async with async_session() as session:
        resp = await session.execute(text(f"""
            SELECT transactions_outputs.transaction_id, transactions_outputs.index, transactions_inputs.transaction_id as inp_transaction,
                    transactions.block_time, transactions.transaction_id
            
            FROM transactions
			LEFT JOIN transactions_outputs ON transactions.transaction_id = transactions_outputs.transaction_id
			LEFT JOIN transactions_inputs ON transactions_inputs.previous_outpoint_hash = transactions.transaction_id AND transactions_inputs.previous_outpoint_index = transactions_outputs.index
            WHERE "script_public_key_address" = :coinsecAddress
			ORDER by transactions.block_time DESC
			LIMIT 500"""),
                                     {'coinsecAddress': coinsecAddress})

        resp = resp.all()

    # build response
    tx_list = []
    for x in resp:
        tx_list.append({"tx_received": x[0],
                        "tx_spent": x[2]})
    return {
        "transactions": tx_list
    }


@app.get("/addresses/{coinsecAddress}/full-transactions",
         response_model=List[TxModel],
         response_model_exclude_unset=True,
         tags=["Coinsec addresses"])
@sql_db_only
async def get_full_transactions_for_address(
        coinsecAddress: str = Path(
            description="Coinsec address as string e.g. "
                        f"{ADDRESS_EXAMPLE}",
            regex=REGEX_COINSEC_ADDRESS),
        limit: int = Query(
            description="The number of records to get",
            ge=1,
            le=500,
            default=50),
        offset: int = Query(
            description="The offset from which to get records",
            ge=0,
            default=0),
        fields: str = "",
        resolve_previous_outpoints: PreviousOutpointLookupMode =
        Query(default="no",
              description=DESC_RESOLVE_PARAM)):
    """
    Get all transactions for a given address from database.
    And then get their related full transaction data
    """

    async with async_session() as s:
        # Doing it this way as opposed to adding it directly in the IN clause
        # so I can re-use the same result in tx_list, TxInput and TxOutput
        tx_within_limit_offset = await s.execute(select(TxAddrMapping.transaction_id)
                                                 .filter(TxAddrMapping.address == coinsecAddress)
                                                 .limit(limit)
                                                 .offset(offset)
                                                 .order_by(TxAddrMapping.block_time.desc())
                                                 )

        tx_ids_in_page = [x[0] for x in tx_within_limit_offset.all()]

    return await search_for_transactions(TxSearch(transactionIds=tx_ids_in_page),
                                         fields,
                                         resolve_previous_outpoints)


@app.get("/addresses/{coinsecAddress}/transactions-count",
         response_model=TransactionCount,
         tags=["Coinsec addresses"])
@sql_db_only
async def get_transaction_count_for_address(
        coinsecAddress: str = Path(
            description="Coinsec address as string e.g. "
                        f"{ADDRESS_EXAMPLE}",
            regex=REGEX_COINSEC_ADDRESS)
):
    """
    Count the number of transactions associated with this address
    """

    async with async_session() as s:
        count_query = select(func.count()).filter(TxAddrMapping.address == coinsecAddress)

        tx_count = await s.execute(count_query)

    return TransactionCount(total=tx_count.scalar())
