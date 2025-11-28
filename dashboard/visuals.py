
def apply_theme(fig):
    fig.update_layout(
        template="plotly_white",  # White chart background
        paper_bgcolor="#FFFFFF",  # White dashboard background
        plot_bgcolor="#FFFFFF",   # White chart background
        font=dict(color="#006400"),  # Dark green text
        title_font=dict(size=18, color="#006400"),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig
