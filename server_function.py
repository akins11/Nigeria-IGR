from pandas import DataFrame, concat
from numpy import where
from plotly.express import bar, pie


pal = {
    "blue-sapphire": "#22577A",
    "cadet blue": "#38A3A5",
    "ocean green": "#57CC99",
    "light Green": "#80ED99",
    "tea-green": "#C7F9CC"
}


def concat_periods(df1, df2, df3):
    df1["period"] = "1st Quarter"
    df2["period"] = "2nd Quarter"
    df3["period"] = "Half Year"

    f_df = concat([df1, df2, df3]).reset_index(drop = True)

    return f_df


# [1] Cleaning the data frame ======================================================================================|
def clean_data(df):
    """
    df : [Data Frame] a data frame to clean
    """
    # Renaming columns -----------------------------------------------------------------------------------------|
    #     df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Creating Geo-political zones -----------------------------------------------------------------|
    north_central = ["Benue", "Kogi", "Kwara", "Nasarawa", "Niger", "Plateau", "FCT"]
    north_east = ["Adamawa", "Bauchi", "Borno", "Gombe", "Taraba", "Yobe"]
    north_west = ["Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Sokoto", "Zamfara"]
    south_east = ["Abia", "Anambra", "Ebonyi", "Enugu", "Imo"]
    south_south = ["Akwa Ibom", "Bayelsa", "Cross River", "Edo", "Rivers", "Delta"]
    south_west = ["Ekiti", "Lagos", "Ogun", "Ondo", "Osun", "Oyo"]

    df.loc[df["State"].isin(north_central), "Zone"] = "North Central"
    df.loc[df["State"].isin(north_east), "Zone"] = "North East"
    df.loc[df["State"].isin(north_west), "Zone"] = "North West"
    df.loc[df["State"].isin(south_east), "Zone"] = "South East"
    df.loc[df["State"].isin(south_south), "Zone"] = "South South"
    df.loc[df["State"].isin(south_west), "Zone"] = "South West"

    # Relocate the zone column
    # col = df.pop("Zone")
    # col = df.insert(1, col.name, col)

    return df


# [1] =================================================================================================================|
def state_level_df(df, revenue_type):
    ff_tbl = df[["State", revenue_type]].sort_values(revenue_type, ascending=False)
    ff_tbl["Proportion"] = round(ff_tbl[revenue_type] / ff_tbl[revenue_type].sum() * 100, 2)
    ff_tbl["Proportion"] = ff_tbl["Proportion"].astype("str") + "%"
    ff_tbl.reset_index(drop=True, inplace=True)
    ff_tbl = ff_tbl.sort_values(revenue_type)
    return ff_tbl


def zone_level_df(df, revenue_type):
    ff_tbl = DataFrame(df[["Zone", revenue_type]].groupby("Zone")[revenue_type].sum().reset_index())
    ff_tbl["Proportion"] = round(ff_tbl[revenue_type] / ff_tbl[revenue_type].sum() * 100, 2)
    ff_tbl["Proportion"] = ff_tbl["Proportion"].astype("str") + "%"
    ff_tbl = ff_tbl.sort_values(revenue_type)
    return ff_tbl


def revenue_plot(df, period, revenue_type, level):
    f_tbl = df.copy()

    period_dict = {"q1": "1st Quarter", "q2": "2nd Quarter", "half_year": "Half Year"}
    period_value = period_dict[period]

    f_tbl = f_tbl[f_tbl["period"] == period_value]

    if level == "State":
        f_tbl = state_level_df(f_tbl, revenue_type)

    elif level == "Zone":
        f_tbl = zone_level_df(f_tbl, revenue_type)

    if period == "half_year":
        plt_title = f"2021 {period_value} Total Revenue From {revenue_type} For Each {level}"
    else:
        plt_title = f"Total Revenue Of {period_value} 2021 From {revenue_type} For Each {level}"

    plt_height = 700 if level == "State" else 500
    f_plt = bar(data_frame = f_tbl,
                x = revenue_type,
                y = level,
                height= plt_height,
                hover_name = level,
                hover_data = {level: False, "Proportion": True},
                title = plt_title,
                template="plotly_white")
    f_plt.update_traces(marker_color = "#57CC99")
    f_plt.update_yaxes(title = "")
    f_plt.update_xaxes(title = "")

    return f_plt



def reshape_df(df, level, location_var):
    f_tbl = (
        df[df[level] == location_var]
        .drop(["Grand Total", "Total Tax", "period"], axis=1)
        .melt(id_vars=[level], value_vars=["PAYE", "Direct Assessment", "Road Tax", "Other Taxes", "MDAs"], var_name="Revenue")
    )
    f_tbl["Proportion"] = round(f_tbl["value"] / f_tbl["value"].sum() * 100, 2)
    f_tbl["Proportion"] = f_tbl["Proportion"].astype("str") + "%"
    f_tbl = f_tbl.sort_values("value")

    return f_tbl


def prep_total_igr_df(df, s_period, level, location_var):
    f_tbl = df[df["period"] == s_period]
    f_tbl = f_tbl.groupby("Zone").sum().reset_index()
    f_tbl["period"] = "period"
    f_tbl = reshape_df(f_tbl, level, location_var)

    return f_tbl


def total_igr_output(df, period, level, location_var):
    f_tbl = df.copy()

    period_dict = {"q1": "1st Quarter", "q2": "2nd Quarter", "half_year": "Half Year"}
    period_value = period_dict[period]

    if level == "State":
        f_tbl = f_tbl[f_tbl["period"] == period_value]
        f_tbl = reshape_df(f_tbl, level, location_var)

    elif level == "Zone":
        f_tbl = prep_total_igr_df(f_tbl, period_value, level, location_var)

    else:
        print("level can only be either State & Zone")

    if level == "State":
        if period == "half_year":
            if_tlt = f"{period_value} Source Of {location_var} State Internally Generated Revenue"
            el_tlt = f"{period_value} Source Of {location_var} Internally Generated Revenue"

            plt_title = if_tlt if location_var != "FCT" else el_tlt

        else:
            if_tlt = f"Source Of {location_var} State Internally Generated Revenue For The {period_value} Of 2021"
            el_tlt = f"Source Of {location_var} Internally Generated Revenue For The {period_value} Of 2021"

            plt_title = if_tlt if location_var != "FCT" else el_tlt

    elif level == "Zone":
        if period == "half_year":
            plt_title = f"{period_value} Source Of {location_var} Region Total IGR"
        else:
            plt_title = f"Source Of {location_var} State Total IGR For The {period_value} Of 2021"

    f_tbl = f_tbl.sort_values(by="value", ascending=False)

    f_plt = bar(data_frame = f_tbl,
                x = "Revenue",
                y = "value",
                hover_name= "Revenue",
                hover_data={"Revenue": False, "Proportion": True},
                title = plt_title,
                template = "plotly_white")
    f_plt.update_traces(marker_color = "#80ED99")
    f_plt.update_xaxes(title = "")
    f_plt.update_yaxes(title = "")

    return f_plt



def prep_zonal_revenue_df(df, s_period, zone, revenue_type):
    f_tbl = df[(df["period"] == s_period) & (df["Zone"] == zone)]
    f_tbl = f_tbl[["State", revenue_type]]

    return f_tbl

def zonal_revenue_output(df, period, zone, revenue_type):
    f_tbl = df.copy()

    period_dict = {"q1": "1st Quarter", "q2": "2nd Quarter", "half_year": "Half Year"}
    period_value = period_dict[period]

    f_tbl = prep_zonal_revenue_df(f_tbl, period_value, zone, revenue_type)

    if period == "half_year":
        plt_title = f"Size Of {revenue_type} Revenue Generated From States In {zone} Region For The {period_value} Of 2021"
    else:
        plt_title = f"Size Of {revenue_type} Revenue Generated From States In The {zone} Region During The {period_value} Of 2021"

    f_tbl = f_tbl.sort_values(by = revenue_type, ascending= False)
    f_plt = bar(data_frame= f_tbl,
                x = "State",
                y = revenue_type,
                hover_name = "State",
                hover_data = {"State": False},
                title = plt_title,
                template = "plotly_white")
    f_plt.update_traces(marker_color = "#57CC99")
    f_plt.update_xaxes(title = "")
    f_plt.update_yaxes(title = "")

    return f_plt


def revenue_change_output(df1, df2, revenue_type):
    f_tbl = df1[["State", revenue_type]].copy()

    f_tbl[revenue_type + "_n"] = df2[revenue_type]
    f_tbl = percent_change(f_tbl, old_value = revenue_type, new_value = f"{revenue_type}_n")
    f_tbl["change_color"] = where(f_tbl["percent_change"] >= 0, "Increase", "Decrease").tolist()
    f_tbl["Change"] = abs(round(f_tbl["percent_change"], 1))
    f_tbl["Change"] = f_tbl["Change"].astype("str") + "%"
    f_tbl = f_tbl.sort_values("percent_change")

    plt_title = f"Percentage Increase Or Decrease In {revenue_type} Revenue Generated By States In 1st-2nd Quarter Of 2021"

    f_plt = bar(data_frame= f_tbl,
                x="percent_change",
                y="State",
                color="change_color",
                text="Change",
                height=700,
                hover_name="State",
                hover_data={"State": False, "change_color": False, "percent_change": False},
                template="plotly_white",
                title= plt_title,
                color_discrete_map = {"Increase": "#80ED99", "Decrease": "#EE2C2C"})
    f_plt.update_layout(showlegend = False)
    f_plt.update_traces(textfont_size = 15, textfont_color = "#FFFFFF", textposition = "outside") #
    f_plt.update_yaxes(title="")
    f_plt.update_xaxes(title="Percentage Change")

    return f_plt


