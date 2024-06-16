import streamlit as st
import pandas as pd
from streamlit import session_state as ss
from time import time
from math import ceil
from functools import lru_cache
import Class_ 
import numpy as np
import altair as alt 
st.set_page_config(layout="wide")

# Data Mentah Properties Casing Design
Casing_data_ = pd.read_excel(io='Casing_Simplify.xlsx', skiprows=[0, 1], header=[0]) 

# Data Rapih Properties Casing Design
Casing_data  = Casing_data_[Casing_data_.iloc[:, 16] != "—"]
Grade_5C3 = ["H-40", "X-42", "X-46", "-50", "X-52", "H-55", "J-55", "K-55", "X-56", "X-60", 'M-65', "-70", "C-75", "E-75", "H-80", "L-80", "N-80", "C-90", "H-90", "C-95", "H-95", "S-95", "T-95", "X-95", "-100", "P-105", "G-105", "P-110", 
             "C-110", "H-110", "P-110", "-120", "H-125", "Q-125", "V-130", "S-135", "V-140", "V-150", "-155", "-160", "-170", "-180"]

# Variasi Data OD Casing Design
Casing_subset_OD = Casing_data.drop_duplicates(subset='1_Size Outside Diameter in. D').reset_index(drop="index")

Casing = Class_.Variabel()
Manual = Class_.Ten_Bix()
Catalog = Class_.Ten_Bix()

with st.expander("Pilih Bagian dan Load Casing Design"):

    # Pembagian Kolom Pertama
    Expander_1, Expander_2, Expander_3 = st.columns(3) 
    
    # Expand Bagian Casing Design
    with Expander_1: Bagian = st.selectbox('How',("Surface", "Intermediate", "Production"), label_visibility="collapsed")

    # Expand Jenis Casing Load Design MAXIMUM atau MINIMUM
    with Expander_2: Load = st.selectbox('Load',("Maximum Load", "Minimum Load"), label_visibility="collapsed")

    # Catalog atau Manual
    with Expander_3: Catalog_select = st.selectbox('Catalog',("Catalog", "Manual"), label_visibility="collapsed")

st.title('_Streamlit_ is :blue[cool] :sunglasses:')
st.header(Bagian + " Casing Design")

# Persamaan Pressure
Pressure_eq = lambda Density, Depth : 0.052 * Density * Depth

# Rumus Burst IP
IP_surface = lambda Density, Depth : 0.052 * Density * Depth
IP_intermediate = lambda Density, Depth : 0.052 * Density * Depth
IP_production = lambda Pressure, Density, Depth : Pressure + 0.052 * Density * Depth

# Rumus Burst Ps
Ps_surface = lambda Density, Gradient_gas, Depth : (0.052 * Density - Gradient_gas) * Depth
Ps_intermediate = lambda Pressure : Pressure
Ps_production = lambda Pressure : Pressure

# Rumus Burst Pe
Pe_burst = lambda Density, Depth : 0.052 * Density * Depth

# Rumus Collapse
Pe_collapse = lambda Density, Depth : 0.052 * Density * Depth

# Rumus Tension
Force = lambda Density, Depth, weight : 0.052 * Density * Depth * weight * 144 / 490

# Rumus Biaxial
Biaxial_ratio = lambda Correction, Resistance : Correction / Resistance
Biaxial_curve = lambda Y : ((-0.52 * Y) + (0.2704 * Y**2 - 4 * ( Y**2 - 1 ))**0.5) / 2
x_distance = lambda X, Body_yield, Weight, Buoyancy, weight : ((X * Body_yield) - Weight - Buoyancy) / weight

# Example Parameter Surface - Intermediate - Production
if Bagian == "Surface": Parameter = [13.375, 3000, 1000, "Minimum", 12.259, "Maximum", 14.001, 8.942, None, None, 11, 1.1, 1.1, 1.6, None]
if Bagian == "Intermediate": Parameter = [7.625, 12000, 2500, "Minimum", 6.5, "Minimum", 17.501, 8.942, None, 14.7, 10.8, 1.1, 1.1, 1.6, 8000]
if Bagian == "Production": Parameter = [5.5, 11000, 3, "Minimum", 4.001, "Maximum", None, 8.942, 8.942, None, 12.8, 1.1, 1.1, 1.6, 5400]

