import json
import os
import pandas as pd
import math
import yfinance
import numpy as np
import requests
from engine.growth_analysis import GrowthAnalysis
from engine.quality_engine import QualityEngine
from engine.utils import to_float,discount,data_growth
import os.path



class AnalysisEngine:
    def __init__(self,ticker):
        self.ticker = ticker

        balansheet_url = f"https://api.stockanalysis.com/wp-json/sa/financials?type=balance-sheet&symbol={self.ticker}&range=annual"
        cashflow_url = f"https://api.stockanalysis.com/wp-json/sa/financials?type=cash-flow-statement&symbol={self.ticker}&range=annual"
        ratio_url = f"https://api.stockanalysis.com/wp-json/sa/financials?type=ratios&symbol={self.ticker}&range=annual"
        income_url = f"https://api.stockanalysis.com/wp-json/sa/financials?type=income-statement&symbol={self.ticker}&range=annual"


        bs = self.get_data(balansheet_url)
        cf = self.get_data(cashflow_url)
        ratio = self.get_data(ratio_url)
        income = self.get_data(income_url)

        self.bs = pd.DataFrame.from_dict(bs['data']['data'],orient='index').transpose()
        self.cf = pd.DataFrame.from_dict(cf['data']['data'],orient='index').transpose()
        self.ratio = pd.DataFrame.from_dict(ratio['data']['data'],orient='index').transpose()
        self.income = pd.DataFrame.from_dict(income['data']['data'],orient='index').transpose()

        self.yf_data = yfinance.Ticker(self.ticker)

    def get_data(self,url):
        payload = ""
        headers = {"User-Agent": "PostmanRuntime/7.29.0"}
        response = requests.request("GET", url, headers=headers, data=payload)
        d = json.loads(response.text)
        return d

    def prepare_data(self):


        cr_index = self.ratio.currentratio[0] #Maybe 1 for last year
        dtfcf_index = self.ratio.debtfcf[0]
        dte_index = self.ratio.debtequity[0]
        self.debt = {"Current Ratio":[],"Debt to FCF":[],"Debt to Equity":[]}
        for i,c in enumerate(self.ratio.currentratio):
            self.debt["Current Ratio"].append(self.ratio.currentratio[i])
            self.debt['Debt to FCF'].append(self.ratio.debtfcf[i])
            self.debt['Debt to Equity'].append(self.ratio.debtequity[i])

        self.debt_dataframe = pd.DataFrame.from_dict(self.debt)
        self.general_information = {"Share Price":self.__share_price__()}


    def enterprise_value_to_ebitda_analysis(self,years=5,discount_rate=0.125,terminal_value=14,ebitda_margin=None,revenue_growth_rate=[0.1],shares_out=None):
        print("not implemented yet")

    def discounted_cash_flow_analysis(self,years=5,discount_rate=0.125,terminal_value=14,perpetuity_growth=0.02,fcf_margin=None,net_margin=None,revenue_growth_rate=[0.1],shares_out=None):
        current_year_revenue = self.yf_data.analysis
        revenue_estimates_y0 = current_year_revenue.loc['0Y']
        revenue_estimates_y1 = current_year_revenue.loc['+1Y']
        revenue_estimates_y5 = current_year_revenue.loc['+5Y']

        growth_0y = revenue_estimates_y0.loc['Revenue Estimate Growth']
        growth_1y = revenue_estimates_y1.loc['Revenue Estimate Growth']

        #growth_5y = (revenue_estimates_y5.loc['Growth']*5 - growth_1y)/4
        normalization_value = 1#1000000000
        analyst_revenue = [revenue_estimates_y0.loc['Revenue Estimate Avg']/normalization_value,revenue_estimates_y1.loc['Revenue Estimate Avg']/normalization_value]
        last_r = analyst_revenue[::-1][0]
        for i in range(0,years-2):
            g = growth_1y*(1-0.1*(i+1))
            if g<=perpetuity_growth:
                g = perpetuity_growth
            r = last_r*(1+(g))
            last_r=r
            analyst_revenue.append(r)
        average_growth_rate = np.mean(revenue_growth_rate)
        self.terminal_information = {"Terminal Multiple":[terminal_value],"Perpetuity Growth":[perpetuity_growth],"Discount Rate":[discount_rate],"Rev Growth Rate":[average_growth_rate],"Actual Share Price":self.general_information['Share Price']}
        last_year = self.income.datekey[1].split('-')[0]
        yf = [f"{int(last_year) + i}" for i in range(1, years+1)] #+ ["TV"]
        #last_year_revenue = self.output.loc['Revenue'][::-1][1]
        if fcf_margin is None:
            min_fcf_margin_average = np.mean([m for m in self.growths.loc['FCF Margin Average'][0:3] if m>0])
        else:
            min_fcf_margin_average = fcf_margin
        if net_margin is None:
            min_net_margin_average = np.mean([m for m in self.growths.loc['Net Margin Average'][0:3] if m>0])
        else:
            min_net_margin_average = net_margin

        future_revenues = [revenue_estimates_y0.loc['Revenue Estimate Avg']/normalization_value,revenue_estimates_y1.loc['Revenue Estimate Avg']/normalization_value]
        future_revenues_custom = [self.income.revenue[1]*(1+revenue_growth_rate[0]),(self.income.revenue[1]*(1+revenue_growth_rate[0]))*(1+revenue_growth_rate[0])]
        last_year_revenue = future_revenues[1]
        last_year_revenue_custom = future_revenues_custom[1]
        revenue_growth_splitted = np.array_split(range(0,years), len(revenue_growth_rate))
        yfr = {}
        j=0
        for y in range(2,years):
            if y not in revenue_growth_splitted[j]:
                j=j+1
            revenue_growth = revenue_growth_rate[j]
            next_y_revenue = last_year_revenue*(1+revenue_growth)
            next_y_revenue_custom = last_year_revenue_custom*(1+revenue_growth)

            future_revenues.append(next_y_revenue)
            future_revenues_custom.append(next_y_revenue_custom)

            last_year_revenue = next_y_revenue
            last_year_revenue_custom = next_y_revenue_custom

        for i,y in enumerate(yf):
            last_shares_out = self.income.shareswadil[0]
            if last_shares_out is None:
                last_shares_out = self.income.shareswa[0]
            last_value_custom_fcf = discount(cf=future_revenues_custom[i]*(min_fcf_margin_average/100),
                                                             discount_rate=discount_rate,
                                                             begin_year=int(last_year)+1,
                                                             actual_year=int(y))
            last_value_analyst_fcf = discount(cf=analyst_revenue[i] * (min_fcf_margin_average / 100),
                                                   discount_rate=discount_rate,
                                                   begin_year=int(last_year) + 1,
                                                   actual_year=int(y))
            last_value_custom_net_income = discount(cf=(future_revenues_custom[i] * (min_net_margin_average / 100))/last_shares_out,
                                                     discount_rate=discount_rate,
                                                     begin_year=int(last_year) + 1,
                                                     actual_year=int(y))
            last_value_analyst_net_income = discount(cf=(analyst_revenue[i] * (min_net_margin_average / 100))/last_shares_out,
                                                       discount_rate=discount_rate,
                                                       begin_year=int(last_year) + 1,
                                                       actual_year=int(y))
            yfr[y] = {
                "Revenue":future_revenues_custom[i],
                "Analyst Revenue": analyst_revenue[i],
                "FCF Margin":min_fcf_margin_average,
                "Net Margin":min_net_margin_average,
                "Projected FCF":future_revenues_custom[i]*(min_fcf_margin_average/100),
                "Analyst Projected FCF":analyst_revenue[i]*(min_fcf_margin_average/100),
                "Discounted FCF":last_value_custom_fcf,
                "Analyst Discounted FCF":last_value_analyst_fcf,
                "Projected EPS":(future_revenues_custom[i]*(min_net_margin_average/100))/last_shares_out,
                "Analyst Projected EPS":(analyst_revenue[i]*(min_net_margin_average/100))/last_shares_out,
                "Discounted EPS":last_value_custom_net_income,
                "Analyst Discounted EPS":last_value_analyst_net_income,
                #"Test":f'={ay}39*((1+K37)^(B36-{ay}36-1))'
        }
        self.termina_value = dict()
        self.termina_value['TV Multiple FCF'] = [last_value_custom_fcf*self.terminal_information['Terminal Multiple'][0],last_value_analyst_fcf*self.terminal_information['Terminal Multiple'][0]]

        perpetuity_v_custom = (last_value_custom_fcf * (1+self.terminal_information['Perpetuity Growth'][0]))/(self.terminal_information['Discount Rate'][0]-self.terminal_information['Perpetuity Growth'][0])
        perpetuity_v_anayst = (last_value_analyst_fcf * (1 + self.terminal_information['Perpetuity Growth'][0])) / (self.terminal_information['Discount Rate'][0] - self.terminal_information['Perpetuity Growth'][0])
        self.termina_value['TV Perpetuity'] = [perpetuity_v_custom,perpetuity_v_anayst]
        self.termina_value['TV Multiple EPS'] = [last_value_custom_net_income*self.terminal_information['Terminal Multiple'][0],last_value_analyst_net_income*self.terminal_information['Terminal Multiple'][0]]
        self.termina_value = pd.DataFrame(self.termina_value)

        self.future_cf = pd.DataFrame(yfr)
        self.terminal_information = pd.DataFrame(self.terminal_information)

        dcf_sum_multiple = sum([yfr[yi]['Discounted FCF'] for yi in yfr]) + self.termina_value['TV Multiple FCF'][0]
        dcf_sum_perpetuity = sum([yfr[yi]['Discounted FCF'] for yi in yfr]) + self.termina_value['TV Perpetuity'][0]

        dcf_sum_multiple_analyst = sum([yfr[yi]['Analyst Discounted FCF'] for yi in yfr]) + self.termina_value['TV Multiple FCF'][1]
        dcf_sum_perpetuity_analyst = sum([yfr[yi]['Analyst Discounted FCF'] for yi in yfr]) + self.termina_value['TV Perpetuity'][1]


        ni_sum_multiple = sum([yfr[yi]['Discounted EPS'] for yi in yfr]) + self.termina_value['TV Multiple EPS'][0]
        #ni_sum_perpetuity = sum([yfr[yi]['Discounted FCF'] for yi in yfr]) + self.termina_value['TV Perpetuity'][0]

        ni_sum_multiple_analyst = sum([yfr[yi]['Analyst Discounted EPS'] for yi in yfr]) + self.termina_value['TV Multiple EPS'][1]
        #ni_sum_perpetuity_analyst = sum([yfr[yi]['Analyst Discounted FCF'] for yi in yfr]) + self.termina_value['TV Perpetuity'][1]


        if shares_out is None:
            future_shares_out = self.__future_shares_outstanding__(last_shares_out,sum(self.income.sharesYoY[1:4])/3)
        else:
            future_shares_out = shares_out
        if math.isnan(future_shares_out):
            future_shares_out = self.income.shareswadil[0]

        fair_share_price_multiple = dcf_sum_multiple/future_shares_out
        fair_share_price_perpetuity = dcf_sum_perpetuity / future_shares_out

        fair_share_price_multiple_analyst = dcf_sum_multiple_analyst / future_shares_out
        fair_share_price_perpetuity_analyst = dcf_sum_perpetuity_analyst / future_shares_out

        fair_share_price_eps_multiple_analyst = ni_sum_multiple_analyst
        fair_share_price_eps_multiple = ni_sum_multiple


        data_out_analyst= {"Source":["Analyst FCF","Analyst FCF Perpetuity","Analyst EPS"],"Fair Enterprise Value":[dcf_sum_multiple_analyst,dcf_sum_perpetuity_analyst,ni_sum_multiple_analyst],"Future Shares Out":[future_shares_out,future_shares_out,future_shares_out],"Fair Share Price":[fair_share_price_multiple_analyst,fair_share_price_perpetuity_analyst,fair_share_price_eps_multiple_analyst]}
        data_out_custom = {"Source":['Custom FCF','Custom FCF Perpetuity',"Custom EPS"],"Fair Enterprise Value":[dcf_sum_multiple,dcf_sum_perpetuity,ni_sum_multiple],"Future Shares Out":[future_shares_out,future_shares_out,future_shares_out],"Fair Share Price":[fair_share_price_multiple,fair_share_price_perpetuity,fair_share_price_eps_multiple]}


        self.discount_cash_flow_final_analyst = pd.DataFrame(data_out_analyst)
        self.discount_cash_flow_final_custom = pd.DataFrame(data_out_custom)


    def growth_analysis(self):
        self.growth_engine = GrowthAnalysis(self)
        growth_out = self.growth_engine.past_years_growth()
        self.growths = pd.DataFrame(growth_out)

    def analysis_quality_check(self):
        self.quality_engine = QualityEngine(self.output,self.debt_dataframe,self.growths,self.general_information)
        quality_valuation = self.quality_engine.quality_valuation()
        self.quality_check_dataframe = pd.DataFrame.from_dict(quality_valuation)

    def __future_shares_outstanding__(self,shares_out,buyback_rate=0,years=3):
        return shares_out*((1+buyback_rate/100)**years)

    def __extract_price__(self):
        start_years =  self.output.columns[0].split('-')[0]
        history = self.yf_data.history(period="max", interval="1mo", start=f"{start_years}-11-30")
        price_data = {}
        for i,d in history.iterrows():
            if i.year not in price_data:
                if str(i.month)=="12" and not math.isnan(d.Close):
                    price_data[str(i.year)] = d.Close
        return price_data

    def __share_price__(self):
        history = self.yf_data.history(period="1d")
        return history['Close'][0]

    def __ratio_history__(self):
        rev_fcf = []
        fcf_margin = []
        net_margin = []
        for d in self.output:
            rev_fcf.append(self.output[d]['Revenue']/self.output[d]['FCF'])
            fcf_margin.append((self.output[d]['FCF']/self.output[d]['Revenue'])*100)
            net_margin.append((self.output[d]['Net Income']/self.output[d]['Revenue'])*100)
        return rev_fcf,fcf_margin,net_margin

    def __fix_growth__(self):
        for index in self.output.index:
            if index.find("Growth")!=-1:
                temp = pd.Series([val if math.isnan(val) else "{0:.3f}%".format(val) for val in self.output.loc[index]])
                self.output.loc[index] = temp.values

    def __save__(self):
        writer = pd.ExcelWriter(f'resources/{self.ticker}/template.xlsx',engine='xlsxwriter')
        self.output.to_excel(writer, sheet_name='Analysis', index=True ) #na_rep='NaN'
        #Auto-adjust columns' width
        #worksheet = writer.sheets['my_analysis']
        max_d = max([len(d) for d in self.output.index])
        for column in self.output:
            column_width = max(self.output[column].astype(str).map(len).max(), max_d)
            col_idx = self.output.columns.get_loc(column)
            writer.sheets['Analysis'].set_column(col_idx, col_idx, column_width)
        self.growths.to_excel(writer, sheet_name='Analysis', startrow=26, startcol=0)
        self.future_cf.to_excel(writer, sheet_name='Analysis', startrow=36, startcol=0)
        self.termina_value.to_excel(writer,sheet_name='Analysis',startrow=52,startcol=5,index=False)
        self.terminal_information.to_excel(writer,sheet_name='Analysis',startrow=52,startcol=9,index=False)
        self.discount_cash_flow_final_custom.to_excel(writer,sheet_name='Analysis',startrow=52,startcol=0,index=False)
        self.discount_cash_flow_final_analyst.to_excel(writer, sheet_name='Analysis', startrow=58, startcol=0,index=False)
        writer.save()

