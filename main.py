from engine.analysis_engine import AnalysisEngine


if __name__ == '__main__':
    engine = AnalysisEngine(ticker="GOOG")
    engine.prepare_data()
    engine.growth_analysis()

    #engine.analysis_quality_check()
    '''engine.enterprise_value_to_ebt_analysis(
        years=10,
        discount_rate=0.125,
        terminal_value=10,
        revenue_growth_rate=[0.10], ebt_margin=46)'''

    engine.discounted_cash_flow_analysis(years=10, discount_rate=0.125, terminal_value=18,
                                         perpetuity_growth=0.05,
                                         revenue_growth_rate=[0.01],fcf_margin=18,net_margin=18
                                         )

