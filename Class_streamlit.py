import streamlit as st
import pandas as pd
from functools import lru_cache
import Class_
import redis
import numpy as np
import altair as alt

redis_client = redis.Redis(host="localhost", port=6379, db=0)

# Data Mentah Properties Casing Design
Casing_data_ = pd.read_excel(io='Casing_Simplify.xlsx', skiprows=[0, 1], header=[0]) 

# Data Rapih Properties Casing Design
Casing_data  = Casing_data_[Casing_data_.iloc[:, 16] != "—"]
Grade_5C3 = ["H-40", "-50", "J-55", "K-55", "-60", 'M-65', "-70", "C-75", "E-75", "L-80", "N-80", "C-90", "C-95", "T-95", "X-95", "-100", "P-105", "G-105", "P-110", 
             "-120", "Q-125", "-130", "S-135", "-140", "-150", "-155", "-160", "-170", "-180"]

# Variasi Data OD Casing Design
Casing_subset_OD = Casing_data.drop_duplicates(subset='1_Size Outside Diameter in. D').reset_index(drop="index")

with st.expander("Pilih Bagian dan Load Casing Design"):

    # Pembagian Kolom Pertama
    Expander_1, Expander_2, Expander_3 = st.columns(3) 
    
    # Expand Bagian Casing Design
    with Expander_1: Bagian = st.selectbox('How',("Surface", "Intermediate", "Production"), label_visibility="collapsed")

    # Expand Jenis Casing Load Design MAXIMUM atau MINIMUM
    with Expander_2: Load = st.selectbox('Load',("Maximum Load", "Minimum Load"), label_visibility="collapsed")

    # Catalog atau Manual
    with Expander_3: Catalog = st.selectbox('Catalog',("Catalog", "Manual"), label_visibility="collapsed")

Casing = Class_.Variabel()
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

# Tab
Tab_Variabel, Tab_Burst_Collapse, Tab_Tension_Biaxial, Tab_Result = st.tabs(["Variabel", "Burst - Collapse", "Tension - Biaxial", "Casing Design"])

# Example Parameter Surface - Intermediate - Production
if Bagian == "Surface": Parameter = [13.375, 3000, 1000, "Minimum", 12.259, "Maximum", 14.001, 8.942, None, None, 11, 1.1, 1.1, 1.6, None]
if Bagian == "Intermediate": Parameter = [7.625, 12000, 2500, "Minimum", 6.5, "Minimum", 17.501, 8.942, None, 14.7, 10.8, 1.1, 1.1, 1.6, 8000]
if Bagian == "Production": Parameter = [5.5, 11000, 3, "Minimum", 4.001, "Maximum", None, 8.942, 8.942, None, 12.8, 1.1, 1.1, 1.6, 5400]

with Tab_Variabel: # Tab Variabel
    Variabel_key = f"{Bagian}_{Load}_Variabel"

    # Opsi Variasi OD Casing
    Casing.OD = Class_.OD_index(Casing_subset_OD, Parameter)

    # Kedalaman Casing MD
    Casing.MD = Class_.MD_ft(Parameter)

    # Length Section
    Section = Class_.Section(Parameter, Casing.MD)
    Casing.Section_value = Section.iloc[0,0]
    Casing.Section = Section.iloc[0,1]

    # Drift Diameter
    Casing_subset_drift = Casing_data[Casing_data.iloc[:,0]==Casing.OD].drop_duplicates(subset='6_Drift Diameter in.').reset_index(drop="index")
    Drift = Class_.Drift(Parameter, Casing_subset_drift)
    Casing.Drift_value = Drift.iloc[0,0]
    Casing.Drift = Drift.iloc[0,1]

    # Gradient Fracture
    Casing.Gfr = Class_.Gradient_Fracture(Parameter, Bagian)

    # Gradient Gas
    Casing.Gg = Class_.Gradient_Gas(Bagian, Load)

    # Fluid Density
    Casing.Fluid = Class_.Fluid_density(Parameter)

    # Packer Density
    Casing.Packer = Class_.Packer_density(Parameter, Bagian)

    # Heavy Mud Density
    Casing.Heavy = Class_.Heavy_density(Parameter, Bagian)

    # Drill Mud Density
    Casing.Drill = Class_.Drill_density(Parameter)

    # Design Factor
    Design_Factor = Class_.Design_Factor()
    Casing.DF_Burst = Design_Factor.iloc[0,0]
    Casing.DF_Collapse = Design_Factor.iloc[0,1]
    Casing.DF_Tension = Design_Factor.iloc[0,2]

    # Surface Pressure
    Casing.Ps = Class_.Surface_Pressure(Bagian, Load, Parameter, Casing)

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

