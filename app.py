import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from datetime import datetime

# ==================== DATA LOADING ====================
df = pd.read_csv("state_wise_daily.csv")
df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y')
df['Active'] = df['Total'] - df['Recovered'] - df['Deceased']

# Clean state names
df['State'] = df['State'].str.strip()

# Get date range from dataset
MIN_DATE = df['Date'].min()
MAX_DATE = df['Date'].max()

# Get states (cleaned)
STATES = ['All'] + sorted(df['State'].unique())

# Color scheme
COLORS = {
    'primary': '#3182ce',
    'active': '#ed8936',
    'recovered': '#38a169',
    'deaths': '#e53e3e',
    'text': '#2d3748',
    'border': '#e2e8f0'
}

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("COVID-19 India Dashboard"),
            html.P("Real-time pandemic analysis with interactive visualizations")
        ], className="header-content")
    ], className="app-header"),

    # Main Content
    html.Div([
        # Filter Card
        html.Div([
            html.Div([
                html.Div([
                    html.Label("Select State", className="filter-label"),
                    dcc.Dropdown(
                        id='state-selector',
                        options=[{'label': s, 'value': s} for s in STATES],
                        value='All',
                        clearable=False
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),

                html.Div([
                    html.Label("Select Date Range", className="filter-label"),
                    dcc.DatePickerRange(
                        id='date-range',
                        min_date_allowed=MIN_DATE,
                        max_date_allowed=MAX_DATE,
                        start_date=MIN_DATE,
                        end_date=MAX_DATE,
                        display_format='YYYY-MM-DD',
                        start_date_placeholder_text='Start Date',
                        end_date_placeholder_text='End Date'
                    )
                ], style={'width': '48%', 'display': 'inline-block'}),
            ])
        ], className="filter-card"),

        # KPI Cards
        html.Div(id='kpi-cards', className="kpi-row"),

        # Trend Chart
        html.Div([
            html.Div([
                html.H3("📈 Case Trend Analysis")
            ], className="chart-header"),
            html.Div([
                dcc.Loading(dcc.Graph(id='trend-chart', config={'displayModeBar': False, 'scrollZoom': False}))
            ], className="chart-body")
        ], className="chart-card"),

        # Two Column Layout
        html.Div([
            # Bar Chart
            html.Div([
                html.Div([
                    html.H3("🏆 State-wise Comparison")
                ], className="chart-header"),
                html.Div([
                    dcc.Loading(dcc.Graph(id='bar-chart', config={'displayModeBar': False, 'scrollZoom': False}))
                ], className="chart-body")
            ], className="chart-card"),

            # Pie Chart
            html.Div([
                html.Div([
                    html.H3("🥧 Case Distribution")
                ], className="chart-header"),
                html.Div([
                    dcc.Loading(dcc.Graph(id='pie-chart', config={'displayModeBar': False, 'scrollZoom': False}))
                ], className="chart-body")
            ], className="chart-card"),
        ], className="two-col-grid"),

        # Footer
        html.Div([
            html.P("Data Source: State-wise Daily Reports | Dashboard built with Dash & Plotly"),
            html.P(f"Data Period: {MIN_DATE.strftime('%Y-%m-%d')} to {MAX_DATE.strftime('%Y-%m-%d')}",
                   style={'marginTop': '8px'}),
            html.P("💡 Tip: Hover on data points for exact values",
                   style={'marginTop': '5px', 'color': '#3182ce'})
        ], className="footer")
    ], className="main-container")
])


# ==================== CALLBACKS ====================

