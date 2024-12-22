from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

import pandas as pd
from adalflow.core import DataClass
from pydantic import BaseModel

from dystopic_investment_aigents.agents.base_agents.agent_base import Agent
from dystopic_investment_aigents.agents.base_agents.fund_manager_base import (
    FundDirective,
)


class AssetType(Enum):
    STOCK = auto()
    BOND = auto()
    COMMODITY = auto()
    CRYPTOCURRENCY = auto()
    REAL_ESTATE = auto()
    ETF = auto()
    MUTUAL_FUND = auto()
    DERIVATIVE = auto()


class Asset(BaseModel):
    name: str
    type: AssetType

    model_config = {"frozen": True}


class Portfolio(BaseModel):
    allocation: dict[Asset, float]

    model_config = {"arbitrary_types_allowed": True}

    def to_df(self) -> pd.DataFrame:
        data = []
        for asset, weight in self.allocation.items():
            data.append(
                {"asset_name": asset.name, "asset_type": asset.type, "weight": weight}
            )
        return pd.DataFrame(data)


@dataclass
class Operations(DataClass):
    # buy: dict[Asset, float]
    # sell: dict[Asset, float]
    final_portfolio: Portfolio
    # intial_portfolio: Portfolio | None = None # not super needed, just seems to work a bit better


class QuantTraderBase(ABC, Agent):
    model_config = {"arbitrary_types_allowed": True}

    @abstractmethod
    def operate(
        self,
        fund_directive: FundDirective | None = None,
        past_portfolio: Portfolio | None = None,
    ) -> Operations: ...
