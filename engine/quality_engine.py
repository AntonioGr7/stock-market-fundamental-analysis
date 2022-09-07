


class QualityEngine:
    def __init__(self,data,debt_information,growth_information,general_information):
        self.data = data
        self.debt_information = debt_information
        self.growth_information = growth_information
        self.general_information = general_information

    def quality_valuation(self):
        quality_check = {}
        # current ratio >1.2
        cr = self.debt_information['Current Ratio'][::-1].tolist()[0]
        if cr >= 1.2:
            valuation = True
        else:
            valuation = False
        quality_check['Current Ratio'] = {"value": cr,"reference": 1.2,"valuation": valuation}
        ### Quick Ratio > 1
        qr = self.debt_information['Quick Ratio'][::-1].tolist()[0]
        if cr >= 1:
            valuation = True
        else:
            valuation = False
        quality_check['Quick Ratio'] = {"value": qr,"reference": 1,"valuation": valuation}
        ## Debto to equity <2
        dte = self.debt_information['Debt to Equity'][::-1].tolist()[0]
        if dte < 2:
            valuation = True
        else:
            valuation = False
        quality_check['Debt to Equity'] = {"value": dte, "reference": 2,"valuation": valuation}
        ###################### average 5Y roic > 9%
        roic_avg = sum(self.data.loc['ROIC'][::-1][0:5]) / len(self.data.loc['ROIC'][::-1][0:5])
        if roic_avg >= 9:
            valuation = True
        else:
            valuation = False
        quality_check['ROIC AVG 5Y'] = {"value": roic_avg,"reference": 9, "valuation": valuation}

        ########### average 5Y ROA > 10%
        roa_avg = sum(self.data.loc['ROA'][::-1][0:5]) / len(self.data.loc['ROA'][::-1][0:5])
        if roa_avg >= 9:
            valuation = True
        else:
            valuation = False
        quality_check['ROA AVG 5Y'] = {"value": roa_avg,"reference": 9,"valuation": valuation}

        ########### revenue growth 5Y > 0
        revenue_growth_avg_5y = self.growth_information.loc['Revenue Growth']['5Y']
        if revenue_growth_avg_5y > 0:
            valuation = True
        else:
            valuation = False
        quality_check['Revenue Growth AVG 5Y'] = {"value": revenue_growth_avg_5y, "reference": 0,"valuation": valuation}
        ########### net income growth > 0
        net_income_growth_avg_5y = self.growth_information.loc['Net Income Growth']['5Y']
        if net_income_growth_avg_5y > 0:
            valuation = True
        else:
            valuation = False
        quality_check['Net Income Growth AVG 5Y'] = {"value": net_income_growth_avg_5y,"reference":0, "valuation": valuation}
        ########### cash flow growth > 0
        fcf_growth_avg_5y = self.growth_information.loc['FCF Growth']['5Y']
        if fcf_growth_avg_5y > 0:
            valuation = True
        else:
            valuation = False
        quality_check['FCF Growth AVG 5Y'] = {"value": fcf_growth_avg_5y, "reference": 0,"valuation": valuation}
        ########### shares out decreasing or stable
        shares_out_growth_avg_5y = self.growth_information.loc['Shares Out Growth']['5Y']
        if shares_out_growth_avg_5y <= 0:
            valuation = True
        else:
            valuation = False
        quality_check['Shares Out Growth AVG 5Y'] = {"value": shares_out_growth_avg_5y,"reference": 0, "valuation": valuation}
        # Price to FCF average 5Y < 20
        #Buffet Indicator Market Cap < Actual Market Cap
        if self.general_information['Share Price'] * self.data.loc['Shares Out'][::-1][1]<= self.data.loc['Buffet Indicator'][::-1][1]:
            valuation = True
        else:
            valuation = False
        quality_check['Buffet Market Cap'] = {"value": self.data.loc['Buffet Indicator'][::-1][1],"reference": self.general_information['Share Price'] * self.data.loc['Shares Out'][::-1][1], "valuation": valuation}
        return quality_check