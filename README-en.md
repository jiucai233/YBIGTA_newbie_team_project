## WEB homework usage guide

The web application is a simple user management system built with FastAPI. It provides endpoints for user registration, login, password updates, and account deletion.

### How to run

1.  Make sure you have all the required packages installed. You can install them using pip:
    ```bash
    pip install -r requirements.txt
    ```
2.  To run the web application, execute the `main.py` file in the `app` directory:
    ```bash
    python app/main.py
    ```
3.  The application will be available at `http://localhost:8000`. You can access the user interface by opening this URL in your web browser.

## Crawling homework usage guide

The project includes crawlers for Google Maps, Kakao Maps, and Trip.com. The crawlers use Selenium to scrape reviews from the respective websites.

### How to run

1.  To run the crawlers, you need to execute the `main.py` file in the `review_analysis/crawling` directory.
2.  You can run a specific crawler or all of them at once.

    *   **Run a specific crawler:**
        ```bash
        python review_analysis/crawling/main.py -c [crawler_name] -o ../../database
        ```
        Replace `[crawler_name]` with one of `google`, `kakao`, or `tripdotcom`.

    *   **Run all crawlers:**
        ```bash
        python review_analysis/crawling/main.py -a -o ../../database
        ```
3.  The scraped data will be saved as CSV files in the `database` directory.

## EDA/FE homework usage guide

The project includes scripts for preprocessing the crawled data, performing feature engineering, and generating EDA plots and reports.

### Preprocessing and Feature Engineering

The preprocessing steps include data cleaning, null value handling, and text preprocessing. Feature engineering includes adding columns like `content_length` and `is_positive`, and generating TF-IDF embeddings.

#### How to run

1.  To run the preprocessing and feature engineering, execute the `main.py` file in the `review_analysis/preprocessing` directory.
2.  You can run a specific preprocessor or all of them at once.

    *   **Run a specific preprocessor:**
        ```bash
        python review_analysis/preprocessing/main.py -c [preprocessor_name]
        ```
        Replace `[preprocessor_name]` with one of `reviews_google`, `reviews_kakao`, or `reviews_tripdotcom`.

    *   **Run all preprocessors:**
        ```bash
        python review_analysis/preprocessing/main.py -a -o ../../database
        ```
3.  The processed data will be saved as new CSV files (with the `preprocessed_` prefix) in the `database` directory. The TF-IDF embeddings will also be saved to separate CSV files.
