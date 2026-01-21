import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import argparse

def plot_rating_distribution(df, base_name, output_dir):
    """Plot 1: Rating distribution"""
    plt.figure(figsize=(10, 6))
    sns.countplot(x='rating', data=df)
    plt.title(f'{base_name} Distribution of Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, f'{base_name}_rating_distribution.png'))
    plt.close()

def plot_content_length_distribution(df, base_name, output_dir):
    """Plot 2: Content length distribution"""
    plt.figure(figsize=(10, 6))
    sns.histplot(df['content_length'], bins=50, kde=True)
    plt.title(f'{base_name} Distribution of Review Content Length')
    plt.xlabel('Content Length')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, f'{base_name}_review_length_distribution.png'))
    plt.close()

def plot_reviews_by_month(df, base_name, output_dir):
    """Plot 3: Reviews by month"""
    plt.figure(figsize=(10, 6))
    sns.countplot(x='month', data=df.sort_values('month'))
    plt.title(f'{base_name} Number of Reviews by Month')
    plt.xlabel('Month')
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, f'{base_name}_reviews_by_month.png'))
    plt.close()

def plot_reviews_by_weekday(df, base_name, output_dir):
    """Plot 4: Reviews by weekday"""
    plt.figure(figsize=(10, 6))
    sns.countplot(x='weekday', data=df, order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    plt.title(f'{base_name} Number of Reviews by Weekday')
    plt.xlabel('Weekday')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(output_dir, f'{base_name}_reviews_by_weekday.png'))
    plt.close()

def plot_rating_distribution_comparison(dfs, base_names, output_dir):
    """Comparison Plot: Rating distribution"""
    plt.figure(figsize=(10, 6))
    for df, name in zip(dfs, base_names):
        sns.kdeplot(df['rating'], label=name, clip=(1, 5))
    plt.title('Comparison of Rating Distributions')
    plt.xlabel('Rating')
    plt.ylabel('Density')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'comparison_rating_distribution.png'))
    plt.close()

def plot_content_length_distribution_comparison(dfs, base_names, output_dir):
    """Comparison Plot: Content length distribution"""
    plt.figure(figsize=(10, 6))
    for df, name in zip(dfs, base_names):
        sns.kdeplot(df['content_length'], label=name)
    plt.title('Comparison of Review Content Length Distributions')
    plt.xlabel('Content Length')
    plt.ylabel('Density')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'comparison_content_length_distribution.png'))
    plt.close()

def plot_reviews_by_month_comparison(dfs, base_names, output_dir):
    """Comparison Plot: Reviews by month"""
    plt.figure(figsize=(12, 7))
    
    combined_data = pd.DataFrame()
    for df, name in zip(dfs, base_names):
        monthly_counts = df['month'].value_counts().reset_index()
        monthly_counts.columns = ['month', 'count']
        monthly_counts['source'] = name
        combined_data = pd.concat([combined_data, monthly_counts])

    sns.barplot(x='month', y='count', hue='source', data=combined_data)
    plt.title('Comparison of Number of Reviews by Month')
    plt.xlabel('Month')
    plt.ylabel('Count')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'comparison_reviews_by_month.png'))
    plt.close()

def plot_reviews_by_weekday_comparison(dfs, base_names, output_dir):
    """Comparison Plot: Reviews by weekday"""
    plt.figure(figsize=(12, 7))
    
    combined_data = pd.DataFrame()
    for df, name in zip(dfs, base_names):
        weekday_counts = df['weekday'].value_counts().reset_index()
        weekday_counts.columns = ['weekday', 'count']
        weekday_counts['source'] = name
        combined_data = pd.concat([combined_data, weekday_counts])

    sns.barplot(x='weekday', y='count', hue='source', data=combined_data, order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    plt.title('Comparison of Number of Reviews by Weekday')
    plt.xlabel('Weekday')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'comparison_reviews_by_weekday.png'))
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Generate EDA charts for review data.')
    parser.add_argument('input_files', type=str, nargs='+', help='Path to one or more input CSV files.')
    parser.add_argument('--all', action='store_true', help='Generate all EDA charts.')
    parser.add_argument('--rating-distribution', action='store_true', help='Generate rating distribution chart.')
    parser.add_argument('--content-length-distribution', action='store_true', help='Generate content length distribution chart.')
    parser.add_argument('--reviews-by-month', action='store_true', help='Generate reviews by month chart.')
    parser.add_argument('--reviews-by-weekday', action='store_true', help='Generate reviews by weekday chart.')
    
    args = parser.parse_args()

    for file_path in args.input_files:
        if not os.path.exists(file_path):
            print(f"Error: Input file not found at {file_path}")
            return

    output_dir = 'review_analysis/plot'
    os.makedirs(output_dir, exist_ok=True)

    if len(args.input_files) == 1:
        input_file = args.input_files[0]
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        df = pd.read_csv(input_file)

        if args.all or args.rating_distribution:
            plot_rating_distribution(df, base_name, output_dir)
        
        if args.all or args.content_length_distribution:
            plot_content_length_distribution(df, base_name, output_dir)
            
        if args.all or args.reviews_by_month:
            plot_reviews_by_month(df, base_name, output_dir)

        if args.all or args.reviews_by_weekday:
            plot_reviews_by_weekday(df, base_name, output_dir)

        print(f"Selected EDA charts for '{base_name}' saved to '{output_dir}' directory.")
    else:
        dfs = [pd.read_csv(file) for file in args.input_files]
        base_names = [os.path.splitext(os.path.basename(file))[0] for file in args.input_files]

        if args.all or args.rating_distribution:
            plot_rating_distribution_comparison(dfs, base_names, output_dir)
        
        if args.all or args.content_length_distribution:
            plot_content_length_distribution_comparison(dfs, base_names, output_dir)
            
        if args.all or args.reviews_by_month:
            plot_reviews_by_month_comparison(dfs, base_names, output_dir)

        if args.all or args.reviews_by_weekday:
            plot_reviews_by_weekday_comparison(dfs, base_names, output_dir)
        
        print(f"Comparison EDA charts for {len(dfs)} files saved to '{output_dir}' directory.")


if __name__ == '__main__':
    main()
