import praw
import json
import boto3
import os
from datetime import datetime
import time
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Reddit API Credentials
client_id = "Ev2FWFGqYzmxApMsdRLayg"
client_secret = "1xqfBWZaxhyRN8WeeGGeecBChmSkaA"
user_agent = "MyRedditApp/0.1 by u/NervousLog84"

# AWS Clients Setup
s3_client = boto3.client('s3')
redshift_data = boto3.client('redshift-data', region_name='us-east-1')

# S3 and Redshift Details
bucket_name = 'reddit-data-for-redshiftdb'  # Your S3 bucket name
s3_prefix = 'reddit_data/'  # The folder where the files will be stored
CLUSTER_ID = 'reddit-data-cluster'  # Your Redshift cluster ID
DATABASE = 'reddit_datadb'
ROLE_ARN = 'arn:aws:iam::767397986153:role/service-role/AmazonRedshift-CommandsAccessRole-'  # Updated Redshift IAM Role ARN

# Initialize Reddit instance
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

def fetch_trending_posts(subreddit_list=None, limit=100):
    """Fetch trending Reddit posts from specified subreddits or 'all'."""
    subreddit_list = subreddit_list or ['all']  # Default to all if no specific list is provided
    results = []

    for subreddit_name in subreddit_list:
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.hot(limit=limit):  # Fetch top 'hot' posts
            post_data = {
                "title": submission.title,
                "score": submission.score,
                "num_comments": submission.num_comments,
                # Convert to Redshift-compatible timestamp format
                "created": datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "subreddit": submission.subreddit.display_name,
                "url": submission.url,
                "selftext": submission.selftext
            }
            results.append(post_data)
    return results

def save_to_s3_line_delimited(data):
    """Save the data to S3 in line-delimited JSON format."""
    # Prepare line-delimited JSON string
    line_delimited_json = "\n".join(json.dumps(record) for record in data)
    
    # Generate a unique S3 key for the file, based on the current timestamp
    s3_key = f"{s3_prefix}all_posts_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    
    # Save to S3 bucket
    s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=line_delimited_json)
    logger.info(f"Data saved to S3 bucket '{bucket_name}' with key '{s3_key}'")
    
    return s3_key  # Return the S3 key

def load_to_redshift_from_s3(s3_key):
    """Load the data from the given S3 key into Redshift."""
    s3_path = f's3://{bucket_name}/{s3_key}'
    logger.info(f"Processing file from S3: {s3_path}")

    # Redshift COPY command
    sql = f"""
    COPY reddit_schema.reddit_data
    FROM '{s3_path}'
    IAM_ROLE '{ROLE_ARN}'
    FORMAT AS JSON 'auto';
    """

    # Execute Redshift COPY command
    response = redshift_data.execute_statement(
        ClusterIdentifier=CLUSTER_ID,  # Updated for correct usage with ClusterIdentifier
        Database=DATABASE,
        Sql=sql
    )

    # Wait for the query to complete
    query_id = response['Id']
    logger.info(f"COPY command submitted. Query ID: {query_id}")

    while True:
        status = redshift_data.describe_statement(Id=query_id)['Status']
        logger.info(f"COPY command status: {status}")
        if status in ['FINISHED', 'FAILED']:
            break
        time.sleep(1)

    if status == 'FAILED':
        error_msg = redshift_data.describe_statement(Id=query_id)['Error']
        logger.error(f"Redshift COPY command failed: {error_msg}")
        return {"statusCode": 500, "body": f"Redshift COPY command failed: {error_msg}"}

    # Return success response
    logger.info(f"Data successfully copied from {s3_path} to Redshift.")
    return {"statusCode": 200, "body": f"Data successfully copied from {s3_path} to Redshift."}

def lambda_handler(event, context):
    """AWS Lambda handler to fetch data from Reddit and load it into Redshift."""
    # Step 1: Fetch the list of files in the S3 bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)
    files = response.get('Contents', [])
    
    # Get the latest file by timestamp in the filename
    latest_file = max(files, key=lambda x: x['LastModified'])

    # Extract the timestamp from the filename (assuming format 'all_posts_YYYY-MM-DD_HH-MM-SS.json')
    latest_file_name = latest_file['Key']
    try:
        # The timestamp part of the filename is after 'all_posts_' and before '.json'
        timestamp_str = latest_file_name.split('_')[-2] + '_' + latest_file_name.split('_')[-1].replace('.json', '')
        # Parse the timestamp from the filename
        latest_file_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S')
        logger.info(f"Latest file timestamp: {latest_file_timestamp}")
    except Exception as e:
        logger.error(f"Error parsing timestamp from file: {e}")
        raise

    # Step 2: Fetch trending posts from Reddit
    posts = fetch_trending_posts(subreddit_list=['all'])

    # Step 3: Save the data to S3 and get the exact S3 key
    latest_s3_key = save_to_s3_line_delimited(posts)

    # Step 4: Load the new data from S3 to Redshift
    load_result = load_to_redshift_from_s3(latest_s3_key)
    
    return load_result
