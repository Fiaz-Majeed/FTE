# LinkedIn Posting Skill

This skill helps automate LinkedIn posts about business to generate sales.

## Functions:

### create_linkedin_post
Create and post content to LinkedIn.
- `content`: Content to post
- `username`: LinkedIn username (optional, uses env var if not provided)
- `password`: LinkedIn password (optional, uses env var if not provided)
- `visibility`: Post visibility ('PUBLIC' or 'CONNECTIONS_ONLY', default: 'PUBLIC')
- `hashtags`: List of hashtags to include (optional)

### schedule_linkedin_post
Schedule a LinkedIn post for a specific time.
- `content`: Content to post
- `scheduled_time`: When to post (ISO format datetime string)
- `username`: LinkedIn username (optional)
- `password`: LinkedIn password (optional)
- `visibility`: Post visibility (default: 'PUBLIC')
- `hashtags`: List of hashtags to include (optional)

### create_post_from_vault_content
Create LinkedIn post content from vault notes.
- `vault_path`: Path to vault directory (optional)
- `content_type`: Type of content to generate (default: 'business_update')
- `hashtags`: List of hashtags to suggest (optional)

### get_suggested_posting_times
Get suggested optimal times for LinkedIn posting.
- `count`: Number of suggested times to return (default: 5)

### get_linkedin_profile_info
Get LinkedIn profile information.
- `username`: LinkedIn username (optional)
- `password`: LinkedIn password (optional)

### get_linkedin_network_info
Get LinkedIn network information.
- `username`: LinkedIn username (optional)
- `password`: LinkedIn password (optional)

## Usage Examples:

```
/inbox-processor create_post_from_vault_content
/task-manager create_linkedin_post "Excited to share our latest product update! #Innovation #Tech"
/dashboard-updater schedule_linkedin_post "Check out our new services!" "2024-01-15T10:00:00"
/note-creator get_suggested_posting_times 3
```