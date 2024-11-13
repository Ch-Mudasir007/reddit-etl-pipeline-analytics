import praw
import json
import boto3
from datetime import datetime

# Reddit API Credentials
client_id = "xyz"
client_secret = "xyz"
user_agent = "xyz"

# AWS S3 Client Setup
s3_client = boto3.client('s3')
bucket_name = 'reddit-data-for-redshiftdb'  # Replace with your actual bucket name

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

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
                "created": datetime.fromtimestamp(submission.created_utc).isoformat(),
                "subreddit": submission.subreddit.display_name,
                "url": submission.url,
                "selftext": submission.selftext
            }
            results.append(post_data)
    return results

def save_to_s3(data):
    """Save the data to S3 in JSON format."""
    json_data = json.dumps(data)
    s3_key = f"reddit_data/all_posts_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=json_data)
    print(f"Data saved to S3 bucket '{bucket_name}' with key '{s3_key}'")

def lambda_handler(event, context):
    """AWS Lambda handler function to fetch and store all Reddit posts."""
    # Fetch trending posts from multiple subreddits
    posts = fetch_trending_posts(subreddit_list=['all'])
    
    # Save results to S3
    save_to_s3(posts)
    
    # Return a success message
    return {"status": "success", "message": "All trending data saved to S3"}
