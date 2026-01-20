
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Generate EDA charts for review data.')
    parser.add_argument('input_file', type=str, help='Path to the input CSV file.')
    args = parser.parse_args()

    input_file = args.input_file
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return

    # Create output directory
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = 'review_analysis/plot'
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    df = pd.read_csv(input_file)

    # Plot 1: Rating distribution
    plt.figure(figsize=(10, 6))
    sns.countplot(x='rating', data=df)
    plt.title('Distribution of Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, f'{base_name}rating_distribution.png'))
    plt.close()

    # Plot 2: Content length distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['content_length'], bins=50, kde=True)
    plt.title('Distribution of Review Content Length')
    plt.xlabel('Content Length')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, f'{base_name}content_length_distribution.png'))
    plt.close()
    
    # Plot 3: Reviews by month
    plt.figure(figsize=(10, 6))
    sns.countplot(x='month', data=df.sort_values('month'))
    plt.title('Number of Reviews by Month')
    plt.xlabel('Month')
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, f'{base_name}reviews_by_month.png'))
    plt.close()

    # Plot 4: Reviews by weekday
    plt.figure(figsize=(10, 6))
    sns.countplot(x='weekday', data=df, order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    plt.title('Number of Reviews by Weekday')
    plt.xlabel('Weekday')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(output_dir, f'{base_name}reviews_by_weekday.png'))
    plt.close()

    print(f"EDA charts saved to '{output_dir}' directory.")

if __name__ == '__main__':
    main()
