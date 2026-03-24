"""
Facebook and Instagram API Integration for Gold Tier
Supports posting, monitoring, and analytics via Facebook Graph API
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..audit.audit_logger import get_audit_logger, AuditEventType
from ..resilience.error_recovery import with_retry, get_circuit_breaker


class FacebookAPI:
    """Facebook Graph API client for Facebook and Instagram."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        page_id: Optional[str] = None,
        instagram_account_id: Optional[str] = None
    ):
        """Initialize Facebook API client.

        Args:
            access_token: Facebook access token
            page_id: Facebook page ID
            instagram_account_id: Instagram business account ID
        """
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")
        self.instagram_account_id = instagram_account_id or os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.base_url = "https://graph.facebook.com/v19.0"

        self.audit_logger = get_audit_logger()
        self.circuit_breaker = get_circuit_breaker("facebook_api")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint}"
        params = kwargs.get('params', {})
        params['access_token'] = self.access_token

        response = requests.request(method, url, params=params, **{k: v for k, v in kwargs.items() if k != 'params'})

        self.audit_logger.log_api_call(
            service="facebook",
            endpoint=endpoint,
            method=method,
            status_code=response.status_code,
            actor="facebook_api"
        )

        response.raise_for_status()
        return response.json()

    @with_retry(max_attempts=3, initial_delay=2.0)
    def post_to_facebook(self, message: str, link: Optional[str] = None,
                         image_url: Optional[str] = None) -> Dict[str, Any]:
        """Post to Facebook page.

        Args:
            message: Post message
            link: Optional link to share
            image_url: Optional image URL

        Returns:
            Post data including ID
        """
        if not self.page_id:
            raise Exception("Facebook page ID not configured")

        try:
            data = {'message': message}
            if link:
                data['link'] = link
            if image_url:
                data['url'] = image_url

            result = self.circuit_breaker.call(
                self._make_request,
                'POST',
                f"{self.page_id}/feed",
                params=data
            )

            post_id = result.get('id')
            post_url = f"https://facebook.com/{post_id}"

            self.audit_logger.log_social_post(
                platform="facebook",
                post_id=post_id,
                actor="facebook_api",
                content_preview=message[:100],
                url=post_url
            )

            return {
                "id": post_id,
                "url": post_url,
                "message": message,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to post to Facebook: {e}",
                actor="facebook_api",
                resource="post_to_facebook"
            )
            raise

    @with_retry(max_attempts=3, initial_delay=2.0)
    def post_to_instagram(self, image_url: str, caption: str) -> Dict[str, Any]:
        """Post to Instagram.

        Args:
            image_url: URL of image to post
            caption: Post caption

        Returns:
            Post data including ID
        """
        if not self.instagram_account_id:
            raise Exception("Instagram account ID not configured")

        try:
            # Step 1: Create media container
            container_data = {
                'image_url': image_url,
                'caption': caption
            }

            container_result = self.circuit_breaker.call(
                self._make_request,
                'POST',
                f"{self.instagram_account_id}/media",
                params=container_data
            )

            container_id = container_result.get('id')

            # Step 2: Publish media container
            publish_result = self.circuit_breaker.call(
                self._make_request,
                'POST',
                f"{self.instagram_account_id}/media_publish",
                params={'creation_id': container_id}
            )

            post_id = publish_result.get('id')

            self.audit_logger.log_social_post(
                platform="instagram",
                post_id=post_id,
                actor="facebook_api",
                content_preview=caption[:100],
                image_url=image_url
            )

            return {
                "id": post_id,
                "caption": caption,
                "image_url": image_url,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to post to Instagram: {e}",
                actor="facebook_api",
                resource="post_to_instagram"
            )
            raise

    @with_retry(max_attempts=3, initial_delay=2.0)
    def get_facebook_insights(self, metric: str = "page_impressions",
                              period: str = "day", days: int = 7) -> Dict[str, Any]:
        """Get Facebook page insights.

        Args:
            metric: Metric to retrieve
            period: Time period (day, week, days_28)
            days: Number of days to look back

        Returns:
            Insights data
        """
        if not self.page_id:
            raise Exception("Facebook page ID not configured")

        try:
            since = datetime.now() - timedelta(days=days)
            until = datetime.now()

            result = self.circuit_breaker.call(
                self._make_request,
                'GET',
                f"{self.page_id}/insights",
                params={
                    'metric': metric,
                    'period': period,
                    'since': int(since.timestamp()),
                    'until': int(until.timestamp())
                }
            )

            return result

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to get Facebook insights: {e}",
                actor="facebook_api",
                resource="get_facebook_insights"
            )
            raise

    @with_retry(max_attempts=3, initial_delay=2.0)
    def get_instagram_insights(self, metric: str = "impressions",
                               period: str = "day", days: int = 7) -> Dict[str, Any]:
        """Get Instagram insights.

        Args:
            metric: Metric to retrieve (impressions, reach, profile_views)
            period: Time period
            days: Number of days to look back

        Returns:
            Insights data
        """
        if not self.instagram_account_id:
            raise Exception("Instagram account ID not configured")

        try:
            since = datetime.now() - timedelta(days=days)
            until = datetime.now()

            result = self.circuit_breaker.call(
                self._make_request,
                'GET',
                f"{self.instagram_account_id}/insights",
                params={
                    'metric': metric,
                    'period': period,
                    'since': int(since.timestamp()),
                    'until': int(until.timestamp())
                }
            )

            return result

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to get Instagram insights: {e}",
                actor="facebook_api",
                resource="get_instagram_insights"
            )
            raise

    def generate_summary(self, platform: str, days: int = 7) -> Dict[str, Any]:
        """Generate engagement summary for a platform.

        Args:
            platform: Platform name (facebook or instagram)
            days: Number of days to analyze

        Returns:
            Summary statistics
        """
        try:
            if platform == "facebook":
                impressions = self.get_facebook_insights("page_impressions", days=days)
                engagement = self.get_facebook_insights("page_engaged_users", days=days)

                return {
                    "platform": "facebook",
                    "period_days": days,
                    "impressions": impressions,
                    "engagement": engagement,
                    "generated_at": datetime.now().isoformat()
                }

            elif platform == "instagram":
                impressions = self.get_instagram_insights("impressions", days=days)
                reach = self.get_instagram_insights("reach", days=days)

                return {
                    "platform": "instagram",
                    "period_days": days,
                    "impressions": impressions,
                    "reach": reach,
                    "generated_at": datetime.now().isoformat()
                }

            else:
                raise ValueError(f"Unknown platform: {platform}")

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to generate summary for {platform}: {e}",
                actor="facebook_api",
                resource="generate_summary"
            )
            raise


