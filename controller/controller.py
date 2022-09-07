from fastapi import APIRouter
from service_core.config.load_configuration import ConfigurationLoader
from controller.models import TextInput,DiscountCashFlowInput
from controller.models import LoadDataOutput,DiscountCashFlowOutput

from engine.analysis_engine import AnalysisEngine

configuration = ConfigurationLoader.load("settings/config.yaml")
router = APIRouter(prefix=configuration.core.server.prefix)

@router.post("/load_data/", tags=["load data"],response_model=LoadDataOutput)
async def load_data(ticker:TextInput):
    engine = AnalysisEngine(ticker=ticker.ticker)
    engine.parse()
    engine.prepare_data()
    engine.growth_analysis()
    response = {"text":"Done"}
    return response


@router.post("/discount_cash_flow/",response_model=DiscountCashFlowOutput)
async def discount_cash_flow(dco:DiscountCashFlowInput):
    engine = AnalysisEngine(ticker=dco.ticker)
    engine.parse()
    engine.prepare_data()
    engine.growth_analysis()
    engine.discounted_cash_flow_analysis(years=10, discount_rate=dco.discount_rate, terminal_value=dco.terminal_value,
                                         perpetuity_growth=dco.perpetuity_growth,
                                         revenue_growth_rate=dco.revenue_growth_rate, fcf_margin=dco.fcf_margin, net_margin=dco.net_margin
                                         )
    response = {"text":"dfddj"}
    return response