import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, dash_table
from sqlalchemy import create_engine

# --- Fix Path for Imports ---
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.db.manager import DB_PATH

# --- Data Loading ---
def load_data():
    """Reads the SQLite DB into a Pandas DataFrame."""
    if not DB_PATH.exists():
        return pd.DataFrame()
    
    # We use raw SQL for speed here
    conn = create_engine(f"sqlite:///{DB_PATH}")
    query = """
    SELECT 
        author, 
        cleaned_text as text, 
        likes, 
        sentiment_label, 
        sentiment_score,
        cluster_id
    FROM comments
    WHERE cleaned_text IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    return df

# --- Initialize App ---
app = Dash(__name__, title="YT Community Pulse")

df = load_data()

# --- Layout ---
app.layout = html.Div([
    html.H1("📺 YouTube Community Pulse", style={'textAlign': 'center', 'fontFamily': 'Arial'}),
    
    # 1. Top Metrics Row
    html.Div([
        html.Div([
            html.H3("Total Comments"),
            html.H1(f"{len(df)}"),
        ], style={'padding': '20px', 'backgroundColor': '#f0f2f6', 'borderRadius': '10px', 'textAlign': 'center', 'width': '30%'}),
        
        html.Div([
            html.H3("Positive Vibe"),
            html.H1(f"{len(df[df['sentiment_label']=='POSITIVE'])}"),
        ], style={'padding': '20px', 'backgroundColor': '#d4edda', 'borderRadius': '10px', 'textAlign': 'center', 'width': '30%'}),
        
        html.Div([
            html.H3("Negative Vibe"),
            html.H1(f"{len(df[df['sentiment_label']=='NEGATIVE'])}"),
        ], style={'padding': '20px', 'backgroundColor': '#f8d7da', 'borderRadius': '10px', 'textAlign': 'center', 'width': '30%'}),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px'}),

    # 2. Charts Row
    html.Div([
        # Left: Sentiment Pie
        html.Div([
            dcc.Graph(
                id='sentiment-pie',
                figure=px.pie(df, names='sentiment_label', title='Sentiment Distribution', 
                              color='sentiment_label',
                              color_discrete_map={'POSITIVE': 'green', 'NEGATIVE': 'red', 'NEUTRAL': 'gray'})
            )
        ], style={'width': '48%'}),
        
        # Right: Cluster Bars
        html.Div([
            dcc.Graph(
                id='cluster-bar',
                figure=px.histogram(df, x='cluster_id', title='Comment Volume by Topic Cluster',
                                    color='cluster_id')
            )
        ], style={'width': '48%'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}),

    # 3. Data Table (Interactive)
    html.H3("📝 Deep Dive: Read the Comments"),
    dash_table.DataTable(
        id='comments-table',
        columns=[
            {"name": "Author", "id": "author"},
            {"name": "Comment", "id": "text"},
            {"name": "Sentiment", "id": "sentiment_label"},
            {"name": "Likes", "id": "likes"},
        ],
        data=df.to_dict('records'),
        page_size=10,
        style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Arial'},
        style_header={'backgroundColor': 'black', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{sentiment_label} = NEGATIVE'},
                'backgroundColor': '#ffeeba'
            }
        ],
        sort_action="native",
        filter_action="native", # Allows you to type "Python" in the header to search!
    )
], style={'padding': '50px', 'maxWidth': '1200px', 'margin': '0 auto'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)