def revenue_summary_output(df, period, summary):
    f_tbl = df.copy()

    drop_cols = ["State", "Zone", "Grand Total", "Total Tax"]
    f_tbl = f_tbl.drop(drop_cols, axis = 1)

    period_dict = {"q1": "1st Quarter", "q2": "2nd Quarter", "half_year": "Half Year"}
    period_value = period_dict[period]

    f_tbl = f_tbl[f_tbl["period"] == period_value]
    f_tbl = f_tbl.drop("period", axis=1)

    if summary == "sum":
        f_tbl = f_tbl.sum()
    elif summary == "mean":
        f_tbl = f_tbl.mean()
    elif summary == "median":
        f_tbl = f_tbl.median()
    else:
        raise ValueError("`summary` must be any of 'sum', 'mean' or 'median'")

    f_tbl = f_tbl.reset_index().rename(columns = {"index": "variable", 0: "value"})
    f_tbl["Proportion"] = round(f_tbl["value"] / f_tbl["value"].sum() * 100, 1)
    f_tbl["Proportion"] = f_tbl["Proportion"].astype("str") + "%"
    f_tbl = f_tbl.sort_values("value")

    if period == "half_year":
        if summary == "sum":
            plt_title = f"{period_value} Of 2021 Total Revenue Generated By Each Source Of IGR"
        else:
            plt_title = f"{period_value} Of 2021 Average Revenue Generated By Each Source Of IGR"
    else:
        if summary == "sum":
            plt_title = f"Total Revenue Generated By Each Source Of IGR In The {period_value} Of 2021"
        else:
            plt_title = f"Average Revenue Generated By Each Source Of IGR In The {period_value} Of 2021"

    f_tbl = f_tbl.sort_values(by = "value", ascending= False)

    f_plt = bar(data_frame= f_tbl,
                x="variable",
                y="value",
                # text="proportion",
                hover_name="variable",
                hover_data={"variable": False, "Proportion": True},
                title=plt_title,
                template="plotly_white")
    f_plt.update_traces(marker_color = "#C7F9CC")
    f_plt.update_yaxes(title = "")
    f_plt.update_xaxes(title = "")

    return f_plt

def prop_table(df, var, deci=None):
    """
    df : [dataframe]
    var: [float, int] variable from the `df`.

    return
    ------
    the proportion of each value from the variable.
    """
    if deci is None:
        result = round(df[var] / df[var].sum() * 100)
    else:
        result = round(df[var] / df[var].sum() * 100, deci)

    return result


# [10] percentage change in revenue ===============================================| ************
def percent_change(df, old_value, new_value, deci=2, chg_names=None, with_neg=True):
    """
    df: [DataFrame]
    old_value: [float64, int64] a variable from the `df` to use as the previous value.
    new_value: [float64, int64] a variable from the `df` to use as the new value.
    deci:      [int] the number of decimal point to keep when rounding.
    chg_names: [list(str)] Alternate names to give the two new columns.
    with_neg:  [bool] True to calculate with negative values, False to not.

    return
    ------
    two additional columns  if chg_names is none:
    difference: the difference between the new_value and the old_value
    percent_change: the increase or decrease change in percentage.
    """
    # Conditions -------------------------------------------------------------------------------------------|
    if chg_names is None:
        if with_neg:
            df["difference"] = df[new_value] - df[old_value]
            df["percent_change"] = round(df["difference"] / df[old_value] * 100, deci)
        else:
            df["difference"] = abs(df[new_value] - df[old_value])
            df["percent_change"] = round(df["difference"] / df[old_value] * 100, deci)
    else:
        if len(chg_names) != 2:
            raise Exception(f"`chg_names` must be a list of length 2, but {len(chg_names)} was given.")

        if with_neg:
            df[chg_names[0]] = df[new_value] - df[old_value]
            df[chg_names[1]] = round(df["difference"] / df[old_value] * 100, deci)
        else:
            df[chg_names[0]] = abs(df[new_value] - df[old_value])
            df[chg_names[1]] = round(df["difference"] / df[old_value] * 100, deci)

    return df
