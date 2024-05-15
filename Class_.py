import pandas as pd
import altair as alt
import streamlit as st
class Variabel:
    def __init__(self) -> None:
        
        self.Parameter = []
        
        # Variabel
        self.OD = 0
        self.MD = 0
        self.Section_value = 0
        self.Section = "Minimum"
        self.Drift_value = 0
        self.Drift = "Minimum"
        self.Gfr = 0
        self.Gg = 0
        self.Fluid = 0
        self.Packer = 0
        self.Heavy = 0
        self.Drill = 0
        self.DF_Burst = 0
        self.DF_Collapse = 0
        self.DF_Tension = 0
        self.Ps = 0
        self.SF = 0
        
        self.Drilling_fluid_psi = {}
        self.Drilling_fluid_ppg = {}
        
        # Burst
        self.Burst_IP = 0
        self.Burst_Ps = 0
        self.Burst_Pe = 0
        self.Burst_Hg = 0
        self.Burst_Hs = 0
        
        self.Burst_depth = []
        self.Burst_A = []
        self.Burst_B = []
        
        self.Burst_design = []

        # Collapse
        self.Collapse_Pressure = 0
        self.Collapse_P3 = 0
        self.Collapse_D3 = 0
        self.Collapse_table = []
        
        self.Collapse_design = []

        # Tension
        self.Tension_Table = []
        self.Tension_Overpull = 0
        self.Section_alt = 0
        self.Tension_check = [False]
        self.Tension_Depth = []
        self.Tension_Collapse = []
        self.fail_current = []
        self.succ_current = []
        self.fail = []
        self.fail_table = []
        
        self.Tension_Resist = []
        self.Tension_weight = []
        self.Tension_Buoyancy = 0
        self.Between = []

        # Biaxial
        self.Biaxial_X = 0
        self.Biaxial_Length = 0
        
    def Burst(self, Bagian, Load, Pe_burst, cement_list, cement_delta_pressure):
        if Bagian == "Surface" or Bagian == "Production":
            self.Burst_depth = [0, self.MD]
            self.Burst_A = [round(self.Burst_Ps, 2), round(self.Burst_IP, 2)]
            self.Burst_B = [0, round(self.Burst_Pe, 2)]
        elif Bagian == "Intermediate" and Load == "Maximum Load":
            self.Burst_depth = [0, round(self.MD - self.Burst_Hg, 2), self.MD]
            self.Burst_A = [round(self.Burst_Ps, 2), round(self.Burst_IP - self.Gg * self.Burst_Hg, 2), round(self.Burst_IP, 2)]
            self.Burst_B = [0, round(Pe_burst(self.Fluid, self.Burst_depth[1]), 2), round(self.Burst_Pe, 2)]
        elif Bagian == "Intermediate" and Load == "Minimum Load":
            self.Burst_depth = cement_list if min(cement_list) == 0 else [0] + cement_list
            self.Burst_A = [round(self.Burst_Ps + (self.Burst_IP - self.Burst_Ps) / (len(self.Burst_depth) - 1) * i, 2) for i in range(len(self.Burst_depth))]
            self.Burst_B = [sum(cement_delta_pressure[:i + 1]) for i in range(len(self.Burst_depth))]
    
    def Collapse(self, Bagian, Load, cement_delta, cement_delta_pressure, ppg_list, cement_list, Pressure_eq):
        self.Drilling_fluid_psi = {0:0} | {sum(cement_delta[:i + 1]):sum(cement_delta_pressure[:i + 1]) for i in range(len(cement_delta))}
        self.Drilling_fluid_ppg = {0:0} | {sum(cement_delta[:i + 1]):([self.Drill] + ppg_list)[i] for i in range(len(cement_delta))}
        if Bagian == "Surface" and Load == "Minimum Load":
            Collapse_depth = [0, self.MD]
            Collapse_A = [0, round(self.Collapse_Pressure, 2)]
            Collapse_B = [0, round(self.Collapse_Pressure * self.DF_Collapse, 2)]
            self.Collapse_table = pd.DataFrame({"Depth":Collapse_depth, "A_psi":Collapse_A, "B_psi":Collapse_B})
        elif (Bagian == "Surface" and Load == "Maximum Load") or (Bagian == "Production"):
            self.Collapse_table = pd.DataFrame({"Depth":list(self.Drilling_fluid_psi.keys()), "A_psi":list(self.Drilling_fluid_psi.values())})
            self.Collapse_table["B_psi"] = self.Collapse_table["A_psi"] * self.DF_Collapse
        elif Bagian == "Intermediate":
            Collapse_depth = sorted(list(set(cement_list + [self.Collapse_D3] if min(cement_list) == 0 else [0] + cement_list + [self.Collapse_D3])))
            Collapse_A = [(0 if depth < self.Collapse_D3 else round(Pressure_eq(self.Heavy, depth - self.Collapse_D3), 2)) for depth in Collapse_depth]
            Collapse_B_df = pd.DataFrame({"depth":list(self.Drilling_fluid_psi.keys()), "psi":list(self.Drilling_fluid_psi.values()), "ppg":list(self.Drilling_fluid_ppg.values())})
            Collapse_B = []
            for depth in Collapse_depth:
                Bigger  = min(filter(lambda i: i > depth, Collapse_B_df.iloc[:,0])) if depth != self.MD else None
                Smaller = max(filter(lambda i: i < depth, Collapse_B_df.iloc[:,0])) if depth != 0 else None
                if len(Collapse_B_df[Collapse_B_df.iloc[:,0] == depth]) != 0: Collapse_B.append(round(self.Drilling_fluid_psi[depth], 2))
                else: Collapse_B.append(round(self.Drilling_fluid_psi[Smaller] + Pressure_eq(self.Drilling_fluid_ppg[Bigger], depth - Smaller), 2))
            self.Collapse_table = pd.DataFrame({"Depth":Collapse_depth, "A_psi":Collapse_A, "B_psi":Collapse_B})
            self.Collapse_table["C_psi"] = round(self.Collapse_table["B_psi"] - self.Collapse_table["A_psi"], 2)
            self.Collapse_table["D_psi"] = round(self.Collapse_table["C_psi"] * self.DF_Collapse, 2)
            self.Collapse_table["M2"] = round(Pressure_eq(self.Heavy, self.Collapse_table["Depth"]), 2)
    
    def Tension(self): 
        self.Tension_weight = []
        self.Tension_Depth = [self.MD]

