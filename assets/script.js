import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime

# Load data
patients = pd.read_csv("state_wise_daily.csv")

# Convert date to datetime
patients['Date'] = pd.to_datetime(patients['Date'], format='%d-%b-%y')

# Get unique states (excluding 'UN' which might be unknown)
all_states = [state for state in patients['State'].unique() if state != 'UN']
all_states.sort()

# Create summary data by Status
status_summary = patients.groupby('Status')[['Total', 'Hospitalized', 'Recovered', 'Deceased']].sum()

# Calculate totals
total_cases = patients['Total'].sum()
active_cases = patients[patients['Status'] == 'Confirmed']['Hospitalized'].sum() if 'Confirmed' in patients['Status'].values else 0
recovered_cases = patients[patients['Status'] == 'Recovered']['Recovered'].sum()
deaths_cases = patients[patients['Status'] == 'Deceased']['Deceased'].sum()

# Get top states by total cases
state_totals = patients.groupby('State')['Total'].sum().sort_values(ascending=False).head(10)

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div([
    # Main Container
    html.Div([
        # Hero Section
        html.Div([
            html.H1([
                html.I(className="fas fa-virus", style={"marginRight": "15px"}),
                "COVID-19 Dashboard"
            ], className="hero-title"),
            html.P("Real-time Pandemic Analytics & Monitoring", className="hero-subtitle"),
        ], className="hero-section"),

        # Controls Bar
        html.Div([
            html.Div([
                html.Label("Select State", className="control-label"),
                dcc.Dropdown(
                    id='state-dropdown',
                    options=[{'label': 'All States', 'value': 'All'}] +
                            [{'label': state, 'value': state} for state in all_states],
                    value='All',
                    className="control-dropdown",
                    clearable=False
                )
            ], className="control-item"),

            html.Div([
                html.Label("Select Status", className="control-label"),
                dcc.Dropdown(
                    id='status-dropdown',
                    options=[
                        {'label': 'All', 'value': 'All'},
                        {'label': 'Confirmed', 'value': 'Confirmed'},
                        {'label': 'Recovered', 'value': 'Recovered'},
                        {'label': 'Deceased', 'value': 'Deceased'}
                    ],
                    value='All',
                    className="control-dropdown",
                    clearable=False
                )
            ], className="control-item"),
        ], className="controls-bar"),
    ], className="hero-container"),

    # KPI Cards Row
    html.Div([
        html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line kpi-icon", style={"color": "#3b82f6"}),
                        html.H4("Total Cases", className="kpi-title"),
                    ], className="kpi-header"),
                    html.H2(f"{total_cases:,}", className="kpi-value"),
                    html.P("Cumulative Cases", className="kpi-subtitle")
                ])
            ], className="kpi-card", style={"borderTop": "3px solid #3b82f6"})
        ], className="col-md-3 col-sm-6"),

        html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-procedures kpi-icon", style={"color": "#10b981"}),
                        html.H4("Active Cases", className="kpi-title"),
                    ], className="kpi-header"),
                    html.H2(f"{active_cases:,}", className="kpi-value"),
                    html.P("Currently Hospitalized", className="kpi-subtitle")
                ])
            ], className="kpi-card", style={"borderTop": "3px solid #10b981"})
        ], className="col-md-3 col-sm-6"),

        html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-heartbeat kpi-icon", style={"color": "#f59e0b"}),
                        html.H4("Recovered", className="kpi-title"),
                    ], className="kpi-header"),
                    html.H2(f"{recovered_cases:,}", className="kpi-value"),
                    html.P("Recovered Patients", className="kpi-subtitle")
                ])
            ], className="kpi-card", style={"borderTop": "3px solid #f59e0b"})
        ], className="col-md-3 col-sm-6"),

        html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-skull-crossbones kpi-icon", style={"color": "#ef4444"}),
                        html.H4("Deaths", className="kpi-title"),
                    ], className="kpi-header"),
                    html.H2(f"{deaths_cases:,}", className="kpi-value"),
                    html.P("Fatalities", className="kpi-subtitle")
                ])
            ], className="kpi-card", style={"borderTop": "3px solid #ef4444"})
        ], className="col-md-3 col-sm-6"),
    ], className="row kpi-row"),

    # Row 1: State-wise Bar Chart
    html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.I(className="fas fa-chart-bar", style={"marginRight": "10px"}),
                "Top 10 States by Total Cases"
            ], className="card-header-custom"),
            dbc.CardBody([
                dcc.Graph(id="state-bar-chart")
            ])
        ], className="dashboard-card")
    ], className="row"),

    # Row 2: Two Columns
    html.Div([
        html.Div([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-chart-line", style={"marginRight": "10px"}),
                    "Daily Trend Analysis"
                ], className="card-header-custom"),
                dbc.CardBody([
                    dcc.Graph(id="line-chart")
                ])
            ], className="dashboard-card")
        ], className="col-md-6"),

        html.Div([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-chart-pie", style={"marginRight": "10px"}),
                    "Status Distribution"
                ], className="card-header-custom"),
                dbc.CardBody([
                    dcc.Graph(id="pie-chart")
                ])
            ], className="dashboard-card")
        ], className="col-md-6")
    ], className="row"),

    # Row 3: Commodity Trends
    html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.I(className="fas fa-chart-simple", style={"marginRight": "10px"}),
                "Commodity Demand Trends"
            ], className="card-header-custom"),
            dbc.CardBody([
                dcc.Dropdown(
                    id='commodity-dropdown',
                    options=[
                        {'label': 'Mask', 'value': 'Mask'},
                        {'label': 'Sanitizer', 'value': 'Sanitizer'},
                        {'label': 'Oxygen', 'value': 'Oxygen'}
                    ],
                    value='Mask',
                    className="commodity-dropdown",
                    clearable=False
                ),
                dcc.Graph(id="commodity-chart")
            ])
        ], className="dashboard-card")
    ], className="row"),

    # Footer
    html.Div([
        html.Hr(),
        html.Div([
            html.Div([
                html.I(className="fas fa-database", style={"marginRight": "8px"}),
                "Data Source: State-wise Daily Reports",
            ], className="footer-text"),
            html.Div([
                html.I(className="fas fa-chart-line", style={"marginRight": "8px"}),
                f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ], className="footer-text"),
        ], className="footer-content")
    ], className="footer")
], className="main-container")
], className="app-container")

