
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import json
from schema import load_data
from styles import colors, HEADER_STYLE, CARD_STYLE, PAGE_STYLE, FILTER_STYLE

# ✅ Load data
df = load_data(r"C:\Users\Olatunbosunno\Downloads\New Transport Data.xlsx")

# ✅ Load GeoJSON for Nigeria states
with open(r"C:\Users\Olatunbosunno\Desktop\GROUP 8 GROUP PROJECT ON TRANSPORTATION SECTOR.PY\dashboard\ng.json") as f:
    nigeria_geojson = json.load(f)

# ✅ Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ✅ Layout
app.layout = html.Div(style=PAGE_STYLE, children=[
    html.H1("Nigeria Road Accident Analysis Dashboard (2021-2025)", style=HEADER_STYLE),

    # Filters
    html.Div([
        html.Label("Select Year Range:", style={'marginRight': '10px'}),
        dcc.RangeSlider(id='year-slider',
                        min=df['YEAR'].min(),
                        max=df['YEAR'].max(),
                        step=1,
                        marks={int(y): str(y) for y in sorted(df['YEAR'].unique())},
                        value=[df['YEAR'].min(), df['YEAR'].max()]),
        html.Br(),
        html.Label("Select State:", style={'marginRight': '10px'}),
        dcc.Dropdown(id='state-filter',
                     options=[{'label': 'All', 'value': 'All'}] + [{'label': s, 'value': s} for s in sorted(df['STATE'].unique())],
                     value='All',
                     style={'color': colors['text'], 'backgroundColor': colors['card']})
    ], style=FILTER_STYLE),

    # KPI Cards
    dbc.Row(id='kpi-cards'),

    # Charts
    dbc.Row([
        dbc.Col(dcc.Graph(id='top-causes'), md=4),
        dbc.Col(dcc.Graph(id='yearly-casualty'), md=4),
        dbc.Col(dcc.Graph(id='deaths-zone'), md=4),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='severity-dist'), md=6),
        dbc.Col(dcc.Graph(id='map-visual'), md=6),
    ])
])

# ✅ Callback for interactivity
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('top-causes', 'figure'),
     Output('yearly-casualty', 'figure'),
     Output('deaths-zone', 'figure'),
     Output('severity-dist', 'figure'),
     Output('map-visual', 'figure')],
    [Input('year-slider', 'value'),
     Input('state-filter', 'value'),
     Input('top-causes', 'clickData')]
)
def update_dashboard(year_range, selected_state, clickData):
    filtered_df = df[(df['YEAR'] >= year_range[0]) & (df['YEAR'] <= year_range[1])]
    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['STATE'] == selected_state]
    if clickData:
        clicked_state = clickData['points'][0]['y']
        filtered_df = filtered_df[filtered_df['STATE'] == clicked_state]

    # ✅ KPIs
    total_accidents = filtered_df['TOTAL CASES'].sum()
    total_deaths = filtered_df['NUMBER KILLED'].sum()
    total_injured = filtered_df['NUMBER INJURED'].sum()
    total_persons = filtered_df['PEOPLE INVOLVED'].sum()
    fatality_rate = (total_deaths / total_persons) * 100 if total_persons > 0 else 0

    kpi_cards = dbc.Row([
        dbc.Col(html.Div([html.H4("Road Accidents"), html.H2(f"{total_accidents:,}")], style=CARD_STYLE)),
        dbc.Col(html.Div([html.H4("Deaths"), html.H2(f"{total_deaths:,}")], style=CARD_STYLE)),
        dbc.Col(html.Div([html.H4("Injured"), html.H2(f"{total_injured:,}")], style=CARD_STYLE)),
        dbc.Col(html.Div([html.H4("Persons Involved"), html.H2(f"{total_persons:,}")], style=CARD_STYLE)),
        dbc.Col(html.Div([html.H4("Fatality Rate"), html.H2(f"{fatality_rate:.1f}%")], style=CARD_STYLE)),
    ])

    # ✅ Charts
    top_causes = filtered_df.groupby('STATE')['TOTAL CASES'].sum().nlargest(10).reset_index()
    fig_top_causes = px.bar(top_causes, x='TOTAL CASES', y='STATE', orientation='h',
                            color='TOTAL CASES', color_continuous_scale=['#14532d', '#32cd32'],
                            title='Top Ten Accident Causes')

    yearly_casualty = filtered_df.groupby('YEAR')['TOTAL CASUALTY'].sum().reset_index()
    fig_yearly = px.line(yearly_casualty, x='YEAR', y='TOTAL CASUALTY', markers=True)
    fig_yearly.update_traces(line_color=colors['accent'])

    deaths_zone = filtered_df.groupby('GEOGRAPHIC ZONE')['NUMBER KILLED'].sum().reset_index()
    fig_deaths_zone = px.bar(deaths_zone, x='NUMBER KILLED', y='GEOGRAPHIC ZONE', orientation='h',
                              color='NUMBER KILLED', color_continuous_scale=['#14532d', '#32cd32'])

    severity_dist = filtered_df.groupby('YEAR')[['FATAL', 'SERIOUS', 'MINOR']].sum().reset_index()
    fig_severity = go.Figure()
    fig_severity.add_trace(go.Bar(x=severity_dist['YEAR'], y=severity_dist['FATAL'], name='Fatal', marker_color='#14532d'))
    fig_severity.add_trace(go.Bar(x=severity_dist['YEAR'], y=severity_dist['SERIOUS'], name='Serious', marker_color='#228B22'))
    fig_severity.add_trace(go.Bar(x=severity_dist['YEAR'], y=severity_dist['MINOR'], name='Minor', marker_color='#32cd32'))
    fig_severity.update_layout(barmode='stack', title='Accident Severity Distribution')

    # ✅ Choropleth Map
    map_data = filtered_df.groupby('STATE')[['NUMBER KILLED', 'NUMBER INJURED']].sum().reset_index()
    fig_map = px.choropleth(
        map_data,
        geojson=nigeria_geojson,
        locations='STATE',
        featureidkey='properties.name',
        color='NUMBER KILLED',
        hover_data=['NUMBER INJURED'],
        color_continuous_scale=['#14532d', '#32cd32'],
        title="Killed & Injured by State"
    )
    fig_map.update_geos(fitbounds="locations", visible=False)

    return kpi_cards, fig_top_causes, fig_yearly, fig_deaths_zone, fig_severity, fig_map

if __name__ == "__main__":
    app.run(debug=True)
