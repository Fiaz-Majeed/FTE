"""LinkedIn Browser Automation - Post to LinkedIn using Selenium/Playwright.

This module provides browser-based automation for LinkedIn operations since
LinkedIn has deprecated direct username/password API authentication.

Note: This is a fallback method. For production use, consider applying for
the official LinkedIn Marketing Developer Program API.
"""

import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Try Selenium first, then Playwright
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class LinkedInBrowserAutomation:
    """LinkedIn automation using browser automation."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        headless: bool = True,
    ):
        """Initialize LinkedIn browser automation.

        Args:
            username: LinkedIn username/email
            password: LinkedIn password
            headless: Whether to run browser in headless mode
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "selenium is required for LinkedIn browser automation. "
                "Install with: pip install selenium"
            )

        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self._authenticated = False

    def _load_credentials_from_env(self) -> bool:
        """Load credentials from environment variables.

        Returns:
            True if credentials loaded successfully
        """
        import os

        self.username = self.username or os.getenv("LINKEDIN_USERNAME")
        self.password = self.password or os.getenv("LINKEDIN_PASSWORD")

        return bool(self.username and self.password)

    def _initialize_driver(self) -> None:
        """Initialize the browser driver."""
        options = Options()

        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        # Add user agent to avoid detection
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        # Disable some anti-bot detection features
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)

        # Hide webdriver property
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def authenticate(self) -> bool:
        """Authenticate with LinkedIn using browser automation.

        Returns:
            True if authentication successful
        """
        if not self._load_credentials_from_env():
            raise ValueError(
                "LinkedIn credentials not provided. Set username/password "
                "or environment variables LINKEDIN_USERNAME/LINKEDIN_PASSWORD"
            )

        try:
            self._initialize_driver()

            # Navigate to LinkedIn login page
            self.driver.get("https://www.linkedin.com/login")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )

            # Enter credentials
            username_field = self.driver.find_element(By.ID, "username")
            username_field.send_keys(self.username)

            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)

            # Submit login form
            password_field.send_keys(Keys.RETURN)

            # Wait for login to complete (check for either feed or security challenge)
            time.sleep(3)

            # Check if we're on the feed page (successful login)
            current_url = self.driver.current_url

            if "feed" in current_url or "linkedin.com/feed" in current_url:
                self._authenticated = True
                print("LinkedIn authentication successful (via browser)")
                return True
            elif "checkpoint" in current_url or "security" in current_url:
                print(
                    "LinkedIn security checkpoint detected. "
                    "Please complete the verification in the browser."
                )
                if self.headless:
                    print(
                        "Note: Running in headless mode. "
                        "Please set headless=False and try again."
                    )
                    self._authenticated = False
                    return False
                else:
                    # Wait for manual verification (max 2 minutes)
                    input("Press Enter after completing verification in the browser...")
                    if "feed" in self.driver.current_url:
                        self._authenticated = True
                        return True
                    return False
            else:
                print(f"Login may have failed. Current URL: {current_url}")
                self._authenticated = False
                return False

        except Exception as e:
            print(f"LinkedIn browser authentication failed: {e}")
            self._authenticated = False
            return False

    def post_update(
        self,
        text: str,
        visibility: str = "PUBLIC",
        hashtags: List[str] | None = None,
        images: List[str] | None = None,
    ) -> Dict[str, Any]:
        """Post an update to LinkedIn using browser automation.

        Args:
            text: Text content of the post
            visibility: Post visibility (PUBLIC or CONNECTIONS_ONLY)
            hashtags: List of hashtags to include
            images: List of image file paths to attach

        Returns:
            Dictionary with post result
        """
        if not self._authenticated:
            if not self.authenticate():
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "timestamp": datetime.now().isoformat(),
                }

        try:
            # Add hashtags to text if provided
            if hashtags:
                text += " " + " ".join([f"#{tag}" for tag in hashtags])

            # Navigate to the LinkedIn feed
            self.driver.get("https://www.linkedin.com/feed/")

            # Wait for the post box to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-test-key="create-share"]')
                )
            )

            # Click on the "Start a post" box
            post_button = self.driver.find_element(By.CSS_SELECTOR, '[data-test-key="create-share"]')
            post_button.click()

            # Wait for the text area to appear
            time.sleep(2)
            text_area = self.driver.find_element(
                By.CSS_SELECTOR, '.ql-editor[contenteditable="true"]'
            )

            # Type the post content
            text_area.send_keys(text)
            time.sleep(1)

            # Set visibility if needed
            if visibility == "CONNECTIONS_ONLY":
                # Click the visibility selector and choose "Connections only"
                try:
                    visibility_button = self.driver.find_element(
                        By.CSS_SELECTOR, '[aria-label="Anyone"]'
                    )
                    visibility_button.click()
                    time.sleep(0.5)

                    connections_option = self.driver.find_element(
                        By.XPATH, "//span[contains(text(), 'Connections only')]"
                    )
                    connections_option.click()
                    time.sleep(0.5)
                except Exception:
                    print("Warning: Could not set visibility, using default")

            # Click the post button
            post_submit_button = self.driver.find_element(
                By.CSS_SELECTOR, '[data-test-key="share-post"]'
            )
            post_submit_button.click()

            # Wait for the post to be created
            time.sleep(3)

            # Check if post was successful (look for success indicator or navigate back to feed)
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(2)

            post_result = {
                "success": True,
                "method": "browser_automation",
                "text": text[:100] + "..." if len(text) > 100 else text,
                "visibility": visibility,
                "timestamp": datetime.now().isoformat(),
                "hashtags": hashtags or [],
            }

            print("LinkedIn post created successfully (via browser)")
            return post_result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "browser_automation",
                "timestamp": datetime.now().isoformat(),
            }

    def close(self) -> None:
        """Close the browser driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self._authenticated = False

    def __enter__(self):
        """Context manager entry."""
        self.authenticate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def post_to_linkedin(
    text: str,
    username: str | None = None,
    password: str | None = None,
    headless: bool = True,
) -> Dict[str, Any]:
    """Convenience function to post to LinkedIn using browser automation.

    Args:
        text: Text content of the post
        username: LinkedIn username/email
        password: LinkedIn password
        headless: Whether to run browser in headless mode

    Returns:
        Dictionary with post result
    """
    with LinkedInBrowserAutomation(
        username=username, password=password, headless=headless
    ) as automation:
        return automation.post_update(text)


# Fallback implementation for when browser automation is not available
class LinkedInAPIFallback:
    """Fallback LinkedIn API implementation using browser automation when available."""

    def __init__(self, username: str | None = None, password: str | None = None):
        """Initialize fallback implementation.

        Args:
            username: LinkedIn username/email
            password: LinkedIn password
        """
        self.automation = None
        if SELENIUM_AVAILABLE:
            try:
                self.automation = LinkedInBrowserAutomation(
                    username=username, password=password, headless=False
                )
            except Exception as e:
                print(f"Could not initialize browser automation: {e}")

    def authenticate(self) -> bool:
        """Authenticate with LinkedIn."""
        if self.automation:
            return self.automation.authenticate()
        return False

    def post_update(
        self,
        text: str,
        visibility: str = "PUBLIC",
        hashtags: List[str] | None = None,
        images: List[str] | None = None,
    ) -> Dict[str, Any]:
        """Post an update to LinkedIn."""
        if self.automation and self.automation._authenticated:
            return self.automation.post_update(text, visibility, hashtags, images)
        return {
            "success": False,
            "error": "Browser automation not available or not authenticated",
        }