# Tab
Tab_Variabel, Tab_Subs, Tab_Cement, Tab_Burst_Collapse, Tab_Tension_Biaxial, Tab_Result = st.tabs(["Casing Variable", "Subsurface Variable", "Mud - Cement", "Burst - Collapse", "Tension - Biaxial", "Casing Design"])

# Tab Variabel
with Tab_Variabel: 

    # Opsi Variasi OD Casing
    Casing.OD = Class_.OD_index(Casing_subset_OD, Parameter)
    if Catalog_select == "Manual":
        with Tab_Variabel: Cas_Manual, Cas_Total = st.columns([15,1])
        with Cas_Total: ss["Cas_Total"] = st.number_input("Total", min_value=1, value=1)
        with Cas_Manual: Class_.Manual_data(ss["Cas_Total"], Casing.OD, Casing_data[Casing_data['1_Size Outside Diameter in. D'] == Casing.OD], Grade_5C3)
        Manual_data = pd.concat([Casing_data[Casing_data.iloc[:,0] == 0], Class_.Manual_data_pandas(ss).dropna()], ignore_index = True)
    
    import Custom_Casing as Custom_Casing
    if Catalog_select == "Manual":
        try: st.write(Custom_Casing.Session[f"OD_{Casing.OD}"])
        except:
            st.warning("Input Custom Casing Parameters")
            st.stop()

    # Pembagian Kolom Variabel
    Variabel_left, Variabel_mid, Variabel_right = st.columns(3) 
    
    # Kedalaman Casing MD --- MD_ft = df_Input.iloc[list(df_Input.iloc[:,0]).index(f"MD_ft_{Bagian}"),1] 
    with Variabel_left: MD_ft = Class_.MD_ft(Parameter)
    Casing.MD = MD_ft.iloc[0,0]
    
    # Length Section
    with Variabel_mid: Section = Class_.Section(Parameter, Casing.MD)
    Casing.Section_value = Section.iloc[0,0]
    Casing.Section = Section.iloc[0,1]

    # Drift Diameter
    if Catalog_select == "Manual": Casing.Subset_drift(Manual_data, Casing.OD)
    else: Casing.Subset_drift(Casing_data, Casing.OD)
    with Variabel_right: Drift = Class_.Drift(Parameter, Casing.Subset_Drift)
    Casing.Drift_value = Drift.iloc[0,0]
    Casing.Drift = Drift.iloc[0,1]

with Tab_Subs:
    Subs_left, Subs_mid, Subs_right = st.columns(3) 
    
    # Gradient Fracture
    with Subs_mid: Casing.Gfr = Class_.Gradient_Fracture(Parameter, Bagian)

    # Gradient Gas
    with Subs_right: Casing.Gg = Class_.Gradient_Gas(Bagian, Load)

    # Fluid Density
    with Subs_left: Casing.Fluid = Class_.Fluid_density(Parameter)

    # Pembagian Kolom Variabel
    Subs_Packer, Subs_Ps = st.columns([1,2]) 
    
    # Packer Density
    with Subs_Packer: Casing.Packer = Class_.Packer_density(Parameter, Bagian)
    
    # Design Factor
    Design_Factor = Class_.Design_Factor()
    Casing.DF_Burst = Design_Factor.iloc[0,0]
    Casing.DF_Collapse = Design_Factor.iloc[0,1]
    Casing.DF_Tension = Design_Factor.iloc[0,2]
    
    # Surface Pressure
    with Subs_Ps: Casing.Ps = Class_.Surface_Pressure(Bagian, Load, Parameter, Casing)

