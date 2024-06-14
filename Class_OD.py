import pandas as pd
import streamlit as st
from streamlit import session_state as ss
Grade_5C3 = ["H-40", "X-42", "X-46", "-50", "X-52", "H-55", "J-55", "K-55", "X-56", "X-60", 'M-65', "-70", "C-75", "E-75", "H-80", "L-80", "N-80", "C-90", "H-90", "C-95", "H-95", "S-95", "T-95", "X-95", "-100", "P-105", "G-105", "P-110", 
             "C-110", "H-110", "P-110", "-120", "H-125", "Q-125", "V-130", "S-135", "V-140", "V-150", "-155", "-160", "-170", "-180"]

def OD_df(OD):
    pd_manual = pd.DataFrame(
        {
            "1_Size Outside Diameter in. D":[], "2_Nominal Weight, Threadsand Coupling lb/ft":[], "3_Grade":[], "6_Drift Diameter in.":[], 
            "12_Collapse Resistance psi":[], "13_Pipe Body Yield 1000 lb":[], "17_Same Grade":[], "24_Same Grade":[]
        })
    return st.data_editor(
        pd_manual, column_config=
        {
            "3_Grade":st.column_config.SelectboxColumn("Grade", required=True, options=Grade_5C3),
            "1_Size Outside Diameter in. D":st.column_config.NumberColumn("Outside Diameter, OD (Inch)", required=True, default=OD),
            "2_Nominal Weight, Threadsand Coupling lb/ft":st.column_config.NumberColumn("Nominal Weight, Wa (lbs/ft)", required=True), 
            "6_Drift Diameter in.":st.column_config.NumberColumn("Drift Diameter (Inch)", required=True),
            "12_Collapse Resistance psi":st.column_config.NumberColumn("Collapse Resistance (psi)", required=True), 
            "13_Pipe Body Yield 1000 lb":st.column_config.NumberColumn("Pipe Body Yield 1000 lb", required=True),
            "17_Same Grade":st.column_config.NumberColumn("Burst (psi)", required=True),
            "24_Same Grade":st.column_config.NumberColumn("Joint Strength 1000 lb", required=True)
        }, 
        use_container_width=True, num_rows="dynamic", disabled=["1_Size Outside Diameter in. D"])