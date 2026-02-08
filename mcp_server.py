import pandas as pd
from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("LotteWorld-Deep-Analyzer")

def load_and_unify_data():
    kakao_path = "/app/database/preprocessed_reviews_kakao.csv"
    trip_path = "/app/database/preprocessed_reviews_tripdotcom.csv"
    try:
        df_kakao = pd.read_csv(kakao_path)
        df_trip = pd.read_csv(trip_path)
        df = pd.concat([df_kakao, df_trip], ignore_index=True)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month_name()
        df['weekday'] = df['date'].dt.day_name()
        df['is_weekend'] = df['weekday'].isin(['Saturday', 'Sunday'])
        return df
    except Exception as e:
        print(f"--- [ERROR] Data Load Failed: {e} ---", flush=True)
        return pd.DataFrame()


@mcp.tool(name="get_sentiment_summary")
def get_sentiment_summary() -> str:
    """Calculates overall sentiment metrics and average ratings."""
    df = load_and_unify_data()
    if df.empty: return "Data not available."
    avg_rating = df['rating'].mean()
    pos_ratio = (df['is_positive'].sum() / len(df)) * 100
    return (f"Overall Analysis:\n- Total Reviews: {len(df)}\n"
            f"- Average Rating: {avg_rating:.2f}/5.0\n"
            f"- Positive Review Ratio: {pos_ratio:.1f}%")

@mcp.tool(name="analyze_crowd_impact")
def analyze_crowd_impact() -> str:
    """Compares visitor satisfaction between Weekdays and Weekends."""
    df = load_and_unify_data()
    if df.empty: return "Data not available."
    stats = df.groupby('is_weekend')['rating'].mean().to_dict()
    weekend_avg = stats.get(True, 0)
    weekday_avg = stats.get(False, 0)
    advice = "Weekdays are significantly better." if (weekday_avg - weekend_avg) > 0.3 else "Satisfaction is consistent."
    return f"Weekday: {weekday_avg:.2f}, Weekend: {weekend_avg:.2f}. Insight: {advice}"

@mcp.tool(name="get_seasonal_trends")
def get_seasonal_trends() -> str:
    """Identifies seasonal satisfaction levels."""
    df = load_and_unify_data()
    if df.empty: return "Data not available."
    monthly = df.groupby('month')['rating'].mean().sort_values(ascending=False)
    return f"Best Month: {monthly.idxmax()} ({monthly.max():.2f})"

@mcp.tool(name="extract_high_value_complaints")
def extract_high_value_complaints(min_length: int = 100) -> str:
    """Filters for long, negative reviews."""
    df = load_and_unify_data()
    if df.empty: return "Data not available."
    critical_df = df[(df['rating'] <= 2) & (df['content_length'] >= min_length)]
    if critical_df.empty: return "No significant complaints found."
    samples = critical_df['content'].head(3).tolist()
    return f"Found {len(critical_df)} complaints. Samples:\n" + "\n---\n".join(samples)


registered = [t.name for t in mcp._tool_manager.list_tools()]
print(f"--- [CRITICAL DEBUG] Registered Tools: {registered} ---", flush=True)

if __name__ == "__main__":
    import uvicorn
    print("--- [BOOT] Starting Uvicorn for MCP Server ---", flush=True)
    uvicorn.run(mcp.sse_app, host="0.0.0.0", port=8000)