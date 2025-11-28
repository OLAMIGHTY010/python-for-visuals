
"""
visuals.py
Plotly visualizations for dashboard
"""

import plotly.express as px
import styles

def apply_theme(fig):
    fig.update_layout(template="plotly_dark",
                      paper_bgcolor=styles.colors["background"],
                      plot_bgcolor=styles.colors["background"],
                      font=dict(color=styles.colors["text"]))
    return fig

def trend_over_time(df):
    trend = df.groupby("YEAR")["TOTAL CASES"].sum().reset_index()
    fig = px.line(trend, x="YEAR", y="TOTAL CASES", title="Trend of Road Accidents Over Time", markers=True)
    return apply_theme(fig)

def crash_severity_composition(df):
    severity_totals = df[["FATAL", "SERIOUS", "MINOR"]].sum().reset_index()
    severity_totals.columns = ["Severity", "Count"]
    fig = px.pie(severity_totals, names="Severity", values="Count", hole=0.4, title="Crash Severity Composition")
    return apply_theme(fig)

def gender_impact(df):
    fig = px.bar(df, x="GENDER", y="TOTAL KILLED", color="AGE GROUP", barmode="group", title="Fatalities by Gender and Age Group")
    return apply_theme(fig)

def vehicle_type_distribution(df):
    fig = px.bar(df, x="VehicleType", y="Count", title="Vehicle Types Involved in Crashes", color="VehicleType")
    return apply_theme(fig)

def top_causes(df):
    fig = px.bar(df.sort_values(by="Count", ascending=False), x="Cause", y="Count", title="Leading Causes of Road Accidents", color="Cause")
    return apply_theme(fig)

def regional_comparison(df):
    region_totals = df.groupby("Region")["TOTAL CASES"].sum().reset_index()
    fig = px.bar(region_totals.sort_values(by="TOTAL CASES", ascending=False), x="Region", y="TOTAL CASES", title="Crashes by Region", color="Region")
    return apply_theme(fig)
