# LinkedIn Activity Monitoring Setup

## Current Status
The LinkedIn watcher can monitor your LinkedIn activity (notifications, comments, messages) and save them to your vault, but it requires valid LinkedIn credentials.

## To Monitor LinkedIn Activity:

### Prerequisites
1. LinkedIn account with proper permissions
2. Valid username and password (though LinkedIn may restrict API access)

### Setup Process
1. **Set Environment Variables:**
   ```bash
   # Windows
   set LINKEDIN_USERNAME=fiaz.majeed@uog.edu.pk
   set LINKEDIN_PASSWORD=UOGFocal0222
   ```

2. **Start the LinkedIn Watcher:**
   ```bash
   fte linkedin
   ```

### What Gets Saved to Your Vault
When monitoring is active, the system will save:
- LinkedIn notifications
- Comments on your posts
- New messages
- Connection requests
- Engagement metrics

### File Location
Saved in: `vault/Inbox/` with filenames like:
- `linkedin_notification_[timestamp].md`
- `linkedin_message_[timestamp].md`
- `linkedin_comment_[timestamp].md`

### Content Format
Each saved file includes:
- Timestamp
- Sender/origin
- Content of the notification/message
- Engagement data
- Metadata for processing

## Alternative Approach
Due to LinkedIn's API restrictions, you may need to:
1. Use the content preparation features (working)
2. Manually post content to LinkedIn
3. Monitor engagement manually
4. Use the vault for content organization and scheduling