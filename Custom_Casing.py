import numpy as np
import pandas as pd
import streamlit as st
Grade_5C3 = ["H-40", "X-42", "X-46", "-50", "X-52", "H-55", "J-55", "K-55", "X-56", "X-60", 'M-65', "-70", "C-75", "E-75", "H-80", "L-80", "N-80", 
             "C-90", "H-90", "C-95", "H-95", "S-95", "T-95", "X-95", "-100", "P-105", "G-105", "P-110", "C-110", "H-110", "P-110", "-120", "H-125", 
             "Q-125", "V-130", "S-135", "V-140", "V-150", "-155", "-160", "-170", "-180"]

def OD_df(OD):
    pd_manual = pd.DataFrame(
        {
            "1_Size Outside Diameter in. D":[OD], "2_Nominal Weight, Threadsand Coupling lb/ft":[np.nan], "3_Grade":[np.nan], "6_Drift Diameter in.":[np.nan], 
            "12_Collapse Resistance psi":[np.nan], "13_Pipe Body Yield 1000 lb":[np.nan], "17_Same Grade":[np.nan], "24_Same Grade":[np.nan]
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

if __name__ == "__main__":
    st.write("4.5 Inch")
    st.session_state["OD_4.5"] = OD_df(4.5)
    
    st.write("5.0 Inch")
    st.session_state["OD_5.0"] = OD_df(5.0)
    
    st.write("5.5 Inch")
    st.session_state["OD_5.5"] = OD_df(5.5)
    
    st.write("6.625 Inch")
    st.session_state["OD_6.625"] = OD_df(6.625)
    
    st.write("7.0 Inch")
    st.session_state["OD_7.0"] = OD_df(7.0)
    
    st.write("7.625 Inch")
    st.session_state["OD_7.625"] = OD_df(7.625)
    
    st.write("8.625 Inch")
    st.session_state["OD_8.625"] = OD_df(8.625)
    
    st.write("9.625 Inch")
    st.session_state["OD_9.625"] = OD_df(9.625)
    
    st.write("10.75 Inch")
    st.session_state["OD_10.75"] = OD_df(10.75)
    
    st.write("11.75 Inch")
    st.session_state["OD_11.75"] = OD_df(11.75)
    
    st.write("13.375 Inch")
    st.session_state["OD_13.375"] = OD_df(13.375)
    
    st.write("16.0 Inch")
    st.session_state["OD_16.0"] = OD_df(16.0)
    
    st.write("18.625 Inch")
    st.session_state["OD_18.625"] = OD_df(18.625)
    
    st.write("20.0 Inch")
    st.session_state["OD_20.0"] = OD_df(20.0)

Session = st.session_state