with Tab_Cement:
    
    Variabel_Drill, Variabel_Heavy = st.columns(2)

    # Heavy Mud Density
    with Variabel_Heavy: Casing.Heavy = Class_.Heavy_density(Parameter, Bagian)

    # Drill Mud Density
    with Variabel_Drill: Casing.Drill = Class_.Drill_density(Parameter)
    
    # Cement
    def jumlah_(): # Edit Value Cement Top dan Density Pertama Setelah Jumlah Variasi Berubah
        st.session_state.Top_0 = 0
        st.session_state.Density_0 = 10.00

    Cement_No, Cement_Depth, Cement_Range, Cement_Density, Cement_Jumlah = st.columns([1, 4, 4, 4, 2]) # Pembagian Kolom Variasi Cement Depth
    with Cement_Jumlah: jumlah = st.selectbox('Variation', (1, 2, 3, 4, 5), key="jumlah", on_change=jumlah_) # Kolom 5 (Jumlah Variasi Cement Depth)

    def Top_(): # Koreksi Value Cement Top (ft) Setelah Berubah
        if Bagian == "Surface": st.session_state.Top_0 = int(0)
        for x in range (jumlah):
            if st.session_state[f"Top_{x}"] != cement_list[x]:
                if x == 0: 
                    if  st.session_state[f"Top_{x}"] >= cement_list[x+1]: 
                        st.session_state[f"Top_{x}"] = cement_list[x] = int(cement_list[x+1] - 100)
                        break
                else:
                    if   st.session_state[f"Top_{x}"] <= cement_list[x-1]: 
                        st.session_state[f"Top_{x}"] = cement_list[x] =  int(cement_list[x-1] + 100)
                        break
                    elif st.session_state[f"Top_{x}"] >= cement_list[x+1]: 
                        st.session_state[f"Top_{x}"] = cement_list[x] =  int(cement_list[x+1] - 100)
                        break
                    
    ppg_list = [] # List (ppg) Awal Parameter Cement
    cement_list = [] # List (ft) Awal Parameter Cement

    @lru_cache(maxsize=None)
    def cement_data():
        
        for x in range(jumlah):
            ppg_list.append(10 + x)
            cement_list.append(Casing.MD / jumlah * x)
            with Cement_No: st.text_input("No", f"{x+1}", key=f"No_{x}", disabled=True, label_visibility="visible" if x == 0 else "collapsed")
            with Cement_Depth: st.number_input("Cement Depth (ft)", value=int(cement_list[x]), min_value=0, max_value=int(Casing.MD - 100), key=f"Top_{x}", on_change=Top_, label_visibility="visible" if x == 0 else "collapsed")
            with Cement_Density: st.number_input("Density (ppg)", value=float(ppg_list[x]), min_value=float(0.00), key=f"Density_{x}", label_visibility="visible" if x == 0 else "collapsed")
            if x == (jumlah - 1): cement_list.append(int(Casing.MD))
        
        for x in range (jumlah):
            cement_list[x] = st.session_state[f"Top_{x}"]
            ppg_list[x] = st.session_state[f"Density_{x}"]
            if x == (jumlah - 1):
                st.session_state.cement_list = cement_list
                st.session_state.ppg_list = ppg_list

        for x in range (jumlah):
            with Cement_Range: st.text_input("Range", f"{int(cement_list[x])} - {int(cement_list[x+1])} ft", key=f"Range_{x}", disabled=True, label_visibility="visible" if x == 0 else "collapsed")

    cement_data()
    cement_delta = [cement_list[0]] + [cement_list[x + 1] - cement_list[x] for x in range(jumlah)]
    cement_delta_pressure = [Pressure_eq(density, depth) for density, depth in zip([Casing.Drill] + ppg_list, cement_delta)]

with Tab_Burst_Collapse:Burst_side, Collapse_side = st.columns(2) # Pembagian Kolom Burst-Collapse
with Burst_side:
    st.subheader("Burst Load")
    # Safety Factor
    if Bagian != "Production": Casing.SF = st.number_input("Safety Factor", value=1.00 if Load == "Maximum Load" else 0, placeholder="Input Safety Factor...", disabled=False if Load == "Maximum Load" else True)

# Burst IP
if Bagian == "Surface": Casing.Burst_IP = IP_surface(Casing.Gfr + Casing.SF if Load == "Maximum Load" else Casing.Gfr, Casing.MD)
elif Bagian == "Intermediate": Casing.Burst_IP = IP_intermediate(Casing.Gfr + Casing.SF if Load == "Maximum Load" else Casing.Gfr, Casing.MD)
elif Bagian == "Production": Casing.Burst_IP = IP_production(Casing.Ps, Casing.Packer, Casing.MD)

# Burst Ps
if Bagian == "Surface": Casing.Burst_Ps = Ps_surface(Casing.Gfr + Casing.SF if Load == "Maximum Load" else Casing.Gfr, Casing.Gg if Load == "Maximum Load" else 0, Casing.MD)
elif Bagian == "Intermediate": Casing.Burst_Ps = Ps_intermediate(Casing.Ps)
elif Bagian == "Production": Casing.Burst_Ps = Ps_production(Casing.Ps)

