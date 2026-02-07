import pandas as pd
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import os
# 1. Initialize FastMCP
mcp = FastMCP("LotteWorld-Deep-Analyzer")

# 2. Data Loading & Preprocessing Logic
def load_and_unify_data():
    """
    Loads Kakao and Tripadvisor datasets and ensures uniform formatting.
    """
    # Define your local paths here
    kakao_path = "./database/preprocessed_reviews_kakao.csv"
    trip_path = "./database/preprocessed_reviews_tripdotcom.csv"
    # base_path = os.path.dirname(os.path.abspath(__file__))
    # kakao_path = os.path.join(base_path, "data", "kakao_reviews.csv")
    # trip_path = os.path.join(base_path, "data", "trip_advisor_reviews.csv")
    
    try:
        df_kakao = pd.read_csv(kakao_path)
        df_trip = pd.read_csv(trip_path)
        
        # Combine datasets
        df = pd.concat([df_kakao, df_trip], ignore_index=True)
        
        # Ensure 'date' is a datetime object
        df['date'] = pd.to_datetime(df['date'])
        
        # Feature Engineering: Re-derive to ensure 100% accuracy
        df['month'] = df['date'].dt.month_name()
        df['weekday'] = df['date'].dt.day_name()
        df['is_weekend'] = df['weekday'].isin(['Saturday', 'Sunday'])
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# --- MCP TOOLS ---

@mcp.tool()
def get_sentiment_summary() -> str:
    """
    Calculates overall sentiment metrics and average ratings across both platforms.
    """
    df = load_and_unify_data()
    if df.empty: return "Data not available."

    avg_rating = df['rating'].mean()
    pos_ratio = (df['is_positive'].sum() / len(df)) * 100
    
    return (f"Overall Analysis:\n"
            f"- Total Reviews: {len(df)}\n"
            f"- Average Rating: {avg_rating:.2f}/5.0\n"
            f"- Positive Review Ratio: {pos_ratio:.1f}%")

@mcp.tool()
def analyze_crowd_impact() -> str:
    """
    Compares visitor satisfaction between Weekdays and Weekends.
    Useful for advising users on when to visit.
    """
    df = load_and_unify_data()
    if df.empty: return "Data not available."

    stats = df.groupby('is_weekend')['rating'].mean().to_dict()
    weekend_avg = stats.get(True, 0)
    weekday_avg = stats.get(False, 0)
    
    diff = weekday_avg - weekend_avg
    advice = "Weekdays are significantly better." if diff > 0.3 else "Satisfaction is consistent across the week."
    
    return (f"Crowd Impact Analysis:\n"
            f"- Weekday Avg Rating: {weekday_avg:.2f}\n"
            f"- Weekend Avg Rating: {weekend_avg:.2f}\n"
            f"- Insight: {advice}")

@mcp.tool()
def get_seasonal_trends() -> str:
    """
    Identifies which months have the highest and lowest satisfaction levels.
    """
    df = load_and_unify_data()
    if df.empty: return "Data not available."

    monthly_stats = df.groupby('month')['rating'].mean().sort_values(ascending=False)
    best_month = monthly_stats.idxmax()
    worst_month = monthly_stats.idxmin()
    
    return (f"Seasonal Trend Analysis:\n"
            f"- Best Month for Visitors: {best_month} ({monthly_stats[best_month]:.2f})\n"
            f"- Worst Month for Visitors: {worst_month} ({monthly_stats[worst_month]:.2f})")

@mcp.tool()
def extract_high_value_complaints(min_length: int = 100) -> str:
    """
    Filters for long, negative reviews to find specific operational pain points.
    """
    df = load_and_unify_data()
    if df.empty: return "Data not available."

    # Filter: Low rating and high content length
    critical_df = df[(df['rating'] <= 2) & (df['content_length'] >= min_length)]
    
    if critical_df.empty:
        return "No significant detailed complaints found."
    
    # Return the first 3 major complaints as examples
    samples = critical_df['content'].head(3).tolist()
    formatted_samples = "\n---\n".join(samples)
    
    return f"Found {len(critical_df)} detailed complaints. Top issues:\n\n{formatted_samples}"

if __name__ == "__main__":
    mcp.run()