class SocialMediaContentGenerator:
    """Generate content for Facebook and Instagram."""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize content generator.

        Args:
            vault_path: Path to vault for content sources
        """
        self.vault_path = vault_path or Path(__file__).parent.parent.parent.parent / "vault"

    def generate_facebook_post(self, topic: str, include_link: bool = False) -> Dict[str, str]:
        """Generate a Facebook post.

        Args:
            topic: Topic for the post
            include_link: Whether to include a link

        Returns:
            Post data with message and optional link
        """
        templates = [
            f"Exciting news about {topic}! We're thrilled to share our latest progress. 🎉",
            f"Here's what we've been working on with {topic}. Check it out! 💼",
            f"New developments in {topic} - we're making great strides! 🚀",
            f"Quick update on {topic}: Things are moving forward! ⚡"
        ]

        import random
        message = random.choice(templates)

        result = {"message": message}
        if include_link:
            result["link"] = "https://example.com"  # Placeholder

        return result

    def generate_instagram_caption(self, topic: str, hashtags: int = 5) -> str:
        """Generate an Instagram caption.

        Args:
            topic: Topic for the caption
            hashtags: Number of hashtags to include

        Returns:
            Caption text with hashtags
        """
        caption = f"Making progress on {topic}! 📸✨"

        # Add hashtags
        topic_words = topic.lower().replace(' ', '').split()
        base_hashtags = ['business', 'growth', 'innovation', 'success', 'entrepreneur']
        all_hashtags = topic_words + base_hashtags

        import random
        selected_hashtags = random.sample(all_hashtags, min(hashtags, len(all_hashtags)))
        hashtag_string = ' '.join(f"#{tag}" for tag in selected_hashtags)

        return f"{caption}\n\n{hashtag_string}"