with Tab_Burst_Collapse:
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

with Tab_Burst_Collapse:
    
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
    
# Collapse Pe
if Bagian == "Surface" and Load == "Minimum Load": Casing.Collapse_Pressure = Pe_collapse(Casing.Fluid, Casing.MD)

# Collapse P3 
if Bagian == "Intermediate" and Load == "Maximum Load": Casing.Collapse_D3 = (Pressure_eq(Casing.Heavy, Casing.MD) - Pressure_eq(Casing.Fluid, Casing.MD)) / (0.052 * Casing.Heavy)
elif Bagian == "Intermediate" and Load == "Minimum Load": Casing.Collapse_D3 = 0.5 * Casing.MD
if Bagian == "Intermediate": Casing.Collapse_P3 = Pe_collapse(Casing.Heavy, Casing.MD - Casing.Collapse_D3)

# Collapse Rule
Casing.Collapse(Bagian, Load, cement_delta, cement_delta_pressure, ppg_list, cement_list, Pressure_eq)

with Tab_Burst_Collapse:
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

with Tab_Tension_Biaxial:
    st.subheader("Tension Load")
    
    Overpull = st.data_editor(pd.DataFrame({"Overpull Tension Load (lbs)":[100000]}), use_container_width=True, hide_index=True)
    Casing.Tension_Overpull = Overpull.iloc[0,0]
    
    Section_alt_name = "Minimum" if Casing.Section == "Maximum" else "Maximum"
    Section_alt_min = int(3 if Casing.Section == "Maximum" else ((Casing.Section_value//3) * 3 if Casing.Section_value//3 == Casing.Section_value/3 else (Casing.Section_value//3 + 1) * 3))
    Section_alt_max = int((Casing.Section_value//3) * 3 if Casing.Section == "Maximum" else Casing.MD)
    Section_alt = st.data_editor(pd.DataFrame({f"{Section_alt_name} Length Section (ft)":[3 if Casing.Section == "Maximum" else Casing.MD]}), column_config=
        {
            f"{Section_alt_name} Length Section (ft)": st.column_config.NumberColumn(help=f"Minimum Length {Section_alt_min} ft and Maximum Length {Section_alt_max} ft", min_value= Section_alt_min, max_value= Section_alt_max,)
        },
        use_container_width=True, hide_index=True)
    Casing.Section_alt = Section_alt.iloc[0,0]
    
Parameter = Casing_data[(Casing_data.iloc[:,0]==Casing.OD) & (Casing_data.iloc[:,5] <= Casing.Drift_value if Casing.Drift == "Maximum" else Casing_data.iloc[:,5] >= Casing.Drift_value)].replace("—", None)
with Tab_Tension_Biaxial: Grade_drop = st.multiselect("Casing Grade", Parameter.iloc[:,2].drop_duplicates())
Parameter = Parameter.iloc[:, [0, 1, 2, 5, 11, 12, 16, 23]]

Para_Grade = pd.DataFrame({"Grade":Parameter.iloc[:,2]})
Para_Grade["Split"] = Para_Grade["Grade"].str.split("-")
Para_Split = pd.DataFrame({"Split_A":[split[0] for split in Para_Grade["Split"]], "Split_B":[int(split[1]) for split in Para_Grade["Split"]], "Grade":Parameter.iloc[:,2]}).replace("","A")
add_index = Para_Split[Para_Split.iloc[:,0] == 0]
for value in Para_Split.sort_values(by=["Split_B"]).iloc[:,1].drop_duplicates():
    add = Para_Split[Para_Split.iloc[:,1] == value].sort_values(by=["Split_A"])
    add_index = pd.concat([add_index, add])

if len(Parameter) > 1: # Mengurutkan Casing Properties Berdasarkan Nominal Weight dan Grade (dari index)
    Casing.Parameter = Parameter[Parameter.iloc[:,2] == 0]
    for weight in sorted(Parameter.iloc[:,1].drop_duplicates()):
        add_weight = Parameter[Parameter.iloc[:,1] == weight]
        for grade in add_index["Grade"].drop_duplicates():
            add = add_weight[add_weight.iloc[:,2] == grade]
            if len(add) == 0: continue
            else: Casing.Parameter = pd.concat([Casing.Parameter, add], ignore_index = True)
else: Casing.Parameter = Parameter
Casing.Parameter.index = Casing.Parameter.index + 1
Casing.Parameter = Casing.Parameter[Casing.Parameter.iloc[:,2].isin(Grade_drop) == True if len(Grade_drop) != 0 else Casing.Parameter.iloc[:,2].isin(Grade_drop) == False]

def call(row, col): return Casing.Parameter.loc[row,Casing.Parameter.columns[col]]
def Between(df, value, known, find):
    Limit = pd.concat([df, pd.DataFrame({known:[value], find:[np.nan]})])
    Limit = Limit.sort_values(known, ascending=(True if known == "Depth" else False)).set_index(known).interpolate(method='index')
    try: return next(iter(set(Limit[find]) - set(df[find])))
    except: return df[df[known] == value].reset_index(drop="index").loc[0,find]

# Penentuan Section Max-Min Casing 
Set_Section_max = Casing.Section_alt if Casing.Section == "Minimum" else Casing.Section_value
Set_Section_min = Casing.Section_alt if Casing.Section == "Maximum" else Casing.Section_value

@lru_cache(maxsize=None) 
def Tension_Biaxial(index):
    Susunan_Casing = []
    Susunan_Depth = []
    Susunan_Load = []
    Susunan_Collapse = []
    Casing.Tension()
    for z in index:
        if min(Casing.Tension_Depth) == 0: break
        if call(z, 4) < Between(Casing.Collapse_design, min(Casing.Tension_Depth), "Depth", "Design"): break
        elif  call(z, 6) < Between(Casing.Burst_design, min(Casing.Tension_Depth), "Depth", "Design"): break
        
        # Burst Check
        Burst_check = Casing.Burst_design[Casing.Burst_design.iloc[:,1] >= call(z, 6)]
        try: Tension_Burst = ((Casing.MD - Between(Casing.Burst_design[Casing.Burst_design.iloc[:,0] >= Burst_check.iloc[-1,0]], call(z, 6), "Design", "Depth"))//3)*3
        except: Tension_Burst = Casing.MD
        
        Casing.Biaxial_X = Biaxial_curve(Biaxial_ratio(Between(Casing.Collapse_design, min(Casing.Tension_Depth), "Depth", "Design"), call(z, 4)))
        Casing.Tension_Resist = min([call(z, 5), call(z, 7)]) * 1000 # Yield or Joint
        
        # Weight (lb) = weight_unit (lb/ft) * Tension_Depth (ft) ==> used
        Weight = [0] if len(Casing.Tension_weight) == 0 else [weight * (depth[0] - depth[1]) for weight, depth in zip(Casing.Tension_weight, Susunan_Depth)]
        
        # weight_unit (lb/ft)
        Casing.Tension_weight.append(call(z, 1))
        
        # Force (lb) = pressure (psi = lb/sq in) * Cross Sectional Area (sq in)
        force_ = [0] + [Force(Casing.Drill, depth, weight)for depth, weight in zip(Casing.Tension_Depth, Casing.Tension_weight)]
        force_sum = [force_[i] - force_[i + 1] for i in range(len(Casing.Tension_weight))]
        
        # Menentukan Kemampuan Panjang Collapse Yang Mampu Ditahan Oleh Casing
        Collapse_length = ( (Casing.Biaxial_X * Casing.Tension_Resist) - sum(Weight) - sum(force_sum) ) / call(z, 1)

        # Set Section Casing Minimum Pada Kelipatan 3ft - [0] Length Casing Sisa - [1] Collapse Length - [2] Section Limit - [3] Burst Check ===> Kemampuan Length Casing Dari Body Yield
        Tension_length = min([min(Casing.Tension_Depth), (Collapse_length//3)*3, (Set_Section_max//3)*3, Tension_Burst])
        
        # Collapse Check
        Collapse_lambda = lambda depth: ((call(z, 1) * (min(Casing.Tension_Depth) - depth)) + sum(Weight) + sum(force_sum)) / Casing.Tension_Resist
        if Tension_length >= Set_Section_min:
            for depth_false in np.arange(min(Casing.Tension_Depth) - Tension_length, min(Casing.Tension_Depth) - Set_Section_min, 3):
                try: 
                    Collapse_check = pd.concat(
                        [
                            Casing.Collapse_design, 
                            pd.DataFrame({
                                "Depth" :[depth_false], 
                                "Design":[Between(Casing.Collapse_design, depth_false, "Depth", "Design")]})
                        ]
                        ).sort_values("Depth").drop_duplicates(subset='Depth').reset_index(drop="index")
                    Collapse_check["Check"] = (Biaxial_curve(Collapse_lambda(Collapse_check["Depth"])) * call(z, 4)) - Collapse_check["Design"]
                except: pass
                if len(Collapse_check[(Collapse_check["Depth"] >= depth_false) & (Collapse_check["Check"] < 0)]) == 0: break
            Tension_length = min(Casing.Tension_Depth) - depth_false
        else: break
        
        # Membatasi Nilai Minimum Section Tension_length
        if Tension_length < Set_Section_min: break
        elif Tension_length >= Set_Section_min:
            if Tension_length >= min(Casing.Tension_Depth): Tension_length = min(Casing.Tension_Depth)
            elif (Tension_length < min(Casing.Tension_Depth)) & (min(Casing.Tension_Depth) - Tension_length < Set_Section_min):
                if min(Casing.Tension_Depth) - Set_Section_min >= Set_Section_min: Tension_length = min(Casing.Tension_Depth) - Set_Section_min
                else: break
        
        # Input Variabel
        Tension_check = Collapse_lambda(min(Casing.Tension_Depth) - Tension_length) * Casing.Tension_Resist
        if Casing.Tension_Resist >= max([Tension_check*Casing.DF_Tension, Tension_check + Casing.Tension_Overpull]):
            Susunan_Casing.append(z)
            Susunan_Collapse.append([round(Biaxial_curve(Collapse_lambda(depth)) * call(z, 4), 2) for depth in [min(Casing.Tension_Depth), min(Casing.Tension_Depth) - Tension_length]])
            Susunan_Load.append([round(Collapse_lambda(depth) * Casing.Tension_Resist, 2) for depth in [min(Casing.Tension_Depth), min(Casing.Tension_Depth) - Tension_length]])
            Susunan_Depth.append([min(Casing.Tension_Depth), min(Casing.Tension_Depth) - Tension_length])
            Casing.Tension_Depth.append(min(Casing.Tension_Depth) - Tension_length)
        else: break
    
    if min(Casing.Tension_Depth) == 0: Casing.Tension_Table = pd.concat([Casing.Tension_Table, pd.DataFrame({"combination":[Susunan_Casing], "Collapse":[Susunan_Collapse], "Load":[Susunan_Load], "depth":[Susunan_Depth]})], ignore_index = True)
    else: Casing.fail.append(list(index))

@lru_cache(maxsize=None) 
def fail():
    mantap = []
    for fail in Casing.fail:
        for i in list(set(Para_index) - set(fail)): mantap.append(fail + [i])
    return mantap

with Tab_Tension_Biaxial:
    
    Para_index = [i for i in list(Casing.Parameter.index)]       
    Casing_fail = [[i] for i in Para_index]
    while len(Casing_fail) != 0:
        for combination in Casing_fail:
            if len(Casing.Tension_Table) > 50: break
            i = []
            for c in combination: 
                i.append(c)
                if (i not in list(Casing.Tension_Table.iloc[:,0])) and (i == list(combination)): Tension_Biaxial(tuple(combination))
                elif i in list(Casing.Tension_Table.iloc[:,0]): break
        Casing_fail = []
    else: st.dataframe(Casing.Tension_Table, use_container_width=True)

    mantap = fail()
    st.write(mantap)