# Callbacks
@app.callback(
    Output("state-bar-chart", "figure"),
    [Input("state-dropdown", "value"),
     Input("status-dropdown", "value")]
)
def update_bar_chart(selected_state, selected_status):
    filtered_df = patients.copy()

    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['State'] == selected_state]

    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]

    # Aggregate by state
    state_data = filtered_df.groupby('State')['Total'].sum().sort_values(ascending=True).tail(10)

    fig = go.Figure(data=[
        go.Bar(
            x=state_data.values,
            y=state_data.index,
            orientation='h',
            marker=dict(
                color=state_data.values,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Cases")
            ),
            text=state_data.values,
            textposition='outside',
            texttemplate='%{text:,}',
            hovertemplate='<b>%{y}</b><br>Cases: %{x:,}<extra></extra>'
        )
    ])

    fig.update_layout(
        title=f"Top 10 States - {selected_status if selected_status != 'All' else 'All Cases'}",
        xaxis_title="Number of Cases",
        yaxis_title="State",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e5e7eb', family='Inter'),
        height=500,
        margin=dict(l=120, r=30, t=50, b=30)
    )

    return fig

@app.callback(
    Output("line-chart", "figure"),
    [Input("state-dropdown", "value"),
     Input("status-dropdown", "value")]
)
def update_line_chart(selected_state, selected_status):
    filtered_df = patients.copy()

    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['State'] == selected_state]

    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
        y_column = 'Total'
    else:
        # For 'All', sum all statuses by date
        filtered_df = filtered_df.groupby('Date')['Total'].sum().reset_index()
        y_column = 'Total'

    if selected_status != 'All':
        # Group by date for specific status
        daily_data = filtered_df.groupby('Date')['Total'].sum().reset_index()
        fig = go.Figure(data=[
            go.Scatter(
                x=daily_data['Date'],
                y=daily_data['Total'],
                mode='lines+markers',
                name=selected_status,
                line=dict(width=3, color='#3b82f6', shape='spline'),
                marker=dict(size=4, color='#60a5fa'),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.2)',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Cases: %{y:,}<extra></extra>'
            )
        ])
    else:
        fig = go.Figure(data=[
            go.Scatter(
                x=filtered_df['Date'],
                y=filtered_df['Total'],
                mode='lines+markers',
                name='Total Cases',
                line=dict(width=3, color='#3b82f6', shape='spline'),
                marker=dict(size=4, color='#60a5fa'),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.2)'
            )
        ])

    fig.update_layout(
        title=f"Daily Cases - {selected_state if selected_state != 'All' else 'India'}",
        xaxis_title="Date",
        yaxis_title="Number of Cases",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e5e7eb', family='Inter'),
        height=400,
        hovermode='x unified'
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')

    return fig

@app.callback(
    Output("pie-chart", "figure"),
    [Input("state-dropdown", "value")]
)
def update_pie_chart(selected_state):
    filtered_df = patients.copy()

    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['State'] == selected_state]

    # Get latest data for each status
    status_data = filtered_df.groupby('Status')[['Hospitalized', 'Recovered', 'Deceased']].sum()

    values = []
    labels = []
    colors = []

    if 'Confirmed' in status_data.index:
        values.append(status_data.loc['Confirmed', 'Hospitalized'])
        labels.append('Active')
        colors.append('#ef4444')

    if 'Recovered' in status_data.index:
        values.append(status_data.loc['Recovered', 'Recovered'])
        labels.append('Recovered')
        colors.append('#10b981')

    if 'Deceased' in status_data.index:
        values.append(status_data.loc['Deceased', 'Deceased'])
        labels.append('Deceased')
        colors.append('#f59e0b')

    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>'
        )
    ])

    fig.update_layout(
        title=f"Case Distribution - {selected_state if selected_state != 'All' else 'India'}",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e5e7eb', family='Inter'),
        height=400,
        showlegend=True
    )

    return fig

@app.callback(
    Output("commodity-chart", "figure"),
    [Input("state-dropdown", "value"),
     Input("commodity-dropdown", "value")]
)
def update_commodity_chart(selected_state, commodity):
    filtered_df = patients.copy()

    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['State'] == selected_state]

    # Aggregate commodity by date
    commodity_data = filtered_df.groupby('Date')[commodity].sum().reset_index()

    fig = go.Figure(data=[
        go.Scatter(
            x=commodity_data['Date'],
            y=commodity_data[commodity],
            mode='lines+markers',
            name=commodity,
            line=dict(width=3, color='#8b5cf6', shape='spline'),
            marker=dict(size=6, color='#a78bfa'),
            fill='tozeroy',
            fillcolor='rgba(139, 92, 246, 0.2)',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>' + commodity + ': %{y:,}<extra></extra>'
        )
    ])

    fig.update_layout(
        title=f"{commodity} Demand Trend - {selected_state if selected_state != 'All' else 'India'}",
        xaxis_title="Date",
        yaxis_title=f"Number of {commodity}s",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e5e7eb', family='Inter'),
        height=400,
        hovermode='x unified'
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)