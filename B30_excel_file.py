import pandas as pd
import io
import streamlit as st

def export_dict_of_dfs_to_excel(df_dict, extra_df=None):
    """
    Exports a dictionary of DataFrames to an Excel file in memory.

    Args:
        df_dict (dict): Dictionary of DataFrames to export.
        extra_df (pd.DataFrame, optional): An additional DataFrame to include.

    Returns:
        bytes: The content of the Excel file.
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            sheet = sheet_name[:31]  # Sheet name max length = 31
            df.to_excel(writer, sheet_name=sheet, index=False)

        if extra_df is not None and not extra_df.empty:
            extra_sheet = "all_assets"[:31]
            extra_df.to_excel(writer, sheet_name=extra_sheet, index=False)

    output.seek(0)
    return output.read()