def OD_index(Casing_subset_OD, Parameter):
    OD_index = [index for index, value in enumerate(Casing_subset_OD.iloc[:, 0]) if value == Parameter[0]]
    return st.selectbox('Size Outside Diameter (inch)', Casing_subset_OD.iloc[:, 0], index=OD_index[0])

def MD_ft(Parameter):
    MD_ft = st.data_editor(
        pd.DataFrame({"Casing length (MD)":[Parameter[1]]}), 
            column_config=
            {
                "Casing length (MD)":st.column_config.NumberColumn(help="Casing is assumed to be vertical - 3ft minimum", required=True, min_value=3, format="%d ft")
            }, 
            use_container_width=True, hide_index=True)
    return MD_ft.iloc[0,0]

def Section(Parameter, MD):
    return  st.data_editor(pd.DataFrame({"Casing Length Section (ft)":[Parameter[2]], "Section":[Parameter[3]]}), column_config=
            {
                "Casing Length Section (ft)":st.column_config.NumberColumn(help="Minimum casing length input 3ft", min_value=3, max_value=int(MD), required=True, format="%d ft"),
                "Section":st.column_config.SelectboxColumn(options=["Minimum", "Maximum"], required=True)
            }, 
            use_container_width=True, hide_index=True)

def Drift(Parameter, Casing_subset_drift):
    return st.data_editor(
        pd.DataFrame({"Casing Drift Diameter (Inch)":[Parameter[4] if len(Casing_subset_drift[Casing_subset_drift.iloc[:,5] == Parameter[4]]) != 0 else Casing_subset_drift.iloc[0,5]], "Drift":[Parameter[5]]}),
            column_config=
            {
                "Casing Drift Diameter (Inch)":st.column_config.SelectboxColumn(options=(Casing_subset_drift['6_Drift Diameter in.'].sort_values(ascending=True)), required=True), 
                "Drift":st.column_config.SelectboxColumn(options=["Minimum", "Maximum"], required=True)
            },
            use_container_width=True, hide_index=True)
    
def Gradient_Fracture(Parameter, Bagian):
    Gradient_Fracture = st.data_editor(
        pd.DataFrame({"Gfr (Fracture Gradient)":[Parameter[6]]}), 
            column_config=
            {
                "Gfr (Fracture Gradient)":st.column_config.NumberColumn("Gfr (Fracture Gradient)" if Bagian != "Production" else "None", required=True, format="%.2f ppg")
            }, 
            disabled=False if Bagian != "Production" else True, use_container_width=True, hide_index=True)
    return Gradient_Fracture.iloc[0,0]

def Gradient_Gas(Bagian, Load):
    Gradient_Gas = st.data_editor(
        pd.DataFrame({"Gradient Hidrostatic Gas (β)":[None if (Bagian == "Surface" and Load == "Minimum Load") else 0.115]}), 
            column_config=
            {
                "Gradient Hidrostatic Gas (β)":st.column_config.NumberColumn("None" if (Bagian == "Surface" and Load == "Minimum Load") else "Gradient Hidrostatic Gas (β)", required=True, format="%.3f psi/ft")
            }, 
            disabled=True if (Bagian == "Surface" and Load == "Minimum Load") else False, use_container_width=True, hide_index=True)
    return Gradient_Gas.iloc[0,0]

