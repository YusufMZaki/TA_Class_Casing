import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from functools import lru_cache
class Variabel:
    def __init__(self) -> None:
        
        self.Subset_Drift = 0
        
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
        self.Tension_Overpull = 0
        self.Section_alt = 0
        
    def Subset_drift(self, df, OD): self.Subset_Drift = df[df.iloc[:,0]==OD].drop_duplicates(subset='6_Drift Diameter in.').reset_index(drop="index")
        
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

class Ten_Bix:
    def __init__(self) -> None:
        
        self.Para_df = 1
        self.Parameter = 1
        
        # Tension
        self.Tension_Table = []
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
        
        self.location = 0
        self.Altair = 0
    
    def Tension(self, MD): 
        self.Tension_weight = []
        self.Tension_Depth = [MD]
    
    def Parameter_df(self, df, Casing): self.Para_df = df[(df.iloc[:,0]==Casing.OD) & (df.iloc[:,5] <= Casing.Drift_value if Casing.Drift == "Maximum" else df.iloc[:,5] >= Casing.Drift_value)].replace("—", None)
    def Parameter_sort(self, Grade_drop): 
        
        Parameter = self.Para_df.iloc[:, [0, 1, 2, 5, 11, 12, 16, 23]]
        Para_Grade = pd.DataFrame(
            {
                "Weight":[int(Para) for Para in Parameter.iloc[:,1]], 
                "Grade-num":[("" if str(Para.split("-")[1]).count("") != 3 else "0") + str(Para.split("-")[1]) for Para in Parameter.iloc[:,2]], 
                "Grade-alp":[(str(Para.split("-")[0]) if str(Para.split("-")[0]).count("") == 2 else "A") for Para in Parameter.iloc[:,2]]
            },
            index=Parameter.index).sort_values("Weight")
        Para_Grade["Grade"] = Para_Grade["Grade-num"] + "-" + Para_Grade["Grade-alp"]
        
        Para_Grade_sort = pd.DataFrame({"Weight":[], "Grade-num":[], "Grade-alp":[], "Grade":[]})
        for wght in Para_Grade.drop_duplicates(subset='Weight')["Weight"]: Para_Grade_sort = pd.concat([Para_Grade_sort, Para_Grade[Para_Grade["Weight"] == wght].sort_values("Grade")])
        
        self.Parameter = Parameter.loc[Para_Grade_sort.index].reset_index(drop="index")
        self.Parameter.index = self.Parameter.index + 1
        self.Parameter = self.Parameter[self.Parameter.iloc[:,2].isin(Grade_drop) == True if len(Grade_drop) != 0 else self.Parameter.iloc[:,2].isin(Grade_drop) == False]
    
    
    def call(self, row, col): return self.Parameter.loc[row,self.Parameter.columns[col]]
    def Design_limit(self, Casing, df, value, known, find):
        if Casing.Burst_design.equals(df) == True: Nama = f"Burst_{value}_{known}_{find}"
        else: Nama = f"Collapse_{value}_{known}_{find}"
        if Nama in list(self.Between.iloc[:,0]): return self.Between.iloc[list(self.Between.iloc[:,0]).index(Nama),1]
        else: 
            Limit = pd.concat([df, pd.DataFrame({known:[value], find:[np.nan]})])
            Limit = Limit.sort_values(known, ascending=(True if known == "Depth" else False)).drop_duplicates(subset=known).set_index(known).interpolate(method='index')
            self.Between = pd.concat([self.Between, pd.DataFrame({"Nama":[Nama],"Pandas":[Limit]})], ignore_index = True)
            return Limit
    def Between_df(self, Casing, df, value, known, find): return self.Design_limit(Casing, df, value, known, find).loc[value,find]

    def Preparation(self):
        self.Between = pd.DataFrame({"Nama":[],"Pandas":[]})
        self.Tension_Table = pd.DataFrame({"combination":[], "Collapse":[], "Load":[], "depth":[]})
        self.fail_table = pd.DataFrame({"combination":[], "Collapse":[], "Load":[], "depth":[]})
    
    @lru_cache(maxsize=None)
    def Tension_Biaxial(self, index, Casing, Biaxial_curve, Biaxial_ratio, Force, Set_Section_min, Set_Section_max):
        Susunan_Casing = []
        Susunan_Depth = []
        Susunan_Load = []
        Susunan_Collapse = []
        self.Tension(Casing.MD)
        if (len(index) != 1) and (list(index)[:-1] in list(self.fail_table.iloc[:,0])):
            for key, val in enumerate(list(self.fail_table.iloc[:,0])): 
                if list(index)[:-1] == val: 
                    for ca in self.fail_table.iloc[key,0]: 
                        Susunan_Casing.append(ca)
                        self.Tension_weight.append(self.call(ca, 1))
                    for co in self.fail_table.iloc[key,1]: Susunan_Collapse.append(co)
                    for lo in self.fail_table.iloc[key,2]: Susunan_Load.append(lo)
                    for de in self.fail_table.iloc[key,3]: 
                        Susunan_Depth.append(de)
                        self.Tension_Depth.append(de[1])
                    index = [index[-1]]
                    break
        
        for z in index:
            if min(self.Tension_Depth) == 0: break
            if self.call(z, 4) < self.Between_df(Casing, Casing.Collapse_design, min(self.Tension_Depth), "Depth", "Design"): break
            elif  self.call(z, 6) < self.Between_df(Casing, Casing.Burst_design, min(self.Tension_Depth), "Depth", "Design"): break
            
            # Burst Check
            Burst_check_limit = self.Design_limit(Casing, Casing.Burst_design, min(self.Tension_Depth), "Depth", "Design")
            Burst_check_limit = Burst_check_limit[Burst_check_limit.index <= min(self.Tension_Depth)]
            if len(list(Burst_check_limit[Burst_check_limit["Design"] > self.call(z, 6)].index)) != 0:
                Burst_max = max(list(Burst_check_limit[Burst_check_limit["Design"] > self.call(z, 6)].index))
                Burst_check = pd.DataFrame(
                    {
                        "Depth":[dpth for dpth in Burst_check_limit.index if dpth >= Burst_max] + [None],
                        "Design":[dsgn for dsgn, dpth in zip(Burst_check_limit.iloc[:,0], Burst_check_limit.index) if dpth >= Burst_max] + [self.call(z, 6)]
                    }
                    ).sort_values("Design").set_index("Design").interpolate(method='index')
                Burst_depth = ((min(self.Tension_Depth) - Burst_check.loc[self.call(z, 6), "Depth"])//3)*3
            else: Burst_depth = min(self.Tension_Depth)
            
            self.Biaxial_X = Biaxial_curve(Biaxial_ratio(self.Between_df(Casing, Casing.Collapse_design, min(self.Tension_Depth), "Depth", "Design"), self.call(z, 4)))
            self.Tension_Resist = min([self.call(z, 5), self.call(z, 7)]) * 1000 # Yield or Joint
            
            # Weight (lb) = weight_unit (lb/ft) * Tension_Depth (ft) ==> used
            Weight = [0] if len(self.Tension_weight) == 0 else [weight * (depth[0] - depth[1]) for weight, depth in zip(self.Tension_weight, Susunan_Depth)]
            
            # weight_unit (lb/ft)
            self.Tension_weight.append(self.call(z, 1))
            
            # Force (lb) = pressure (psi = lb/sq in) * Cross Sectional Area (sq in)
            force_ = [0] + [Force(Casing.Drill, depth, weight)for depth, weight in zip(self.Tension_Depth, self.Tension_weight)]
            force_sum = [force_[i] - force_[i + 1] for i in range(len(self.Tension_weight))]
            
            # Menentukan Kemampuan Panjang Collapse Yang Mampu Ditahan Oleh Casing
            Collapse_length = ( (self.Biaxial_X * self.Tension_Resist) - sum(Weight) - sum(force_sum) ) / self.call(z, 1)

            # Set Section Casing Minimum Pada Kelipatan 3ft - [0] Length Casing Sisa - [1] Collapse Length - [2] Section Limit - [3] Burst Check ===> Kemampuan Length Casing Dari Body Yield
            Tension_length = min([min(self.Tension_Depth), (Collapse_length//3)*3, Set_Section_max, Burst_depth])
            
            # Collapse Check
            Collapse_lambda = lambda depth: ((self.call(z, 1) * (min(self.Tension_Depth) - depth)) + sum(Weight) + sum(force_sum)) / self.Tension_Resist
            Collapse_check_limit = self.Design_limit(Casing, Casing.Collapse_design, min(self.Tension_Depth), "Depth", "Design")
            Limit_depth_df = list(Collapse_check_limit.index)
            Limit_check_df = [(Biaxial_curve(Collapse_lambda(depth)) * self.call(z, 4)) - design for depth, design in zip(Limit_depth_df, list(Collapse_check_limit["Design"]))]
            for depth_false in np.arange(min(self.Tension_Depth) - Tension_length, min(self.Tension_Depth), 3):
                Limit_false = []
                Limit_depth = Limit_depth_df + ([] if depth_false in Limit_depth_df else [depth_false])
                Limit_check = Limit_check_df + ([] if depth_false in Limit_depth_df else [(Biaxial_curve(Collapse_lambda(depth_false)) * self.call(z, 4)) - self.Between_df(Casing, Casing.Collapse_design, depth_false, "Depth", "Design")]) 
                for y in sorted([x for x in Limit_depth if (x >= depth_false) and (x <= min(self.Tension_Depth))]): Limit_false.append(Limit_check[Limit_depth.index(y)])
                if min(Limit_false) >= 0: 
                    Tension_length = min(self.Tension_Depth) - depth_false
                    break
                if depth_false == max(list(np.arange(min(self.Tension_Depth) - Tension_length, min(self.Tension_Depth), 3))): Tension_length = min(self.Tension_Depth) - depth_false
            
            # Membatasi Nilai Minimum Section Tension_length
            if Tension_length < Set_Section_min: break
            elif Tension_length >= Set_Section_min:
                if Tension_length >= min(self.Tension_Depth): Tension_length = min(self.Tension_Depth)
                elif (Tension_length < min(self.Tension_Depth)) and (min(self.Tension_Depth) - Tension_length < Set_Section_min):
                    if min(self.Tension_Depth) - Set_Section_min >= Set_Section_min: Tension_length = ((min(self.Tension_Depth) - Set_Section_min)//3)*3
                    else: break
            
            # Input Variabel
            Tension_check = Collapse_lambda(min(self.Tension_Depth) - Tension_length) * self.Tension_Resist
            if self.Tension_Resist >= max([Tension_check*Casing.DF_Tension, Tension_check + Casing.Tension_Overpull]):
                Susunan_Casing.append(z)
                Susunan_Collapse.append([round(Biaxial_curve(Collapse_lambda(depth)) * self.call(z, 4), 2) for depth in [min(self.Tension_Depth), min(self.Tension_Depth) - Tension_length]])
                Susunan_Load.append([round(Collapse_lambda(depth) * self.Tension_Resist, 2) for depth in [min(self.Tension_Depth), min(self.Tension_Depth) - Tension_length]])
                Susunan_Depth.append([float(min(self.Tension_Depth)), float(min(self.Tension_Depth) - Tension_length)])
                self.Tension_Depth.append(min(self.Tension_Depth) - Tension_length)
            else: break
        
        if min(self.Tension_Depth) == 0: 
            self.Tension_Table = pd.concat([self.Tension_Table, pd.DataFrame({"combination":[Susunan_Casing], "Collapse":[Susunan_Collapse], "Load":[Susunan_Load], "depth":[Susunan_Depth]})], ignore_index = True)
            self.succ_current.append(Susunan_Casing)
        elif (len(Susunan_Casing) != 0) and (Susunan_Casing not in list(self.fail_table.iloc[:,0])): 
            self.fail_table = pd.concat([self.fail_table, pd.DataFrame({"combination":[Susunan_Casing], "Collapse":[Susunan_Collapse], "Load":[Susunan_Load], "depth":[Susunan_Depth]})], ignore_index = True)
            self.fail_current.append(Susunan_Casing)
            self.fail.append(Susunan_Casing)
    
    def Design(self, Name, Iterasi_max, Casing, Biaxial_curve, Biaxial_ratio, Force, Set_Section_min, Set_Section_max):
        st.write(Name)
        Para_index = [i for i in list(self.Parameter.index)]
        for casing in [[i] for i in Para_index]: self.Tension_Biaxial(tuple(casing), Casing, Biaxial_curve, Biaxial_ratio, Force, Set_Section_min, Set_Section_max)
        Casing_fail = self.fail
        iterasi = 1
        while (len(Casing_fail) != 0) and (iterasi != Iterasi_max):
            iterasi += 1
            self.fail = []
            for combination in Casing_fail:
                self.succ_current = []
                self.fail_current = []
                if (iterasi > 3) and (len(self.succ_current) + len(self.fail_current) == 10): break
                for i in list(set(Para_index) - set(combination)):
                    if len(self.succ_current) + len(self.fail_current) == len(Para_index): break
                    else: self.Tension_Biaxial(tuple(combination + [i]), Casing, Biaxial_curve, Biaxial_ratio, Force, Set_Section_min, Set_Section_max)
            Casing_fail = self.fail
            if (iterasi == Iterasi_max) or (len(self.fail) == 0): break
        
        # st.dataframe(self.Tension_Table, use_container_width=True)
        Check_combination = pd.DataFrame(
            {
                "combination":[[("" if self.call(row,1) >= 10 else "0") + ("" if self.call(row,1) >= 100 else "0") + str(round(float(self.call(row,1)),1)) + (" " if self.call(row,2).count("") == 6 else " 0") + str(self.call(row,2).split("-")[1]) + "-" + str(self.call(row,2).split("-")[0]) for row in locs] for locs in self.Tension_Table.iloc[:,0]],
                "weight":
                    [
                        round(sum([float(self.call(row,1) * (depth[0] - depth[1])) for row, depth in zip(locs, depths)]), 2) 
                        for locs, depths in zip(self.Tension_Table.iloc[:,0], self.Tension_Table.iloc[:,3])
                    ],
            }).sort_values("weight")
        Check_combination_sort = pd.DataFrame({"combination":[], "weight":[]})
        for wght in Check_combination.drop_duplicates(subset='weight')["weight"]: Check_combination_sort = pd.concat([Check_combination_sort, Check_combination[Check_combination["weight"] == wght].sort_values("combination")])
        self.Tension_Table = self.Tension_Table.loc[Check_combination_sort.index]
        self.Tension_Table["Burst"] = [[[float(self.call(row,6)), float(self.call(row,6))] for row in rows] for rows in self.Tension_Table["combination"]]
        self.Tension_Table["Tension"] = [[[float(min([self.call(row,5), self.call(row,7)]))*1000, float(min([self.call(row,5), self.call(row,7)]))*1000] for row in rows] for rows in self.Tension_Table["combination"]]
        self.Tension_Table["Name"] = [[f"{self.call(row,1)} {self.call(row,2)}" for row in rows] for rows in self.Tension_Table["combination"]]
        self.Tension_Table["Collapse_resist"] = [[[float(self.call(row,4)), float(self.call(row,4))] for row in rows] for rows in self.Tension_Table["combination"]]
        # st.dataframe(Check_combination_sort, use_container_width=True)
        # st.dataframe(self.Tension_Table, use_container_width=True)
        
    def Concat(self, Biaxial_curve, Casing):
        def Pd_Ser(val, idx, grd): return pd.Series(val, index=idx, name=grd)
        def Pd_Con(series): return pd.concat(series, axis=1).reset_index().rename(columns={"index": "Depth"})
        if len(self.Tension_Table) > 10: Tension_Table = self.Tension_Table.iloc[:10]
        else: Tension_Table = self.Tension_Table
        self.Altair = pd.DataFrame(
            {
                "PD_Burst":[Pd_Con([Pd_Ser(val, idx, grd) for val, idx, grd in zip(vals, idxs, grds)]) for vals, idxs, grds in zip(Tension_Table.iloc[:,4], Tension_Table.iloc[:,3], Tension_Table.iloc[:,6])],
                "PD_Collapse":[Pd_Con([Pd_Ser(val, idx, grd) for val, idx, grd in zip(vals, idxs, grds)]) for vals, idxs, grds in zip(Tension_Table.iloc[:,1], Tension_Table.iloc[:,3], Tension_Table.iloc[:,6])],
                "PD_Tension":[Pd_Con([Pd_Ser(val, idx, grd) for val, idx, grd in zip(vals, idxs, grds)]) for vals, idxs, grds in zip(Tension_Table.iloc[:,5], Tension_Table.iloc[:,3], Tension_Table.iloc[:,6])],
                "PD_Load":[Pd_Con([Pd_Ser(val, idx, grd) for val, idx, grd in zip(vals, idxs, grds)]) for vals, idxs, grds in zip(Tension_Table.iloc[:,2], Tension_Table.iloc[:,3], Tension_Table.iloc[:,6])],
                "PD_Load_Over":[Pd_Con([Pd_Ser([v + Casing.Tension_Overpull for v in val], idx, grd) for val, idx, grd in zip(vals, idxs, grds)]) for vals, idxs, grds in zip(Tension_Table.iloc[:,2], Tension_Table.iloc[:,3], Tension_Table.iloc[:,6])],
                "PD_Load_DF":[Pd_Con([Pd_Ser([v * Casing.DF_Tension for v in val], idx, grd) for val, idx, grd in zip(vals, idxs, grds)]) for vals, idxs, grds in zip(Tension_Table.iloc[:,2], Tension_Table.iloc[:,3], Tension_Table.iloc[:,6])],
                "PD_X":[Pd_Con([Pd_Ser([v_l / v_r for v_r, v_l in zip(val_r, val_l)], idx, grd) for val_r, val_l, idx, grd in zip(vals_r, vals_l, idxs, grds)]) for vals_r, vals_l, idxs, grds in zip(Tension_Table.iloc[:,5], Tension_Table.iloc[:,2], Tension_Table.iloc[:,3], Tension_Table.iloc[:,6])],
                "PD_Y":[Pd_Con([Pd_Ser([Biaxial_curve(v_l / v_r) for v_r, v_l in zip(val_r, val_l)], idx, grd) for val_r, val_l, idx, grd in zip(vals_r, vals_l, idxs, grds)]) for vals_r, vals_l, idxs, grds in zip(Tension_Table.iloc[:,5], Tension_Table.iloc[:,2], Tension_Table.iloc[:,3], Tension_Table.iloc[:,6])],
                "PD_Coll_resist":[Pd_Con([Pd_Ser(val, idx, grd) for val, idx, grd in zip(vals, idxs, grds)]) for vals, idxs, grds in zip(Tension_Table.iloc[:,7], Tension_Table.iloc[:,3], Tension_Table.iloc[:,6])],
            })
        
def OD_index(Casing_subset_OD, Parameter):
    OD_index = [index for index, value in enumerate(Casing_subset_OD.iloc[:, 0]) if value == Parameter[0]]
    return st.selectbox('Size Outside Diameter (inch)', Casing_subset_OD.iloc[:, 0], index=OD_index[0])

def Manual_data(Total, OD, manual, Grade_5C3):
    Cas_OD, Cas_We, Cas_Gr, Cas_Dr, Cas_Co, Cas_Yi, Cas_Bu, Cas_Jo = st.columns(8)
    for Tot in range(Total):
        if Tot == 0: Vision = "visible"
        else: Vision = "collapsed"
        with Cas_OD: st.number_input("Outside Diameter (Inch)", value=OD, key=f"Cas_OD_{Tot}", disabled=True, label_visibility=Vision),
        with Cas_We: st.number_input("Nominal Weight (lbs/ft)", min_value=1, value=int(manual.iloc[-1,1]) if Tot == 0 else None, key=f"Cas_We_{Tot}", label_visibility=Vision),
        with Cas_Gr: st.selectbox("Grade", Grade_5C3, index=Grade_5C3.index(manual.iloc[-1,2]), key=f"Cas_Gr_{Tot}", label_visibility=Vision)
        with Cas_Dr: st.number_input("Drift Diameter (Inch)", max_value=OD, value=manual.iloc[-1,5] if Tot == 0 else None, key=f"Cas_Dr_{Tot}", label_visibility=Vision)
        with Cas_Co: st.number_input("Collapse Resist (psi)", min_value=1, value=int(manual.iloc[-1,11]) if Tot == 0 else None, key=f"Cas_Co_{Tot}", label_visibility=Vision)
        with Cas_Yi: st.number_input("Body Yield 1000 lb", min_value=1, value=int(manual.iloc[-1,12]) if Tot == 0 else None, key=f"Cas_Yi_{Tot}", label_visibility=Vision)
        with Cas_Bu: st.number_input("Burst (psi)", min_value=1, value=int(manual.iloc[-1,16]) if Tot == 0 else None, key=f"Cas_Bu_{Tot}", label_visibility=Vision)
        with Cas_Jo: st.number_input("Joint Strength 1000 lb", min_value=1, value=int(manual.iloc[-1,23]) if Tot == 0 else None, key=f"Cas_Jo_{Tot}", label_visibility=Vision)

def Manual_data_pandas(Session):
    Total = Session["Cas_Total"]
    def ses_list(Name): return [Session[f"{Name}{Tot}"] for Tot in range(Total)]
    return pd.DataFrame(
        {
            "1_Size Outside Diameter in. D":ses_list("Cas_OD_"), "2_Nominal Weight, Threadsand Coupling lb/ft":ses_list("Cas_We_"), 
            "3_Grade":ses_list("Cas_Gr_"), "6_Drift Diameter in.":ses_list("Cas_Dr_"), "12_Collapse Resistance psi":ses_list("Cas_Co_"), 
            "13_Pipe Body Yield 1000 lb":ses_list("Cas_Yi_"), "17_Same Grade":ses_list("Cas_Bu_"), "24_Same Grade":ses_list("Cas_Jo_")
        })
    
def MD_ft(Parameter):
    return st.data_editor(
        pd.DataFrame({"Casing length (MD)":[Parameter[1]]}), column_config=
        {
            "Casing length (MD)":st.column_config.NumberColumn(help="Casing is assumed to be vertical - 3ft minimum", required=True, min_value=3, format="%d ft")
        }, 
        use_container_width=True, hide_index=True)

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

def altair_chart(df, title_x, MD):
    return alt.Chart(df).mark_line().encode(
        x = alt.X("value", title=title_x), 
        y = alt.Y("Depth", title="Depth (ft)", scale=alt.Scale(domain=[0, MD], reverse=True)), 
        order="Depth", 
        color=alt.Color('variable', sort=['GOOG']))