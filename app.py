import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import plotly.io as pio

pio.templates.default = "plotly_white"


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
            "Company_Status",
            "Ultimate_Supplier_Name",
            "Revenue",
            "SGA",
            "EBIT",
            "SGA_Percent",
            "Profit_Percent",
            "SGA_and_P",
            "OEMs"
        ]

        if df.iloc[0, 0] == "Public" or df.iloc[0, 2] == "Revenue":
            df = df.iloc[2:].reset_index(drop=True)

        numeric_columns = ["Revenue", "SGA", "EBIT"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(",", "", regex=False)
                df[col] = pd.to_numeric(df[col], errors="coerce")

        percentage_columns = ["SGA_Percent", "Profit_Percent", "SGA_and_P"]
        for col in percentage_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.rstrip("%")
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "Company_Status" in df.columns:
            df["Company_Status"] = df["Company_Status"].astype(str).str.strip()

        if "Ultimate_Supplier_Name" in df.columns:
            df["Ultimate_Supplier_Name"] = (
                df["Ultimate_Supplier_Name"].astype(str).str.strip()
            )

        if "OEMs" in df.columns:
            df["OEMs"] = df["OEMs"].fillna("").astype(str).str.strip()

        df = df.dropna(subset=["Ultimate_Supplier_Name", "Revenue", "SGA"])

        return df

    except Exception as e:
        print(f"File loading failed: {str(e)}")
        raise


def clamp_percent(value):
    if pd.isna(value):
        return 0
    if value < 0:
        return 0
    if value > 100:
        return 100
    return float(value)


def format_money(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:,.0f}"


def make_percent_circle(label, value, color_class):
    display_value = 0 if pd.isna(value) else round(float(value), 1)
    fill_value = clamp_percent(display_value)

    return html.Div(
        [
            html.Div(
                [
                    html.Div(f"{display_value:.1f}%", className="percent-number"),
                    html.Div(label, className="percent-label-inside")
                ],
                className=f"percent-circle {color_class}",
                style={"--percent": f"{fill_value}%"}
            )
        ],
        className="percent-circle-wrap"
    )


def split_oems(oem_text):
    if not oem_text or pd.isna(oem_text):
        return []

    raw_parts = str(oem_text).replace(";", ",").replace("/", ",").split(",")
    cleaned = []

    for part in raw_parts:
        piece = part.strip()
        if piece and piece not in cleaned:
            cleaned.append(piece)

    return cleaned


def make_company_card(row):
    oem_list = split_oems(row.get("OEMs", ""))

    if oem_list:
        oem_chips = [
            html.Span(oem, className="oem-chip") for oem in oem_list
        ]
    else:
        oem_chips = [html.Span("No OEM listed", className="oem-chip muted-chip")]

    status = row.get("Company_Status", "")
    status_text = status if pd.notna(status) and str(status).strip() else "Unknown"

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(
                                row["Ultimate_Supplier_Name"],
                                className="company-card-title"
                            ),
                            html.Div(status_text, className="status-badge")
                        ],
                        className="company-card-top"
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div("Revenue", className="mini-stat-label"),
                                    html.Div(
                                        format_money(row.get("Revenue")),
                                        className="mini-stat-value"
                                    )
                                ],
                                className="mini-stat"
                            ),
                            html.Div(
                                [
                                    html.Div("SG&A", className="mini-stat-label"),
                                    html.Div(
                                        format_money(row.get("SGA")),
                                        className="mini-stat-value"
                                    )
                                ],
                                className="mini-stat"
                            ),
                            html.Div(
                                [
                                    html.Div("EBIT", className="mini-stat-label"),
                                    html.Div(
                                        format_money(row.get("EBIT")),
                                        className="mini-stat-value"
                                    )
                                ],
                                className="mini-stat"
                            )
                        ],
                        className="mini-stats-grid"
                    ),
                ],
                className="company-card-left"
            ),

            html.Div(
                [
                    make_percent_circle(
                        "SG&A %",
                        row.get("SGA_Percent"),
                        "circle-blue"
                    ),
                    make_percent_circle(
                        "EBIT %",
                        row.get("Profit_Percent"),
                        "circle-green"
                    )
                ],
                className="percent-circles-row"
            ),

            html.Div(
                [
                    html.Div("Automotive OEMs", className="section-label"),
                    html.Div(oem_chips, className="oem-chip-row")
                ],
                className="oem-section"
            )
        ],
        className="company-card"
    )


df = get_data()

revenue_df = df.sort_values("Revenue", ascending=False).copy()
sga_df = df.sort_values("SGA", ascending=False).copy()

fig_revenue = px.bar(
    revenue_df,
    x="Ultimate_Supplier_Name",
    y="Revenue",
    title="Revenue by Supplier",
    text="Revenue"
)