@app.callback(
    Output('kpi-cards', 'children'),
    [Input('state-selector', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_kpis(state, start_date, end_date):
    """Update KPI cards based on filters"""
    filtered = df.copy()

    if start_date and end_date:
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        filtered = filtered[(filtered['Date'] >= start_date_obj) & (filtered['Date'] <= end_date_obj)]

    if state != 'All':
        filtered = filtered[filtered['State'] == state]

    total_cases = filtered['Total'].sum()
    recovered = filtered[filtered['Status'] == 'Recovered']['Recovered'].sum()
    deaths = filtered[filtered['Status'] == 'Deceased']['Deceased'].sum()
    active = total_cases - recovered - deaths

    cards = [
        html.Div([
            html.Div("TOTAL CASES", className="kpi-label", style={'color': COLORS['primary']}),
            html.Div(f"{total_cases:,.0f}", className="kpi-number", style={'color': COLORS['primary']}),
            html.Div("Cumulative cases", className="kpi-trend")
        ], className="kpi-card"),

        html.Div([
            html.Div("ACTIVE CASES", className="kpi-label", style={'color': COLORS['active']}),
            html.Div(f"{active:,.0f}", className="kpi-number", style={'color': COLORS['active']}),
            html.Div("Currently infected", className="kpi-trend")
        ], className="kpi-card"),

        html.Div([
            html.Div("RECOVERED", className="kpi-label", style={'color': COLORS['recovered']}),
            html.Div(f"{recovered:,.0f}", className="kpi-number", style={'color': COLORS['recovered']}),
            html.Div("Recovered patients", className="kpi-trend")
        ], className="kpi-card"),

        html.Div([
            html.Div("DEATHS", className="kpi-label", style={'color': COLORS['deaths']}),
            html.Div(f"{deaths:,.0f}", className="kpi-number", style={'color': COLORS['deaths']}),
            html.Div("Fatalities", className="kpi-trend")
        ], className="kpi-card"),
    ]
    return cards


@app.callback(
    Output('trend-chart', 'figure'),
    [Input('state-selector', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_trend(state, start_date, end_date):
    """Update trend line chart - ALWAYS show first and last date on x-axis"""
    filtered = df.copy()

    if start_date and end_date:
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        filtered = filtered[(filtered['Date'] >= start_date_obj) & (filtered['Date'] <= end_date_obj)]

    if state != 'All':
        filtered = filtered[filtered['State'] == state]
        title = f"Daily Cases Trend - {state}"
    else:
        title = "Daily Cases Trend - India"

    daily = filtered.groupby('Date')['Total'].sum().reset_index()
    daily = daily.sort_values('Date')

    fig = go.Figure()

    if not daily.empty:
        fig.add_trace(go.Scatter(
            x=daily['Date'],
            y=daily['Total'],
            mode='lines+markers',
            line=dict(color=COLORS['primary'], width=2.5),
            marker=dict(size=6, color=COLORS['primary']),
            fill='tozeroy',
            fillcolor='rgba(49, 130, 206, 0.1)',
            name='Cases'
        ))

        # Get the date range
        date_list = daily['Date'].tolist()
        first_date = date_list[0]
        last_date = date_list[-1]

        # ALWAYS include first and last date
        if len(date_list) == 1:
            # Only one date
            tick_vals = [first_date]
            tick_text = [first_date.strftime('%Y-%m-%d')]
            tick_angle = 0
        elif len(date_list) <= 10:
            # 2-10 dates - show all
            tick_vals = date_list
            tick_text = [d.strftime('%Y-%m-%d') for d in date_list]
            tick_angle = 45 if len(date_list) > 3 else 0
        else:
            # More than 10 dates - show first, last, and 8 evenly spaced in between
            indices = [0]  # First index
            # Add 8 evenly spaced middle indices
            step = (len(date_list) - 2) / 9
            for i in range(1, 10):
                idx = int(round(i * step))
                if idx not in indices and idx < len(date_list) - 1:
                    indices.append(idx)
            indices.append(len(date_list) - 1)  # Last index
            indices = sorted(set(indices))

            tick_vals = [date_list[i] for i in indices]
            tick_text = [d.strftime('%Y-%m-%d') for d in tick_vals]
            tick_angle = 45

        # Calculate bottom margin based on rotation
        bottom_margin = 100 if tick_angle > 0 else 60
        if len(date_list) <= 3:
            bottom_margin = 50

        fig.update_layout(
            xaxis=dict(
                title="Date",
                tickmode='array',
                tickvals=tick_vals,
                ticktext=tick_text,
                tickangle=tick_angle,
                tickfont=dict(size=11),
                showgrid=True,
                gridcolor='#e2e8f0',
                fixedrange=True,
                range=[first_date - pd.Timedelta(days=1), last_date + pd.Timedelta(days=1)]
            ),
            title=title,
            title_x=0.5,
            title_font=dict(size=14, color=COLORS['text']),
            yaxis=dict(
                title="Number of Cases",
                showgrid=True,
                gridcolor='#e2e8f0',
                fixedrange=True,
                tickformat=',.0f'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            hovermode='x unified',
            margin=dict(l=60, r=30, t=60, b=bottom_margin),
            dragmode=False
        )
    else:
        fig.add_annotation(
            text="No data available for selected filters",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=COLORS['text'])
        )
        fig.update_layout(height=400)

    return fig


@app.callback(
    Output('bar-chart', 'figure'),
    [Input('state-selector', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_bar(state, start_date, end_date):
    """Update bar chart"""
    filtered = df.copy()

    if start_date and end_date:
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        filtered = filtered[(filtered['Date'] >= start_date_obj) & (filtered['Date'] <= end_date_obj)]

    if state != 'All':
        filtered = filtered[filtered['State'] == state]

        total_for_state = filtered['Total'].sum()
        recovered_for_state = filtered[filtered['Status'] == 'Recovered']['Recovered'].sum()
        deaths_for_state = filtered[filtered['Status'] == 'Deceased']['Deceased'].sum()
        active_for_state = total_for_state - recovered_for_state - deaths_for_state

        status_data = pd.DataFrame([
            {'Status': 'Active', 'Total': active_for_state},
            {'Status': 'Recovered', 'Total': recovered_for_state},
            {'Status': 'Deceased', 'Total': deaths_for_state}
        ])

        status_data = status_data[status_data['Total'] > 0]

        fig = px.bar(
            status_data,
            x='Status',
            y='Total',
            title=f'Cases by Status - {state}',
            labels={'Total': 'Number of Cases', 'Status': ''},
            color='Status',
            color_discrete_map={
                'Active': COLORS['active'],
                'Recovered': COLORS['recovered'],
                'Deceased': COLORS['deaths']
            },
            text='Total'
        )
        fig.update_traces(
            textposition='outside',
            texttemplate='%{text:,.0f}',
            textfont=dict(color=COLORS['text'], size=14, weight='bold'),
            marker=dict(cornerradius=8)
        )
        fig.update_layout(
            showlegend=False,
            height=450,
            yaxis=dict(title="Number of Cases", showgrid=True, gridcolor='#e2e8f0', fixedrange=True),
            xaxis=dict(title="", fixedrange=True),
            dragmode=False
        )
    else:
        state_total = filtered.groupby('State')['Total'].sum().sort_values(ascending=False).head(10)
        state_total = state_total.reset_index()

        fig = px.bar(
            state_total,
            x='State',
            y='Total',
            title="Top 10 States by Total Cases",
            labels={'Total': 'Number of Cases', 'State': ''},
            color='Total',
            color_continuous_scale='Blues',
            text='Total'
        )
        fig.update_traces(
            textposition='outside',
            texttemplate='%{text:,.0f}',
            textfont=dict(color=COLORS['text'], size=11, weight='bold'),
            marker=dict(cornerradius=8)
        )
        fig.update_layout(
            showlegend=False,
            height=500,
            yaxis=dict(title="Number of Cases", showgrid=True, gridcolor='#e2e8f0', fixedrange=True),
            xaxis=dict(
                title="",
                tickangle=45,
                tickfont=dict(size=10),
                fixedrange=True
            ),
            margin=dict(l=50, r=30, t=60, b=100),
            dragmode=False
        )

    fig.update_layout(
        title_x=0.5,
        title_font=dict(size=14, color=COLORS['text']),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False)
    )

    return fig


@app.callback(
    Output('pie-chart', 'figure'),
    [Input('state-selector', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_pie(state, start_date, end_date):
    """Update pie chart"""
    filtered = df.copy()

    if start_date and end_date:
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        filtered = filtered[(filtered['Date'] >= start_date_obj) & (filtered['Date'] <= end_date_obj)]

    if state != 'All':
        filtered = filtered[filtered['State'] == state]
        title = f"Case Distribution - {state}"
    else:
        title = "Case Distribution - India"

    total_cases = filtered['Total'].sum()
    recovered = filtered[filtered['Status'] == 'Recovered']['Recovered'].sum()
    deaths = filtered[filtered['Status'] == 'Deceased']['Deceased'].sum()
    active = total_cases - recovered - deaths

    pie_labels = []
    pie_values = []
    pie_colors = []

    if active > 0:
        pie_labels.append('Active')
        pie_values.append(active)
        pie_colors.append(COLORS['active'])
    if recovered > 0:
        pie_labels.append('Recovered')
        pie_values.append(recovered)
        pie_colors.append(COLORS['recovered'])
    if deaths > 0:
        pie_labels.append('Deceased')
        pie_values.append(deaths)
        pie_colors.append(COLORS['deaths'])

    fig = go.Figure()

    if pie_values:
        fig.add_trace(go.Pie(
            labels=pie_labels,
            values=pie_values,
            marker=dict(colors=pie_colors, line=dict(color='white', width=2)),
            hole=0.4,
            textinfo='label+percent',
            textposition='auto',
            textfont=dict(size=13, color='white'),
            insidetextorientation='radial',
            showlegend=True,
            hovertemplate='<b>%{label}</b><br>Cases: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
        ))

        fig.add_annotation(
            text=f"Total<br>{total_cases:,.0f}",
            x=0.5, y=0.5,
            font=dict(size=14, color=COLORS['text'], weight='bold'),
            showarrow=False,
            align='center'
        )
    else:
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=COLORS['text'])
        )

    fig.update_layout(
        title=title,
        title_x=0.5,
        title_font=dict(size=14, color=COLORS['text']),
        height=450,
        showlegend=True,
        legend=dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='right',
            x=0.92,
            font=dict(size=11, color=COLORS['text']),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor=COLORS['border'],
            borderwidth=1
        ),
        margin=dict(l=40, r=140, t=60, b=40)
    )

    return fig


if __name__ == '__main__':
    app.run(debug=True)