# Burst Hg
if Bagian == "Intermediate" and Load == "Maximum Load": Casing.Burst_Hg = (Casing.Burst_IP - Casing.Burst_Ps - Pressure_eq(Casing.Heavy, Casing.MD)) / (Casing.Gg - 0.052 * Casing.Heavy)

# Burst Pe
if Bagian == "Production": Casing.Burst_Pe = Pe_burst(Casing.Packer, Casing.MD)
elif Bagian == "Intermediate" and Load == "Minimum Load": Casing.Burst_Pe = sum(cement_delta_pressure)
else: Casing.Burst_Pe = Pe_burst(Casing.Fluid, Casing.MD)

# Burst Rule
Casing.Burst(Bagian, Load, Pe_burst, cement_list, cement_delta_pressure)

with Burst_side:
    
    Burst_table = pd.DataFrame({"Depth":Casing.Burst_depth, "A_psi":Casing.Burst_A, "B_psi":Casing.Burst_B})
    Burst_table["C_psi"] = round(Burst_table["A_psi"] - Burst_table["B_psi"], 2)
    Burst_table["D_psi"] = round(Burst_table["C_psi"] * Casing.DF_Burst, 2)
    st.dataframe(Burst_table, column_config=
        {
            "A_psi":st.column_config.NumberColumn(help="Burst Load Inside Casing"),
            "B_psi":st.column_config.NumberColumn(help="Burst Load Outside Casing"),
            "C_psi":st.column_config.NumberColumn(help="Burst Load Resultant = A - B"),
            "D_psi":st.column_config.NumberColumn(help=f"Burst Load Design = C x {Casing.DF_Burst}")
        },
        use_container_width=True, hide_index=True)
    Casing.Burst_design = pd.DataFrame({"Depth":Burst_table.iloc[:,0], "Design":Burst_table.iloc[:,4]})
    st.altair_chart(Class_.altair_chart(pd.melt(Burst_table, id_vars=["Depth"], value_vars=[i for i in Burst_table.columns if i != "Depth"]), "Burst (psi)", Casing.MD), theme="streamlit", use_container_width=True)

# Collapse Pe
if Bagian == "Surface" and Load == "Minimum Load": Casing.Collapse_Pressure = Pe_collapse(Casing.Fluid, Casing.MD)

# Collapse P3
if Bagian == "Intermediate" and Load == "Maximum Load": Casing.Collapse_D3 = (Pressure_eq(Casing.Heavy, Casing.MD) - Pressure_eq(Casing.Fluid, Casing.MD)) / (0.052 * Casing.Heavy)
elif Bagian == "Intermediate" and Load == "Minimum Load": Casing.Collapse_D3 = 0.5 * Casing.MD
if Bagian == "Intermediate": Casing.Collapse_P3 = Pe_collapse(Casing.Heavy, Casing.MD - Casing.Collapse_D3)

# Collapse Rule
Casing.Collapse(Bagian, Load, cement_delta, cement_delta_pressure, ppg_list, cement_list, Pressure_eq)

with Collapse_side:
    st.subheader("Collapse Load")
    st.dataframe(Casing.Collapse_table, column_config=
        {
            "A_psi":st.column_config.NumberColumn(help="Minimum Formation Pressure at The Bottom of Casing" if Bagian == "Intermediate" else "Collapse Load Resultant"),
            "B_psi":st.column_config.NumberColumn(help="Hydrostatic Pressure" if Bagian == "Intermediate" else f"Collapse Load Design = A x {Casing.DF_Collapse}"),
            "C_psi":st.column_config.NumberColumn(help="Collapse Load Resultant = B - A"),
            "D_psi":st.column_config.NumberColumn(help=f"Collapse Load Design = C x {Casing.DF_Collapse}"),
            "M2":st.column_config.NumberColumn(help="0.052 x Heavy Mud Density x Depth")
        },
        use_container_width=True, hide_index=True)
    Casing.Collapse_design = pd.DataFrame({"Depth":Casing.Collapse_table.iloc[:,0], "Design":Casing.Collapse_table.iloc[:,4] if Bagian == "Intermediate" else Casing.Collapse_table.iloc[:,2]})
    st.altair_chart(Class_.altair_chart(pd.melt(Casing.Collapse_table, id_vars=["Depth"], value_vars=[i for i in Casing.Collapse_table.columns if i != "Depth"]), "Collapse (psi)", Casing.MD), theme="streamlit", use_container_width=True)

with Tab_Tension_Biaxial:
    st.subheader("Tension Load")
    Casing_grade, Casing_combination = st.columns(2) # Pembagian Kolom Variasi Casing

