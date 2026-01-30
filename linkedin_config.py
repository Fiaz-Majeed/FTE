"""LinkedIn Configuration for Testing"""

import os

# Set environment variables for LinkedIn credentials
# Note: In a real implementation, you would set these securely

# For demonstration purposes only - these would be real credentials in production
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME", "your_linkedin_email@example.com")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "your_linkedin_password")

# For testing, we'll use mock credentials
TEST_LINKEDIN_USERNAME = "test@example.com"
TEST_LINKEDIN_PASSWORD = "testpassword"

def get_linkedin_credentials():
    """Get LinkedIn credentials from environment or return test values."""
    username = os.getenv("LINKEDIN_USERNAME", TEST_LINKEDIN_USERNAME)
    password = os.getenv("LINKEDIN_PASSWORD", TEST_LINKEDIN_PASSWORD)

    return {
        "username": username,
        "password": password
    }

# Define the types of business content we want to auto-post
AUTO_POST_CATEGORIES = [
    "business_update",
    "product_launch",
    "company_news",
    "industry_insights",
    "achievement",
    "milestone"
]

# Define optimal posting times (in UTC)
OPTIMAL_POST_TIMES = [
    "09:00",  # 9 AM UTC (2 AM PST, 5 AM EST)
    "13:00",  # 1 PM UTC (6 AM PST, 9 AM EST)
    "16:00",  # 4 PM UTC (9 AM PST, 12 PM EST)
]

# Hashtags commonly used for business posting
DEFAULT_HASHTAGS = [
    "Business",
    "Entrepreneurship",
    "Innovation",
    "Leadership",
    "Growth",
    "Startup",
    "Technology"
]