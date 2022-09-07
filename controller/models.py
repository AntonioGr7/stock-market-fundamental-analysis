from enum import Enum
from typing import Generic, List, Optional
from pydantic import BaseModel


class TextInput(BaseModel):
    ticker: str

class LoadDataOutput(BaseModel):
    text: str

class DiscountCashFlowInput(BaseModel):
    ticker: str
    years: int
    discount_rate: float
    terminal_value: float
    perpetuity_growth: float
    revenue_growth_rate: List[float]
    fcf_margin: float
    net_margin: float


class DiscountCashFlowOutput(BaseModel):
    years: int
    discount_rate : float
    terminal_value : float
    perpetuity_growth : float
    revenue_growth_rate: List[float]
    fcf_margin : float
    net_margin = float


class TokensSentiment(BaseModel):
    sentence: str
    sentiment:int

class SentimentTaggerOutput(BaseModel):
    tokens: List[str]
    sentiment: List[int]
    tokens_sentiment: List[TokensSentiment]

class PolarityObject(BaseModel):
    tokens: List[str]
    polarity: List[int]

class FeelProbeOutput(BaseModel):
    sentence: str
    sentiment: int
    topics: List[str]
    polarity:PolarityObject

class ServiceOutput(BaseModel):
    feel_probe: List[FeelProbeOutput]



