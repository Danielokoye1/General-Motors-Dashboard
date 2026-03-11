import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc


def get_data():
    try:
        print("Loading Grunt Work CSV file...")

        df = pd.read_csv(
            "data/Grunt Work - Sheet1.csv",
            sep=",",
            engine="c",
            encoding="utf-8-sig",
            dtype=str,
            na_values=["", "NA", "N/A", "null", "NULL", "None", "#N/A"],
            keep_default_na=True
        )

        df.columns = [
            'Company_Status',
            'Ultimate_Supplier_Name',
            'Revenue',
            'SGA',
            'EBIT',
            'SGA_Percent',
            'Profit_Percent',
            'SGA_and_P',
            'OEMs'
        ]

        if df.iloc[0, 0] == 'Public' or df.iloc[0, 2] == 'Revenue':
            df = df.iloc[2:].reset_index(drop=True)

        numeric_columns = ['Revenue', 'SGA', 'EBIT']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')

        percentage_columns = ['SGA_Percent', 'Profit_Percent', 'SGA_and_P']
        for col in percentage_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.rstrip('%')
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'Company_Status' in df.columns:
            df['Company_Status'] = df['Company_Status'].astype(str).str.strip()

        return df

    except Exception as e:
        print(f"File loading failed: {str(e)}")
        raise


df = get_data()

fig_revenue = px.bar(
    df,
    x="Ultimate_Supplier_Name",
    y="Revenue",
    title="Revenue by Supplier"
)
fig_revenue.update_layout(
    xaxis_title="Supplier",
    yaxis_title="Revenue",
    title_x=0.5,
    template="plotly_white",
    height=600
)
fig_revenue.update_xaxes(tickangle=45)

fig_sga = px.bar(
    df,
    x="Ultimate_Supplier_Name",
    y="SGA",
    title="SGA by Supplier"
)
fig_sga.update_layout(
    xaxis_title="Supplier",
    yaxis_title="SGA",
    title_x=0.5,
    template="plotly_white",
    height=600
)
fig_sga.update_xaxes(tickangle=45)

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Supplier Dashboard", style={"textAlign": "center", "marginBottom": "30px"}),
    dcc.Graph(figure=fig_revenue),
    dcc.Graph(figure=fig_sga)
], style={
    "padding": "20px",
    "fontFamily": "Arial",
    "backgroundColor": "#f8f9fa"
})

if __name__ == "__main__":
    app.run(debug=True)