with Casing_grade: Overpull = st.data_editor(pd.DataFrame({"Overpull Tension Load (lbs)":[100000]}), use_container_width=True, hide_index=True)
Casing.Tension_Overpull = Overpull.iloc[0,0]

Section_alt_name = "Minimum" if Casing.Section == "Maximum" else "Maximum"
Section_alt_min = int(3 if Casing.Section == "Maximum" else ((Casing.Section_value//3) * 3 if Casing.Section_value//3 == Casing.Section_value/3 else (Casing.Section_value//3 + 1) * 3))
Section_alt_max = int((Casing.Section_value//3) * 3 if Casing.Section == "Maximum" else Casing.MD)
with Casing_combination: Section_alt = st.data_editor(pd.DataFrame({f"{Section_alt_name} Length Section (ft)":[3 if Casing.Section == "Maximum" else Casing.MD]}), column_config=
    {
        f"{Section_alt_name} Length Section (ft)": st.column_config.NumberColumn(help=f"Minimum Length {Section_alt_min} ft and Maximum Length {Section_alt_max} ft", min_value= Section_alt_min, max_value= Section_alt_max,)
    },
    use_container_width=True, hide_index=True)
Casing.Section_alt = Section_alt.iloc[0,0]

# HARUSNYA DISINI PARAMETER CASING NYA
if Catalog_select == "Manual": Manual.Parameter_df(Manual_data, Casing)
Catalog.Parameter_df(Casing_data, Casing)
with Casing_grade: 
    if Catalog_select == "Manual": Grade_drop = st.multiselect("Casing Grade", Manual.Para_df.iloc[:,2].drop_duplicates())
    else: Grade_drop = st.multiselect("Casing Grade", Catalog.Para_df.iloc[:,2].drop_duplicates())
if Catalog_select == "Manual": Manual.Parameter_sort(Grade_drop)
Catalog.Parameter_sort(Grade_drop)

# Penentuan Section Max-Min Casing 
Set_Section_max = Casing.Section_alt if Casing.Section == "Minimum" else Casing.Section_value
Set_Section_min = Casing.Section_alt if Casing.Section == "Maximum" else Casing.Section_value
with Casing_combination: Iterasi_max = st.selectbox("Maximum Casing Combination", (ceil(Casing.MD/Set_Section_max) + i for i in range(10)))

if Catalog_select == "Manual": Manual.Preparation()
Catalog.Preparation()

start = time()
if Catalog_select == "Manual": 
    with Casing_grade: Manual.Design("Manual", Iterasi_max, Casing, Biaxial_curve, Biaxial_ratio, Force, Set_Section_min, Set_Section_max)
with (Casing_combination if Catalog_select == "Manual" else Tab_Tension_Biaxial):
    Catalog.Design("API 5C2", Iterasi_max, Casing, Biaxial_curve, Biaxial_ratio, Force, Set_Section_min, Set_Section_max)

if Catalog_select == "Manual": 
    with Casing_grade: Manual.Concat(Biaxial_curve, Casing)
with (Casing_combination if Catalog_select == "Manual" else Tab_Tension_Biaxial):
    Catalog.Concat(Biaxial_curve, Casing)

if Catalog_select == "Manual": Manual_intersection = Class_.Table_intersection(Manual, Manual.Tension_Table)
Catalog_intersection = Class_.Table_intersection(Catalog, Catalog.Tension_Table)
def Table_intersect_df(name, weight, depth_end, depth_start, Load_bot, Resist, burst, collapse):
    Table_intersect = pd.DataFrame(
        {
            "Depth":[depth_end + i*3 for i in range((depth_start - depth_end)//3 + 1)] + 
            ([] if ((depth_start - depth_end)//3)*3 == (depth_start - depth_end) else [depth_start])
        })
    Table_intersect[f"X {name}"] = ((weight * (depth_start - Table_intersect["Depth"])) + Load_bot) / Resist
    Table_intersect[f"Y {name}"] = Biaxial_curve(Table_intersect[f"X {name}"])
    Table_intersect[f"Burst {name}"] = burst / Table_intersect[f"Y {name}"]
    Table_intersect[f"Collapse {name}"] = Table_intersect[f"Y {name}"] * collapse
    return Table_intersect.set_index("Depth")
    
Burst_des = Class_.altair_chart(pd.melt(Casing.Burst_design, id_vars=["Depth"], value_vars=[i for i in Casing.Burst_design.columns if i != "Depth"]), "Burst (psi)", Casing.MD)
Coll_des = Class_.altair_chart(pd.melt(Casing.Collapse_design, id_vars=["Depth"], value_vars=[i for i in Casing.Collapse_design.columns if i != "Depth"]), "Collapse (psi)", Casing.MD)    

def Pd_Altair(tbl, x_axis): return Class_.altair_chart(pd.melt(tbl, id_vars=["Depth"], value_vars=[i for i in tbl.columns if i != "Depth"]), x_axis, Casing.MD)
def Altair_sort_Bu(self, Altair):
    
    loc = self.location
    #  + Pd_Altair(self.Altair.iloc[loc-1,9], "Burst (psi)")
    st.dataframe(self.Altair.iloc[loc-1,9].sort_values("Depth"), use_container_width=True, hide_index=True)
    st.altair_chart(Burst_des + Altair, theme="streamlit", use_container_width=True)

def Altair_sort_Co(self, Altair):
    
    loc = self.location
    #  + Pd_Altair(self.Altair.iloc[loc-1,1], "Collapse (psi)")
    st.dataframe(self.Altair.iloc[loc-1,1].sort_values("Depth"), use_container_width=True, hide_index=True)
    st.altair_chart(Coll_des + Altair, theme="streamlit", use_container_width=True)
    
def Altair_sort_TenBix(self):
    
    loc = self.location
    Tension_Load = pd.melt(self.Altair.iloc[loc-1,3], id_vars=["Depth"], value_vars=[i for i in self.Altair.iloc[loc-1,3].columns if i != "Depth"])
    Tension_Load_over = pd.melt(self.Altair.iloc[loc-1,4], id_vars=["Depth"], value_vars=[i for i in self.Altair.iloc[loc-1,3].columns if i != "Depth"])
    Tension_Load_DF = pd.melt(self.Altair.iloc[loc-1,5], id_vars=["Depth"], value_vars=[i for i in self.Altair.iloc[loc-1,3].columns if i != "Depth"])
    
    Tension_Load["variable"] = "Load"
    Tension_Load_over["variable"] = "Load + Overpull"
    Tension_Load_DF["variable"] = "Load x DF_Tension"
    
    st.dataframe(pd.DataFrame({"Depth":Tension_Load["Depth"], "Load":Tension_Load["value"], "Load + Overpull":Tension_Load_over["value"], "Load x DF_Tension":Tension_Load_DF["value"]}).dropna().reset_index(drop="index").sort_index(ascending=False), use_container_width=True, hide_index=True)
    st.dataframe(self.Altair.iloc[loc-1,2].sort_values("Depth"), use_container_width=True, hide_index=True)
    st.altair_chart(
        Class_.altair_chart(Tension_Load.dropna(), "Tension (lbs)", Casing.MD) + Class_.altair_chart(Tension_Load_over.dropna(), "Tension (lbs)", Casing.MD) +
        Class_.altair_chart(Tension_Load_DF.dropna(), "Tension (lbs)", Casing.MD) + Pd_Altair(self.Altair.iloc[loc-1,2], "Tension (lbs)"),
        theme="streamlit", use_container_width=True) 
    
def Altair_sort_Bix_XY(self, df):

    loc = self.location
    # st.dataframe(df, use_container_width=True)
    df_XY = [Table_intersect_df(name, weight, int(depth[1]), int(depth[0]), load[0], tension, burst, collapse) for name, weight, depth, load, tension, burst, collapse in zip(df.iloc[loc-1,0], df.iloc[loc-1,1], df.iloc[loc-1,6], df.iloc[loc-1,5], df.iloc[loc-1,4], df.iloc[loc-1,2], df.iloc[loc-1,3])]
    df_XY_Burst = pd.concat(reversed([df.iloc[:,2] for df in df_XY]), axis=1).rename(columns={list(col.columns)[2]:name for col, name in zip(df_XY, df.iloc[loc-1,0])})
    df_XY_Collapse = pd.concat(reversed([df.iloc[:,3] for df in df_XY]), axis=1).rename(columns={list(col.columns)[3]:name for col, name in zip(df_XY, df.iloc[loc-1,0])})
    with st.expander("Biaxial XY"): st.dataframe(pd.concat(reversed([df.iloc[:,:2] for df in df_XY]), axis=1), use_container_width=True)
    df_XY_Burst_Altair = Class_.altair_chart(pd.melt(df_XY_Burst.reset_index(), id_vars=["Depth"], value_vars=[i for i in df_XY_Burst.columns if i != "Depth"]), "Burst (psi)", Casing.MD)
    df_XY_Collapse_Altair = Class_.altair_chart(pd.melt(df_XY_Collapse.reset_index(), id_vars=["Depth"], value_vars=[i for i in df_XY_Collapse.columns if i != "Depth"]), "Collapse (psi)", Casing.MD)
    
    st.write("Biaxial Burst Correction") #  + Pd_Altair(self.Altair.iloc[loc-1,9], "Burst (psi)")
    st.altair_chart(df_XY_Burst_Altair + Pd_Altair(self.Altair.iloc[loc-1,0], "Burst (psi)"), theme="streamlit", use_container_width=True)
    with st.expander("Burst Correction"): st.dataframe(df_XY_Burst, use_container_width=True)
    st.write("Biaxial Collapse Correction") #  + Pd_Altair(self.Altair.iloc[loc-1,1], "Collapse (psi)")
    st.altair_chart(df_XY_Collapse_Altair + Pd_Altair(self.Altair.iloc[loc-1,8], "Collapse (psi)"), theme="streamlit", use_container_width=True)
    with st.expander("Collapse Correction"): st.dataframe(df_XY_Collapse, use_container_width=True)
    
    return [df_XY_Burst_Altair, df_XY_Collapse_Altair]
    
if Catalog_select == "Manual":
    with Casing_grade: Manual.location = 1 if len(Manual.Tension_Table) == 1 else st.slider("Casing Combination", 1, 10 if len(Manual.Tension_Table) > 10 else len(Manual.Tension_Table), 1)
with (Casing_combination if Catalog_select == "Manual" else Tab_Tension_Biaxial):
    Catalog.location = 1 if len(Catalog.Tension_Table) == 1 else st.slider("Casing Combination", 1, 10 if len(Catalog.Tension_Table) > 10 else len(Catalog.Tension_Table), 1)

if Catalog_select == "Manual": 
    with Casing_grade: Altair_sort_TenBix(Manual)
with (Casing_combination if Catalog_select == "Manual" else Tab_Tension_Biaxial): 
    Altair_sort_TenBix(Catalog)

with Tab_Tension_Biaxial:
    st.subheader("Biaxial Load")
    Casing_manual, Casing_catalog = st.columns(2) # Pembagian Kolom Chart
    
if Catalog_select == "Manual": 
    with Casing_manual: Manual_XY_Altair = Altair_sort_Bix_XY(Manual, Manual_intersection)
with (Casing_catalog if Catalog_select == "Manual" else Tab_Tension_Biaxial): 
    Catalog_XY_Altair = Altair_sort_Bix_XY(Catalog, Catalog_intersection)

def Casing_design_used(self): return self.Parameter.loc[[comb for comb in self.Tension_Table.iloc[self.location-1,0]]].rename(columns={col:name for col, name in zip(self.Parameter.columns, Class_.Parameter_column_name())})
with Tab_Result:
    manual_parameter, catalog_parameter = st.columns(2)
    if Catalog_select == "Manual": 
        with manual_parameter: st.dataframe(Casing_design_used(Manual), use_container_width=True)
    with (catalog_parameter if Catalog_select == "Manual" else Tab_Result): 
        st.dataframe(Casing_design_used(Catalog), use_container_width=True)
    st.subheader("Casing Performance Against Burst")
    Result_manual, Result_catalog = st.columns(2)
    
if Catalog_select == "Manual": 
    with Result_manual: Altair_sort_Bu(Manual, Manual_XY_Altair[0])
with (Result_catalog if Catalog_select == "Manual" else Tab_Result): 
    Altair_sort_Bu(Catalog, Catalog_XY_Altair[0])

with Tab_Result:
    st.subheader("Casing Performance Against Collapse")
    Result_manual_, Result_catalog_ = st.columns(2)
    
if Catalog_select == "Manual": 
    with Result_manual_: Altair_sort_Co(Manual, Manual_XY_Altair[1])
with (Result_catalog_ if Catalog_select == "Manual" else Tab_Result): 
    Altair_sort_Co(Catalog, Catalog_XY_Altair[1])
    st.write(round(time() - start, 2))
