
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os

from queries import load_fact
from visuals import apply_theme
import styles

#  Load data
fact_df = load_fact()

#  Load GeoJSON
geojson_path = os.path.join(os.path.dirname(__file__), "ng.json")
try:
    with open(geojson_path) as f:
        nigeria_geojson = json.load(f)
except FileNotFoundError:
    nigeria_geojson = None

#  Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(style=styles.PAGE_STYLE, children=[
    html.H1("Nigeria Road Accident Analysis Dashboard (2021-2025)", style=styles.HEADER_STYLE),

    # Filters
    html.Div([
        html.Label("Select Year Range:"),
        dcc.RangeSlider(id='year-slider',
                        min=fact_df['YEAR'].min(),
                        max=fact_df['YEAR'].max(),
                        step=1,
                        marks={int(y): str(y) for y in sorted(fact_df['YEAR'].unique())},
                        value=[fact_df['YEAR'].min(), fact_df['YEAR'].max()]),
        html.Br(),
        html.Label("Select State:"),
        dcc.Dropdown(id='state-filter',
                     options=[{'label': 'All', 'value': 'All'}] + [{'label': s, 'value': s} for s in sorted(fact_df['STATE'].unique())],
                     value='All',
                     style={'color': styles.colors['text'], 'backgroundColor': styles.colors['card']})
    ], style=styles.FILTER_STYLE),

    # KPI Cards
    dbc.Row(id='kpi-cards'),

    # Charts Layout
    dbc.Row([
        dbc.Col(dcc.Graph(id='top-causes'), md=4),
        dbc.Col(dcc.Graph(id='yearly-casualty'), md=4),
        dbc.Col(dcc.Graph(id='deaths-zone'), md=4),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='severity-dist'), md=6),
        dbc.Col(dcc.Graph(id='map-visual'), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='speed-analysis'), md=6),
        dbc.Col(dcc.Graph(id='yearly-crashes'), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='zone-accidents'), md=6),
        dbc.Col(dcc.Graph(id='top-deaths'), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='lowest-accidents'), md=12),
    ])
])

@app.callback(
    [Output('kpi-cards', 'children'),
     Output('top-causes', 'figure'),
     Output('yearly-casualty', 'figure'),
     Output('deaths-zone', 'figure'),
     Output('severity-dist', 'figure'),
     Output('map-visual', 'figure'),
     Output('speed-analysis', 'figure'),
     Output('yearly-crashes', 'figure'),
     Output('zone-accidents', 'figure'),
     Output('top-deaths', 'figure'),
     Output('lowest-accidents', 'figure')],
    [Input('year-slider', 'value'),
     Input('state-filter', 'value')]
)
def update_dashboard(year_range, selected_state):
    filtered_df = fact_df[(fact_df['YEAR'] >= year_range[0]) & (fact_df['YEAR'] <= year_range[1])]
    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['STATE'] == selected_state]

    #  KPIs
    total_accidents = filtered_df['TOTAL CASES'].sum()
    total_deaths = filtered_df['NUMBER KILLED'].sum()
    total_injured = filtered_df['NUMBER INJURED'].sum()
    total_persons = filtered_df['PEOPLE INVOLVED'].sum()
    fatality_rate = (total_deaths / total_persons) * 100 if total_persons > 0 else 0

    kpi_cards = dbc.Row([
        dbc.Col(html.Div([html.H4("Road Accidents"), html.H2(f"{total_accidents:,}")], style=styles.CARD_STYLE)),
        dbc.Col(html.Div([html.H4("Deaths"), html.H2(f"{total_deaths:,}")], style=styles.CARD_STYLE)),
        dbc.Col(html.Div([html.H4("Injured"), html.H2(f"{total_injured:,}")], style=styles.CARD_STYLE)),
        dbc.Col(html.Div([html.H4("Persons Involved"), html.H2(f"{total_persons:,}")], style=styles.CARD_STYLE)),
        dbc.Col(html.Div([html.H4("Fatality Rate"), html.H2(f"{fatality_rate:.1f}%")], style=styles.CARD_STYLE)),
    ])

    # 1. Top Ten Accident Causes
    cause_cols = ['SPEEDING', 'PHONE USE', 'TYRE BURST', 'MECHANICAL FAULT', 'BRAKE FAILURE', 'OVERLOADING',
                  'DANGEROUS OVERTAKE', 'WRONGFUL OVERTAKE', 'RECKLESS DRIVING', 'SIGNAL VIOLATION', 'OTHERS']
    cause_data = filtered_df[cause_cols].sum().sort_values(ascending=False).nlargest(10)
    fig_top_causes = px.bar(cause_data, x=cause_data.values, y=cause_data.index, orientation='h',
                        title='Top Ten Accident Causes')
    fig_top_causes.update_traces(marker_color='#006400')  # Dark green bars
    fig_top_causes = apply_theme(fig_top_causes)

    # 2. Total Yearly Casualty
    yearly_casualty = filtered_df.groupby('YEAR')['TOTAL CASUALTY'].sum().reset_index()
    fig_yearly_casualty = px.line(yearly_casualty, x='YEAR', y='TOTAL CASUALTY', markers=True,
                              title='Total Yearly Casualty')
    fig_yearly_casualty.update_traces(line_color='#006400')  # Dark green line
    fig_yearly_casualty = apply_theme(fig_yearly_casualty)

    #  3. Total Deaths by Zone
    deaths_zone = filtered_df.groupby('GEOGRAPHIC ZONE')['NUMBER KILLED'].sum().reset_index()
    fig_deaths_zone = px.bar(deaths_zone, x='NUMBER KILLED', y='GEOGRAPHIC ZONE', orientation='h',
                             title='Total Deaths by Zone')
    fig_deaths_zone.update_traces(marker_color='#32CD32')
    fig_deaths_zone = apply_theme(fig_deaths_zone)

    #  4. Severity Distribution (Green Shades)
    severity_dist = filtered_df.groupby('YEAR')[['FATAL', 'SERIOUS', 'MINOR']].sum().reset_index()
    fig_severity = go.Figure()
    fig_severity.add_trace(go.Bar(x=severity_dist['YEAR'], y=severity_dist['FATAL'], name='Fatal', marker_color='#004d00'))
    fig_severity.add_trace(go.Bar(x=severity_dist['YEAR'], y=severity_dist['SERIOUS'], name='Serious', marker_color='#228B22'))
    fig_severity.add_trace(go.Bar(x=severity_dist['YEAR'], y=severity_dist['MINOR'], name='Minor', marker_color='#32CD32'))
    fig_severity.update_layout(barmode='stack', title='Severity Distribution')
    fig_severity = apply_theme(fig_severity)

    #  5. Map of Killed & Injured by State
    if nigeria_geojson:
        map_data = filtered_df.groupby('STATE')[['NUMBER KILLED', 'NUMBER INJURED']].sum().reset_index()
        fig_map = px.choropleth(map_data, geojson=nigeria_geojson, locations='STATE', featureidkey='properties.name',
                                color='NUMBER KILLED', hover_data=['NUMBER INJURED'],
                                color_continuous_scale=['#14532d', '#32cd32'], title="Killed & Injured by State")
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map = apply_theme(fig_map)
    else:
        fig_map = apply_theme(go.Figure().add_annotation(text="GeoJSON missing", showarrow=False))

    #  6. Speeding Analysis Over Years
    speed_trend = filtered_df.groupby('YEAR')['SPEEDING'].sum().reset_index()
    fig_speed = px.line(speed_trend, x='YEAR', y='SPEEDING', markers=True, title='Speeding Analysis Over Years')
    fig_speed.update_traces(line_color='#32CD32')
    fig_speed = apply_theme(fig_speed)

    #  7. Total Crashes Each Year
    yearly_crashes = filtered_df.groupby('YEAR')['TOTAL CASES'].sum().reset_index()
    fig_yearly_crashes = px.bar(yearly_crashes, x='YEAR', y='TOTAL CASES', title='Total Crashes Each Year')
    fig_yearly_crashes.update_traces(marker_color='#32CD32')
    fig_yearly_crashes = apply_theme(fig_yearly_crashes)

    #  8. Zone with Most Accidents
    zone_accidents = filtered_df.groupby('GEOGRAPHIC ZONE')['TOTAL CASES'].sum().reset_index()
    fig_zone_accidents = px.bar(zone_accidents, x='TOTAL CASES', y='GEOGRAPHIC ZONE', orientation='h',
                                title='Zone with Most Accidents')
    fig_zone_accidents.update_traces(marker_color='#32CD32')
    fig_zone_accidents = apply_theme(fig_zone_accidents)

    # 9. States with Highest Deaths (Top 5)
    top_deaths = filtered_df.groupby('STATE')['NUMBER KILLED'].sum().nlargest(5).reset_index()
    fig_top_deaths = px.bar(top_deaths, x='NUMBER KILLED', y='STATE', orientation='h',
                            title='States with Highest Deaths (Top 5)')
    fig_top_deaths.update_traces(marker_color='#32CD32')
    fig_top_deaths = apply_theme(fig_top_deaths)

    #  10. States with Lowest Accident Cases (Donut)
    lowest_states = filtered_df.groupby('STATE')['TOTAL CASES'].sum().nsmallest(3).reset_index()
    fig_lowest_accidents = px.pie(lowest_states, names='STATE', values='TOTAL CASES', hole=0.4,
                                  title='States with Lowest Accident Cases',
                                  color_discrete_sequence=['#006400', '#228B22', '#32CD32'])
    fig_lowest_accidents = apply_theme(fig_lowest_accidents)

    return (kpi_cards, fig_top_causes, fig_yearly_casualty, fig_deaths_zone, fig_severity, fig_map,
            fig_speed, fig_yearly_crashes, fig_zone_accidents, fig_top_deaths, fig_lowest_accidents)

if __name__ == "__main__":
    app.run(debug=True)
