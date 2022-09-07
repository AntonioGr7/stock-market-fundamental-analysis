import streamlit as st
from engine.analysis_engine import AnalysisEngine

#st.title('Fair Value Calculator')

st.set_page_config(page_title="My App",layout='wide')

def color(val):
    color = 'green' if val else 'red'
    return f'background-color: {color}'


def execute_model():
        try:
            engine = AnalysisEngine(ticker=ticker.lower())

            engine.prepare_data()
            engine.growth_analysis()
            st.dataframe(engine.income,height=1000,width=2000)
            #col_gr,col_quality = st.columns(2)
            #with col_gr:
            st.dataframe(engine.ratio, height=1000, width=2000)
            #with col_quality:
            st.dataframe(engine.cf,height=1000,width=2000)
                #st.dataframe(engine.quality_check_dataframe.T.style.applymap(color,subset=['valuation']),height=1000, width=2000)'''
            st.dataframe(engine.growths,height=1000,width=2000)
            option = st.selectbox("Valuation Method", ['Discount Methods','EV/Ebit'], index=0)
            if option=="Discount Methods":
                col1,col2,col3 = st.columns(3)
                with col1:
                    years = st.selectbox("Years of Analysis", [3, 5, 7, 10])
                    revenue_gr = st.text_input("Revenue Growth % (You could insert multiple growth rate separated by ',' - es. 10,8)",placeholder="10")
                    discount_rate = st.text_input("Discount Rate", placeholder="12.5")
                    fair_value_btn = st.button("Discount Model",disabled=False)
                with col2:
                    fcf_margin = st.text_input("Free Cash Flow Margin %",placeholder="10")
                    net_margin = st.text_input("Net Margin %",placeholder="10")
                with col3:
                    terminal_multiple = st.text_input("Terminal Value",placeholder="16")
                    perpetuity = st.text_input("Perpetuity Growth",placeholder="0.03")
                if fair_value_btn:
                    if len(terminal_multiple)==0:
                        terminal_multiple=16
                    else:
                        terminal_multiple = int(terminal_multiple)
                    if len(revenue_gr)==0:
                        st.errors("Revenue Growth is mandatory")
                    else:
                        grs = revenue_gr.split(",")
                        revenue_gr = [float(g)/100 for g in grs]
                    if len(fcf_margin)==0:
                        fcf_margin=None
                    else:
                        fcf_margin=float(fcf_margin)
                    if len(net_margin) == 0:
                        net_margin = None
                    else:
                        net_margin = float(net_margin)
                    if len(perpetuity) == 0:
                        perpetuity = 0.03
                    else:
                        perpetuity = float(perpetuity)
                    if len(discount_rate) == 0:
                        discount_rate = 0.125
                    else:
                        discount_rate = float(discount_rate)/100
                    print("D",discount_rate)
                    engine.discounted_cash_flow_analysis(
                        years=years,
                        discount_rate=discount_rate,
                        terminal_value=terminal_multiple,
                        perpetuity_growth=perpetuity,
                        revenue_growth_rate=revenue_gr,fcf_margin=fcf_margin,net_margin=net_margin)
                    st.dataframe(engine.future_cf, height=1000, width=2000)
                    st.dataframe(engine.terminal_information, width=1000, height=2000)
                    st.dataframe(engine.discount_cash_flow_final_custom,width=1000,height=2000)
                    st.dataframe(engine.discount_cash_flow_final_analyst,width=1000,height=2000)
            if option == "EV/Ebit":
                col1, col2  = st.columns(2)
                with col1:
                    years = st.selectbox("Years of Analysis", [3, 5, 7, 10])
                    revenue_gr = st.text_input(
                        "Revenue Growth % (You could insert multiple growth rate separated by ',' - es. 10,8)",
                        placeholder="10")
                    discount_rate = st.text_input("Discount Rate", placeholder="12.5")
                    fair_value_btn = st.button("EV/Ebt Valuation", disabled=False)
                with col2:
                    ebtda_margin = st.text_input("Ebt Margin %", placeholder="10")
                    terminal_multiple = st.text_input("Terminal Value", placeholder="10")
                if fair_value_btn:
                    if len(terminal_multiple) == 0:
                        terminal_multiple = 10
                    else:
                        terminal_multiple = int(terminal_multiple)
                    if len(revenue_gr) == 0:
                        st.errors("Revenue Growth is mandatory")
                    else:
                        grs = revenue_gr.split(",")
                        revenue_gr = [float(g) / 100 for g in grs]
                    if len(ebtda_margin) == 0:
                        ebitda_margin = None
                    else:
                        ebitda_margin = float(ebtda_margin)
                    if len(discount_rate) == 0:
                        discount_rate = 0.125
                    else:
                        discount_rate = float(discount_rate) / 100
                    engine.enterprise_value_to_ebt_analysis(
                        years=years,
                        discount_rate=discount_rate,
                        terminal_value=terminal_multiple,
                        revenue_growth_rate=revenue_gr, ebt_margin=ebitda_margin)
                    st.dataframe(engine.future_ebtda, height=1000, width=2000)
                    st.dataframe(engine.terminal_information, width=1000, height=2000)
                    st.dataframe(engine.data_out_ebt_analysis,width=1000,height=2000)
        except Exception as e:
            print(repr(e))






st.sidebar.header('Insert ticker here:')
ticker = st.sidebar.text_input('Ticker', 'META')
load_data_btn = st.sidebar.button("Load Data",on_click=execute_model())