def Fluid_density(Parameter):
    Fluid_density = st.data_editor(
        pd.DataFrame({"Fluid Density":[Parameter[7]]}), 
            column_config=
            {
                "Fluid Density":st.column_config.NumberColumn(required=True, format="%.2f ppg")
            }, 
            use_container_width=True, hide_index=True)
    return Fluid_density.iloc[0,0]

def Packer_density(Parameter, Bagian):
    Packer_density = st.data_editor(
        pd.DataFrame({"Packer Fluid Density":[Parameter[8]]}), 
            column_config=
            {
                "Packer Fluid Density":st.column_config.NumberColumn("Packer Fluid Density" if Bagian == "Production" else "None", required=True, format="%.2f ppg")
            }, 
            disabled=False if Bagian == "Production" else True, use_container_width=True, hide_index=True)
    return Packer_density.iloc[0,0]

def Heavy_density(Parameter, Bagian):
    Heavy_density = st.data_editor(
        pd.DataFrame({"Heavy Mud Density":[Parameter[9]]}), 
            column_config=
            {
                "Heavy Mud Density":st.column_config.NumberColumn("Heavy Mud Density" if Bagian == "Intermediate" else "None", required=True, format="%.2f ppg")
            }, 
            disabled=False if Bagian == "Intermediate" else True, use_container_width=True, hide_index=True)
    return Heavy_density.iloc[0,0]

def Drill_density(Parameter):
    Drill_density = st.data_editor(
        pd.DataFrame({"Drill Mud Density":[Parameter[10]]}), 
            column_config=
            {
                "Drill Mud Density":st.column_config.NumberColumn(required=True, format="%.2f ppg")
            }, 
            use_container_width=True, hide_index=True)
    return Drill_density.iloc[0,0]

def Design_Factor():
    return st.data_editor(
        pd.DataFrame(
            {
                "DF_Burst":[1.1],
                "DF_Collapse":[1.1],
                "DF_Tension":[1.6]
            }), 
            column_config=
            {
                "DF_Burst":st.column_config.NumberColumn(help="Burst Design Factor, usually around 1 - 1.1", required=True, format="%.2f"),
                "DF_Collapse":st.column_config.NumberColumn(help="Collapse Design Factor, usually around 0.85 - 1.125", required=True, format="%.2f"),
                "DF_Tension":st.column_config.NumberColumn(help="Tension Design Factor, usually around 1.6 - 1.8", required=True, format="%.2f")
            },
            use_container_width=True, hide_index=True)

def Surface_Pressure(Bagian, Load, Parameter, Casing):
    if Bagian == "Surface": Surface_Pressure_Type = [None, None]
    elif Bagian == "Intermediate" and Load == "Maximum Load": Surface_Pressure_Type = ["Ps = BOP", "BOP"]
    elif Bagian == "Intermediate" and Load == "Minimum Load": Surface_Pressure_Type = ["Ps = ASP = (0.052 x Gfr - β) x Depth", "ASP", "Unavailable"]
    elif Bagian == "Production" and Load == "Maximum Load": Surface_Pressure_Type = ["Ps = BHP", "BHP"]
    elif Bagian == "Production" and Load == "Minimum Load": Surface_Pressure_Type = ["Ps = SITP = BPH - (β x Casing Length)", "SITP", "BHP"]
    Surface_Pressure = st.data_editor(
        pd.DataFrame({"Surface Pressure (Ps)":[Parameter[14]], "Type":[Surface_Pressure_Type[1]]}),
            column_config=
            {
                "Surface Pressure (Ps)": st.column_config.NumberColumn("Surface Pressure (Ps)" if Bagian != "Surface" else "None", help=Surface_Pressure_Type[0], required=True, format="%.2f psi"),
                "Type": st.column_config.SelectboxColumn("Type" if Bagian != "Surface" else "None", options=Surface_Pressure_Type[1:], required=True)
            }, 
            disabled=False if Bagian != "Surface" else True, use_container_width=True, hide_index=True)
    if Bagian == "Intermediate" and Load == "Minimum Load": return (0.052 * Casing.Gfr - Casing.Gg) * Casing.MD if Surface_Pressure.iloc[0,1] != "ASP" else Surface_Pressure.iloc[0,0]
    elif Bagian == "Production" and Load == "Minimum Load": return Surface_Pressure.iloc[0,0] - Casing.Gg * Casing.MD if Surface_Pressure.iloc[0,1] != "SITP" else Surface_Pressure.iloc[0,0]
    elif Bagian != "Surface": return Surface_Pressure.iloc[0,0]

def altair_chart(df, title_x, MD, theme_set):
    return st.altair_chart(alt.Chart(df).mark_line().encode(
        x = alt.X("value", title=title_x), 
        y = alt.Y("Depth", title="Depth (ft)", scale=alt.Scale(domain=[0, MD], reverse=True)), 
        order="Depth", 
        color=alt.Color('variable', sort=['GOOG'])), theme=theme_set, use_container_width=True)