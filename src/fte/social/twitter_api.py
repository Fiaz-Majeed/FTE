"""
Twitter/X API Integration for Gold Tier
Supports posting tweets, monitoring mentions, and generating summaries
"""
import os
import tweepy
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..audit.audit_logger import get_audit_logger, AuditEventType
from ..resilience.error_recovery import with_retry, get_circuit_breaker


class TwitterAPI:
    """Twitter/X API client with v2 API support."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None
    ):
        """Initialize Twitter API client.

        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Access token
            access_token_secret: Access token secret
            bearer_token: Bearer token for v2 API
        """
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")

        self.audit_logger = get_audit_logger()
        self.circuit_breaker = get_circuit_breaker("twitter_api")

        # Initialize v2 client
        self.client = None
        if self.bearer_token:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )

    @with_retry(max_attempts=3, initial_delay=2.0)
    def post_tweet(self, text: str, media_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post a tweet.

        Args:
            text: Tweet text (max 280 characters)
            media_ids: Optional list of media IDs to attach

        Returns:
            Tweet data including ID and URL
        """
        if not self.client:
            raise Exception("Twitter client not initialized. Check credentials.")

        if len(text) > 280:
            raise ValueError(f"Tweet text too long: {len(text)} characters (max 280)")

        try:
            response = self.circuit_breaker.call(
                self.client.create_tweet,
                text=text,
                media_ids=media_ids
            )

            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"

            self.audit_logger.log_social_post(
                platform="twitter",
                post_id=tweet_id,
                actor="twitter_api",
                content_preview=text[:100],
                url=tweet_url,
                character_count=len(text)
            )

            return {
                "id": tweet_id,
                "url": tweet_url,
                "text": text,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to post tweet: {e}",
                actor="twitter_api",
                resource="post_tweet",
                text_preview=text[:50]
            )
            raise

    @with_retry(max_attempts=3, initial_delay=2.0)
    def get_mentions(self, since_hours: int = 24, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get recent mentions.

        Args:
            since_hours: Hours to look back
            max_results: Maximum number of results

        Returns:
            List of mention data
        """
        if not self.client:
            raise Exception("Twitter client not initialized. Check credentials.")

        try:
            # Get authenticated user ID
            me = self.client.get_me()
            user_id = me.data.id

            # Calculate start time
            start_time = datetime.utcnow() - timedelta(hours=since_hours)

            response = self.circuit_breaker.call(
                self.client.get_users_mentions,
                id=user_id,
                start_time=start_time,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'public_metrics']
            )

            mentions = []
            if response.data:
                for tweet in response.data:
                    mentions.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "author_id": tweet.author_id,
                        "created_at": tweet.created_at.isoformat(),
                        "metrics": tweet.public_metrics
                    })

            self.audit_logger.log_action(
                action="fetch_mentions",
                actor="twitter_api",
                resource="mentions",
                status="success",
                count=len(mentions)
            )

            return mentions

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to fetch mentions: {e}",
                actor="twitter_api",
                resource="get_mentions"
            )
            raise

    @with_retry(max_attempts=3, initial_delay=2.0)
    def get_user_tweets(self, username: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent tweets from a user.

        Args:
            username: Twitter username
            max_results: Maximum number of tweets

        Returns:
            List of tweet data
        """
        if not self.client:
            raise Exception("Twitter client not initialized. Check credentials.")

        try:
            # Get user ID from username
            user = self.client.get_user(username=username)
            user_id = user.data.id

            response = self.circuit_breaker.call(
                self.client.get_users_tweets,
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics']
            )

            tweets = []
            if response.data:
                for tweet in response.data:
                    tweets.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat(),
                        "metrics": tweet.public_metrics
                    })

            return tweets

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to fetch user tweets: {e}",
                actor="twitter_api",
                resource=username
            )
            raise

    def generate_engagement_summary(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate engagement summary from tweets.

        Args:
            tweets: List of tweet data

        Returns:
            Summary statistics
        """
        if not tweets:
            return {
                "total_tweets": 0,
                "total_likes": 0,
                "total_retweets": 0,
                "total_replies": 0,
                "avg_engagement": 0
            }

        total_likes = sum(t.get("metrics", {}).get("like_count", 0) for t in tweets)
        total_retweets = sum(t.get("metrics", {}).get("retweet_count", 0) for t in tweets)
        total_replies = sum(t.get("metrics", {}).get("reply_count", 0) for t in tweets)
        total_engagement = total_likes + total_retweets + total_replies

        return {
            "total_tweets": len(tweets),
            "total_likes": total_likes,
            "total_retweets": total_retweets,
            "total_replies": total_replies,
            "total_engagement": total_engagement,
            "avg_engagement": round(total_engagement / len(tweets), 2) if tweets else 0,
            "top_tweet": max(tweets, key=lambda t: sum(t.get("metrics", {}).values())) if tweets else None
        }

    def search_tweets(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for tweets matching a query.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of matching tweets
        """
        if not self.client:
            raise Exception("Twitter client not initialized. Check credentials.")

        try:
            response = self.circuit_breaker.call(
                self.client.search_recent_tweets,
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'public_metrics']
            )

            tweets = []
            if response.data:
                for tweet in response.data:
                    tweets.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "author_id": tweet.author_id,
                        "created_at": tweet.created_at.isoformat(),
                        "metrics": tweet.public_metrics
                    })

            return tweets

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to search tweets: {e}",
                actor="twitter_api",
                resource="search",
                query=query
            )
            raise


class TwitterContentGenerator:
    """Generate Twitter content from business data."""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize content generator.

        Args:
            vault_path: Path to vault for content sources
        """
        self.vault_path = vault_path or Path(__file__).parent.parent.parent.parent / "vault"

    def generate_tweet_from_note(self, note_path: Path, max_length: int = 280) -> str:
        """Generate a tweet from a vault note.

        Args:
            note_path: Path to note file
            max_length: Maximum tweet length

        Returns:
            Generated tweet text
        """
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract key points (simple implementation)
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # Find first substantial line
        tweet = ""
        for line in lines:
            if len(line) > 20 and not line.startswith('#'):
                tweet = line
                break

        # Truncate if needed
        if len(tweet) > max_length - 3:
            tweet = tweet[:max_length - 3] + "..."

        return tweet

    def generate_business_update(self, topic: str) -> str:
        """Generate a business update tweet.

        Args:
            topic: Topic for the update

        Returns:
            Generated tweet
        """
        templates = [
            f"Excited to share our latest progress on {topic}! 🚀",
            f"New insights on {topic} - check out what we've learned! 💡",
            f"Making strides in {topic}. Here's what's new: 📈",
            f"Quick update on {topic} - we're moving forward! ⚡"
        ]

        import random
        return random.choice(templates)
