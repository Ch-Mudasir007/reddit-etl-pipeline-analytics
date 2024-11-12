# ETL Pipeline for Reddit Data Analytics Using AWS, Docker, Airflow, dbt, and Tableau

This repository contains the code and configurations for an **ETL (Extract, Transform, Load) pipeline** designed to gather data from the **Reddit API**, process and store it on **AWS**, and visualize it on **Tableau**. The pipeline is modular, scalable, and easy to deploy, leveraging Docker and Airflow for orchestration and dbt for data transformation within Redshift.

## Project Overview

This project aims to automate the process of gathering, transforming, and analyzing data from Reddit to gain insights on user engagement, sentiment, trends, and more. The pipeline is built to:
1. Extract data from the Reddit API.
2. Store the raw data in Amazon S3.
3. Load the data into Amazon Redshift for storage.
4. Use dbt to transform the data in Redshift, preparing it for analysis.
5. Visualize the transformed data in Tableau for interactive exploration and insights.

### Key Features

- **Automated Data Extraction**: Retrieves Reddit posts, comments, and metadata based on specific criteria (e.g., subreddit, keywords).
- **Scalable Storage**: Stores raw data in Amazon S3, providing durability and scalability.
- **Data Transformation with dbt**: Transforms and models data in Amazon Redshift for efficient querying.
- **Interactive Visualization**: Uses Tableau to present the data, enabling end-users to explore Reddit trends and insights.
- **Orchestration with Docker and Airflow**: Ensures each stage of the pipeline is consistently managed and scheduled, making the process reliable and repeatable.

## Services and Technologies Used

1. **Reddit API**: Acts as the data source, allowing us to fetch data from Reddit based on specific parameters.
2. **Docker**: Provides a containerized environment for running the application, ensuring consistency across different setups.
3. **Apache Airflow**: Orchestrates the ETL pipeline, automating each stage and managing dependencies between tasks.
4. **Amazon S3**: Serves as the staging area for raw Reddit data, ensuring durability and accessibility across the pipeline.
5. **Amazon Redshift**: Data warehouse for storing and querying processed data, optimized for analytics.
6. **dbt (Data Build Tool)**: Transforms data within Redshift, cleaning and aggregating it to make it ready for analysis.
7. **Tableau**: Visualizes the transformed data, providing interactive dashboards for data exploration.

## Workflow

1. **Data Extraction**:
   - Airflow triggers the extraction process by calling the Reddit API to retrieve posts, comments, and relevant metadata.
   - Data is filtered and temporarily processed for efficient storage.

2. **Data Loading into Amazon S3**:
   - Extracted data is loaded into an S3 bucket, acting as a temporary staging area.

3. **Data Loading into Amazon Redshift**:
   - Airflow orchestrates the process of loading raw data from S3 into Redshift, where it’s stored in tables for further transformations.

4. **Data Transformation with dbt**:
   - dbt applies SQL-based transformations to the raw data in Redshift.
   - Transformations include cleaning, filtering, aggregating, and joining datasets to create a structured, analysis-ready format.

5. **Data Visualization with Tableau**:
   - Tableau connects to the transformed data in Redshift to build interactive dashboards.
   - Dashboards display insights like Reddit user engagement, sentiment analysis, trending topics, and more.

## Advantages of This Approach

1. **Scalable Data Storage and Processing**:
   - Using Amazon S3 and Redshift provides high scalability for storing large amounts of data and querying it efficiently.

2. **Automated and Modular Pipeline**:
   - Airflow automates the ETL process, making it easy to add new data sources or modify existing workflows without affecting other parts of the pipeline.

3. **Flexible Data Transformations**:
   - dbt enables standardized, SQL-based transformations, which are easy to modify and maintain for different analytical needs.

4. **Enhanced Data Visualization**:
   - Tableau allows for rich, interactive dashboards, making it easy for end-users to explore and analyze Reddit data without needing to query the database directly.

## Getting Started

### Prerequisites

1. **AWS Account**: Set up an Amazon S3 bucket and an Amazon Redshift cluster. Ensure that Airflow and dbt have the required access permissions for S3 and Redshift.
2. **Reddit API Access**: Obtain API credentials from [Reddit’s developer portal](https://www.reddit.com/prefs/apps) to access Reddit data.
3. **Docker**: Install Docker for containerized deployment of the ETL components.
4. **Apache Airflow**: Configure Airflow to manage the ETL workflows.

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd reddit-etl-pipeline
