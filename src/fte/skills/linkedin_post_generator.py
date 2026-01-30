"""
LinkedIn Post Generator - Generates business-focused content from vault data
and optimizes for engagement and sales leads.
"""
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..vault_manager import VaultManager


class LinkedInPostGenerator:
    """Generates business-focused LinkedIn posts from vault content."""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize the post generator.

        Args:
            vault_path: Path to the vault directory containing content
        """
        self.vault_manager = VaultManager(vault_path)
        self.business_templates = self._load_business_templates()
        self.engagement_strategies = self._load_engagement_strategies()

    def _load_business_templates(self) -> List[Dict[str, str]]:
        """Load business-focused post templates."""
        return [
            {
                "type": "success_story",
                "template": "🌟 Success Story: {accomplishment}\n\nWe recently helped {client} achieve {result} by {method}. \n\nKey takeaways:\n✅ {takeaway1}\n✅ {takeaway2}\n✅ {takeaway3}\n\n{call_to_action}",
                "tags": ["case study", "success", "results"]
            },
            {
                "type": "industry_insight",
                "template": "📊 Industry Insight: {trend}\n\n{insight_explanation}\n\nThis shift means {implication} for businesses like {target_audience}.\n\nWhat's your experience with {related_topic}? Share your thoughts below! 👇\n\n{call_to_action}",
                "tags": ["insight", "trend", "analysis"]
            },
            {
                "type": "tip_tuesday",
                "template": "💡 Tip Tuesday: {tip_topic}\n\n{tip_explanation}\n\nTry this approach:\n1. {step1}\n2. {step2}\n3. {step3}\n\nHow do you handle {tip_topic} in your business? Let's discuss! 💬\n\n{call_to_action}",
                "tags": ["tips", "advice", "tutorial"]
            },
            {
                "type": "thought_leadership",
                "template": "🤔 Thought Leadership: {topic}\n\n{current_state}\n\nI believe the future belongs to companies that {prediction}. Here's why:\n\n{i_reason1}\n{i_reason2}\n{i_reason3}\n\nWhat's your perspective? I'd love to hear your thoughts! 🤝\n\n{call_to_action}",
                "tags": ["leadership", "future", "prediction"]
            },
            {
                "type": "behind_scenes",
                "template": "🔍 Behind the Scenes: {activity}\n\nToday we're working on {project_details}.\n\n{behind_scenes_detail}\n\nIt's moments like these that remind us why we do what we do. 🚀\n\n{call_to_action}",
                "tags": ["behind scenes", "culture", "process"]
            }
        ]

    def _load_engagement_strategies(self) -> List[str]:
        """Load engagement optimization strategies."""
        return [
            "Ask a question at the end to encourage comments",
            "Include a relevant statistic to add credibility",
            "Use emojis strategically to break up text",
            "Keep paragraphs short for mobile readability",
            "End with a clear call-to-action",
            "Use the 'hook, story, takeaway' format",
            "Include relevant hashtags (#Business #Leadership #Growth)",
            "Tag relevant people or companies when appropriate",
            "Share personal experiences to build connection",
            "Provide actionable insights that readers can implement"
        ]

    def analyze_vault_content(self) -> Dict[str, Any]:
        """Analyze vault content for business-relevant topics."""
        vault_content = self.vault_manager.get_recent_content(days=30)

        analysis = {
            "recent_topics": [],
            "common_themes": [],
            "potential_stories": [],
            "trending_subjects": [],
            "engagement_opportunities": []
        }

        # Extract business-relevant content
        for content_item in vault_content:
            text = content_item.get('content', '')
            title = content_item.get('title', '')

            # Look for business themes
            business_indicators = [
                'project', 'client', 'result', 'success', 'challenge', 'solution',
                'strategy', 'growth', 'opportunity', 'innovation', 'achievement'
            ]

            indicators_found = [indicator for indicator in business_indicators
                              if indicator.lower() in text.lower() or indicator.lower() in title.lower()]

            if indicators_found:
                analysis["potential_stories"].append({
                    "title": title,
                    "summary": text[:200] + "..." if len(text) > 200 else text,
                    "indicators": indicators_found,
                    "relevance_score": len(indicators_found)
                })

        return analysis

    def generate_post_from_template(self, template_type: str, **kwargs) -> Dict[str, Any]:
        """Generate a LinkedIn post using a specific template.

        Args:
            template_type: Type of template to use
            **kwargs: Template-specific parameters

        Returns:
            Dictionary containing post content and metadata
        """
        # Find the template
        template = next((t for t in self.business_templates if t["type"] == template_type), None)
        if not template:
            raise ValueError(f"Template '{template_type}' not found")

        # Fill in the template
        try:
            post_content = template["template"].format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for template '{template_type}': {e}")

        # Optimize for engagement
        optimized_post = self._optimize_for_engagement(post_content)

        return {
            "content": optimized_post,
            "template_used": template_type,
            "hashtags": self._generate_relevant_hashtags(optimized_post),
            "engagement_strategy": random.choice(self.engagement_strategies),
            "timestamp": datetime.now().isoformat(),
            "scheduled_time": kwargs.get("scheduled_time"),
            "target_audience": kwargs.get("target_audience", "business professionals")
        }

    def generate_business_post(self, post_type: str = "auto", vault_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a business-focused LinkedIn post automatically.

        Args:
            post_type: Type of post to generate ('success_story', 'insight', 'tip', etc.)
            vault_analysis: Pre-analyzed vault content (optional)

        Returns:
            Dictionary containing post content and metadata
        """
        if not vault_analysis:
            vault_analysis = self.analyze_vault_content()

        if post_type == "auto":
            # Automatically choose the best post type based on available content
            if vault_analysis["potential_stories"]:
                # Use the highest relevance story
                best_story = max(vault_analysis["potential_stories"], key=lambda x: x["relevance_score"])

                if "success" in best_story["indicators"] or "result" in best_story["indicators"]:
                    post_type = "success_story"
                elif "insight" in best_story["indicators"] or "trend" in best_story["indicators"]:
                    post_type = "industry_insight"
                else:
                    post_type = random.choice(["success_story", "industry_insight", "thought_leadership"])

        # Generate specific content based on post type
        if post_type == "success_story":
            return self._generate_success_story_post(vault_analysis)
        elif post_type == "industry_insight":
            return self._generate_insight_post(vault_analysis)
        elif post_type == "tip_tuesday":
            return self._generate_tip_post()
        elif post_type == "thought_leadership":
            return self._generate_thought_leadership_post()
        elif post_type == "behind_scenes":
            return self._generate_behind_scenes_post(vault_analysis)
        else:
            # Default to success story if type is unknown
            return self._generate_success_story_post(vault_analysis)

    def _generate_success_story_post(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a success story post."""
        if analysis["potential_stories"]:
            story = analysis["potential_stories"][0]  # Use the best story
            content = {
                "accomplishment": story["summary"],
                "client": "a valued client",
                "result": "significant improvements",
                "method": "our proven approach",
                "takeaway1": "Clear communication is key",
                "takeaway2": "Strategic planning drives results",
                "takeaway3": "Continuous improvement creates lasting value",
                "call_to_action": "Connect with me to learn more about how we can help your business grow! 🚀"
            }
        else:
            # Fallback content
            content = {
                "accomplishment": "Recently completed an exciting project that delivered exceptional results",
                "client": "a forward-thinking company",
                "result": "exceeded expectations by 150%",
                "method": "innovative problem-solving approach",
                "takeaway1": "Understanding client needs is fundamental",
                "takeaway2": "Collaboration amplifies success",
                "takeaway3": "Quality execution delivers lasting value",
                "call_to_action": "What challenges is your business facing? I'd love to discuss potential solutions! 💬"
            }

        return self.generate_post_from_template("success_story", **content)

    def _generate_insight_post(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an industry insight post."""
        trends = [
            "digital transformation acceleration",
            "remote work evolution",
            "AI integration in business processes",
            "sustainability becoming mainstream",
            "customer experience taking priority"
        ]

        insights = [
            "The companies adapting fastest to change are the ones investing in both technology and people.",
            "Success in today's market requires balancing innovation with operational excellence.",
            "The most resilient businesses are those that prioritize agility and adaptability."
        ]

        content = {
            "trend": random.choice(trends),
            "insight_explanation": random.choice(insights),
            "implication": "organizations must evolve their strategies",
            "target_audience": "forward-thinking leaders",
            "related_topic": "digital transformation",
            "call_to_action": "How is your organization adapting to these changes? Share your perspective below! 🤔"
        }

        return self.generate_post_from_template("industry_insight", **content)

    def _generate_tip_post(self) -> Dict[str, Any]:
        """Generate a tip-based post."""
        tips = [
            "effective communication",
            "strategic planning",
            "team collaboration",
            "time management",
            "customer relationship building"
        ]

        content = {
            "tip_topic": random.choice(tips),
            "tip_explanation": "This approach has consistently delivered positive results in my experience.",
            "step1": "Identify your core objective",
            "step2": "Develop a clear action plan",
            "step3": "Execute with attention to detail",
            "call_to_action": "Have you tried this approach? How did it work for you? I'd love to hear your experiences! 💡"
        }

        return self.generate_post_from_template("tip_tuesday", **content)

    def _generate_thought_leadership_post(self) -> Dict[str, Any]:
        """Generate a thought leadership post."""
        topics = [
            "the future of work",
            "business innovation",
            "leadership in challenging times",
            "technology adoption",
            "organizational culture"
        ]

        content = {
            "topic": random.choice(topics),
            "current_state": f"We're at an inflection point where traditional approaches to {random.choice(topics)} are being challenged.",
            "prediction": "embrace flexibility and continuous learning",
            "i_reason1": "Market demands are evolving rapidly",
            "i_reason2": "Technology is enabling new possibilities",
            "i_reason3": "Talent expectations are shifting significantly",
            "call_to_action": "What's your take on this? How is your organization preparing for the future? Let's discuss! 🚀"
        }

        return self.generate_post_from_template("thought_leadership", **content)

    def _generate_behind_scenes_post(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a behind-the-scenes post."""
        activities = [
            "developing a new methodology",
            "working on an innovative solution",
            "collaborating with our team",
            "refining our approach",
            "implementing best practices"
        ]

        content = {
            "activity": random.choice(activities),
            "project_details": "an exciting initiative that aligns with our core values",
            "behind_scenes_detail": "It's the attention to detail and commitment to excellence that makes the difference.",
            "call_to_action": "What's happening behind the scenes in your organization? I'd enjoy hearing about your experiences! 👀"
        }

        return self.generate_post_from_template("behind_scenes", **content)

    def _optimize_for_engagement(self, content: str) -> str:
        """Apply engagement optimization techniques to the content."""
        # Ensure content is not too long
        if len(content) > 1300:  # LinkedIn's sweet spot is under 1300-1500 characters
            content = content[:1250] + "..."

        # Add strategic line breaks for readability
        paragraphs = content.split('\n')
        optimized_paragraphs = []

        for para in paragraphs:
            if len(para) > 80:  # Split long lines
                # Simple word wrap at ~80 characters
                words = para.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= 80:
                        current_line += " " + word
                    else:
                        if current_line:
                            optimized_paragraphs.append(current_line.strip())
                        current_line = word
                if current_line:
                    optimized_paragraphs.append(current_line.strip())
            else:
                optimized_paragraphs.append(para)

        return '\n'.join(optimized_paragraphs)

    def _generate_relevant_hashtags(self, content: str) -> List[str]:
        """Generate relevant hashtags based on content."""
        content_lower = content.lower()

        hashtag_mapping = {
            'business': ['#Business', '#Entrepreneurship', '#Leadership'],
            'success': ['#Success', '#Achievement', '#Results'],
            'innovation': ['#Innovation', '#Tech', '#Future'],
            'growth': ['#Growth', '#Development', '#Progress'],
            'team': ['#Teamwork', '#Collaboration', '#Culture'],
            'leadership': ['#Leadership', '#Management', '#Inspiration'],
            'project': ['#ProjectManagement', '#Strategy', '#Execution'],
            'client': ['#CustomerFocus', '#Service', '#Relationships'],
            'solution': ['#ProblemSolving', '#Innovation', '#Value'],
            'technology': ['#Tech', '#DigitalTransformation', '#Innovation']
        }

        relevant_hashtags = set()
        for keyword, tags in hashtag_mapping.items():
            if keyword in content_lower:
                relevant_hashtags.update(tags)

        # Default hashtags for business posts
        default_hashtags = ['#Business', '#Professional', '#Networking', '#Growth']
        all_hashtags = list(relevant_hashtags) + default_hashtags

        # Limit to 5-10 relevant hashtags
        return all_hashtags[:10]

    def schedule_post(self, post_data: Dict[str, Any], scheduled_time: datetime) -> str:
        """Schedule a post for future publication.

        Args:
            post_data: Post content and metadata
            scheduled_time: When to publish the post

        Returns:
            Scheduled post ID
        """
        # This would integrate with a scheduling system
        # For now, just return a mock ID
        post_data["scheduled_time"] = scheduled_time.isoformat()
        return f"scheduled_post_{hash(str(post_data)) % 10000}"

    def get_optimal_posting_times(self) -> List[datetime]:
        """Get optimal times for LinkedIn posting based on engagement data."""
        # Based on research, optimal LinkedIn posting times
        optimal_times = [
            # Tuesday-Thursday, 8-10 AM and 12-2 PM are typically best
            datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),   # Morning
            datetime.now().replace(hour=12, minute=0, second=0, microsecond=0),  # Lunch
            datetime.now().replace(hour=17, minute=0, second=0, microsecond=0),  # Evening
        ]

        # Adjust for day of week
        import calendar
        current_weekday = datetime.now().weekday()

        # If weekend, suggest Monday times
        if current_weekday in [5, 6]:  # Saturday, Sunday
            optimal_times = [time.replace(day=time.day + (7 - current_weekday)) for time in optimal_times]

        return optimal_times


# Example usage and testing
if __name__ == "__main__":
    generator = LinkedInPostGenerator()

    # Analyze vault content
    analysis = generator.analyze_vault_content()
    print("Vault Analysis:")
    print(f"Potential stories found: {len(analysis['potential_stories'])}")

    # Generate different types of posts
    print("\n--- Success Story Post ---")
    success_post = generator.generate_business_post("success_story")
    print(success_post["content"])
    print(f"Hashtags: {success_post['hashtags']}")

    print("\n--- Industry Insight Post ---")
    insight_post = generator.generate_business_post("industry_insight")
    print(insight_post["content"])

    print("\n--- Auto-generated Post ---")
    auto_post = generator.generate_business_post("auto")
    print(auto_post["content"])
    print(f"Engagement Strategy: {auto_post['engagement_strategy']}")