fig_revenue.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Revenue: %{y:,.0f}<extra></extra>"
)

fig_revenue.update_layout(
    xaxis_title="Supplier",
    yaxis_title="Revenue",
    title_x=0.5,
    height=560,
    margin=dict(l=40, r=20, t=70, b=140),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="white",
    font=dict(size=13),
    hovermode="x unified"
)

fig_revenue.update_xaxes(
    tickangle=45,
    showgrid=False
)

fig_revenue.update_yaxes(
    gridcolor="rgba(0,0,0,0.08)",
    zeroline=False
)

fig_sga = px.bar(
    sga_df,
    x="Ultimate_Supplier_Name",
    y="SGA",
    title="SG&A by Supplier",
    text="SGA"
)

fig_sga.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>SG&A: %{y:,.0f}<extra></extra>"
)

fig_sga.update_layout(
    xaxis_title="Supplier",
    yaxis_title="SG&A",
    title_x=0.5,
    height=560,
    margin=dict(l=40, r=20, t=70, b=140),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="white",
    font=dict(size=13),
    hovermode="x unified"
)

fig_sga.update_xaxes(
    tickangle=45,
    showgrid=False
)

fig_sga.update_yaxes(
    gridcolor="rgba(0,0,0,0.08)",
    zeroline=False
)

total_suppliers = df["Ultimate_Supplier_Name"].nunique()
total_revenue = df["Revenue"].sum()
total_sga = df["SGA"].sum()

app = Dash(__name__)
app.title = "Supplier Dashboard"

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div("GM Supplier Intelligence", className="hero-eyebrow"),
                        html.H1("Search a supplier and view its financial profile", className="hero-title"),
                        html.P(
                            "Look up companies from the uploaded dataset and quickly view SG&A %, EBIT %, and OEM relationships in a clean dashboard view.",
                            className="hero-subtitle"
                        ),

                        html.Div(
                            [
                                dcc.Input(
                                    id="company-search",
                                    type="text",
                                    placeholder="Search by supplier name...",
                                    className="search-input"
                                )
                            ],
                            className="search-bar-wrap"
                        )
                    ],
                    className="hero-panel"
                ),

                html.Div(id="search-results", className="search-results-section")
            ],
            className="dashboard-container"
        ),

        html.Div(
            [
                html.Details(
                    [
                        html.Summary("Extra", className="extra-summary"),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div("Total Suppliers", className="metric-label"),
                                        html.Div(f"{total_suppliers:,}", className="metric-value")
                                    ],
                                    className="metric-card"
                                ),

                                html.Div(
                                    [
                                        html.Div("Total Revenue", className="metric-label"),
                                        html.Div(f"{total_revenue:,.0f}", className="metric-value")
                                    ],
                                    className="metric-card"
                                ),

                                html.Div(
                                    [
                                        html.Div("Total SG&A", className="metric-label"),
                                        html.Div(f"{total_sga:,.0f}", className="metric-value")
                                    ],
                                    className="metric-card"
                                )
                            ],
                            className="metrics-row"
                        ),

                        html.Div(
                            [
                                dcc.Graph(
                                    figure=fig_revenue,
                                    config={"displaylogo": False}
                                )
                            ],
                            className="chart-card"
                        ),

                        html.Div(
                            [
                                dcc.Graph(
                                    figure=fig_sga,
                                    config={"displaylogo": False}
                                )
                            ],
                            className="chart-card"
                        )
                    ],
                    className="extra-section"
                )
            ],
            className="dashboard-container extra-container"
        )
    ]
)


@app.callback(
    Output("search-results", "children"),
    Input("company-search", "value")
)
def update_results(search_value):
    if not search_value or not search_value.strip():
        return html.Div(
            [
                html.Div("Start by searching for a company", className="empty-title"),
                html.P(
                    "Type a supplier name into the search bar above to load its financial and OEM information.",
                    className="empty-text"
                )
            ],
            className="empty-state"
        )

    search_value = search_value.strip().lower()

    filtered_df = df[
        df["Ultimate_Supplier_Name"].str.lower().str.contains(search_value, na=False)
    ].copy()

    filtered_df = filtered_df.sort_values("Ultimate_Supplier_Name")

    if filtered_df.empty:
        return html.Div(
            [
                html.Div("No company found", className="empty-title"),
                html.P(
                    "Try another spelling or a shorter company name.",
                    className="empty-text"
                )
            ],
            className="empty-state"
        )

    cards = [make_company_card(row) for _, row in filtered_df.iterrows()]

    return html.Div(
        [
            html.Div(
                f"{len(filtered_df)} result(s) found",
                className="results-count"
            ),
            html.Div(cards, className="company-card-list")
        ]
    )


if __name__ == "__main__":
    app.run(debug=True, port=8051)
