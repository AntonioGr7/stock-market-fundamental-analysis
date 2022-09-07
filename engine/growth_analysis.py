import math
import numpy as np

class GrowthAnalysis:
    def __init__(self,data):
        self.data = data

    def growth_utils(self, values):
        values = [v if v is not None else math.nan for v in values]
        values = [v for v in values if not math.isnan(v)]
        if len(values)==0:
            return float('nan')
        return sum(values) / len(values)

    def __calculate_growth__(self, field, years):
        data = self.data.loc[field][::-1][1:years + 1]
        gr = []
        for i in range(len(data)):
            if i + 1 < len(data):
                gr.append((data[i] - data[i + 1]) / data[i + 1])
        return gr[::-1]

    def past_years_growth(self,years=[1,3,5,10]):
        revenue_gr = self.data.income.revenueGrowth[1:]
        if all([r is None or math.isnan(r) for r in revenue_gr]):
            revenue_gr = self.__calculate_growth__("Revenue",3)
        fcf_gr = self.data.cf.fcfGrowth[1:]
        #ebita_gr = self.data.income.epsGrowth[1:]
        net_income_growth = self.data.income.netIncomeGrowth[1:]
        eps_gr = self.data.income.epsGrowth[1:]
        so_gr = self.data.income.sharesYoY[1:]
        if all([r is None or math.isnan(r) for r in so_gr]):
            so_gr = self.__calculate_growth__("Shares Out",3)
        fcf_margin = self.data.income.fcfMargin[1:]
        ebitda_margin = self.data.income.ebitdaMargin[1:]
        net_margin = self.data.income.profitMargin[1:]
        pe_ratio = self.data.ratio.pe[1:]
        results = {}
        for y in years:
            results[str(y)+"Y"] = {
                "Revenue Growth":self.growth_utils(revenue_gr[0:y]),
                "FCF Growth":self.growth_utils(fcf_gr[0:y]),
                #"EBT Growth":self.growth_utils(ebitda_gr[::-1][0:y]),
                "Net Income Growth":self.growth_utils(net_income_growth[0:y]),
                "EPS Growth":self.growth_utils(eps_gr[0:y]) ,
                "Shares Out Growth":self.growth_utils(so_gr[0:y]),
                "FCF Margin Average":self.growth_utils(fcf_margin[0:y]),
                "EBITDA Margin Average":self.growth_utils(ebitda_margin[0:y]),
                "Net Margin Average":self.growth_utils(net_margin[0:y]),
                "PE Ratio Average":self.growth_utils(pe_ratio[0:y])
            }
        return results