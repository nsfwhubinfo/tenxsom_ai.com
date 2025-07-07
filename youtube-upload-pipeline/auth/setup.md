# 🔐 Google Cloud Setup for YouTube API

## Step-by-Step Setup Guide

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Project name: `tenxsom-youtube-automation`
4. Click "Create"

### 2. Enable YouTube Data API v3

1. In Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click on it and press "Enable"
4. Wait for activation (may take a few minutes)

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External (for personal use)
   - App name: "Tenxsom AI YouTube Automation"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `https://www.googleapis.com/auth/youtube.upload`
   - Test users: Add your email

4. Create OAuth client ID:
   - Application type: "Desktop application"
   - Name: "Tenxsom YouTube Uploader"
   - Click "Create"

5. Download the credentials:
   - Click the download icon next to your OAuth client
   - Save as `client_secrets.json` in the `auth/` directory

### 4. Set Required Scopes

Your application will need these OAuth 2.0 scopes:

```
https://www.googleapis.com/auth/youtube.upload
https://www.googleapis.com/auth/youtube
https://www.googleapis.com/auth/youtube.readonly
https://www.googleapis.com/auth/youtubepartner
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=tenxsom-youtube-automation
YOUTUBE_API_KEY=your_api_key_here

# OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret

# YouTube Channel Configuration  
YOUTUBE_CHANNEL_ID=your_channel_id_here
YOUTUBE_CHANNEL_NAME=your_channel_name

# Upload Settings
DEFAULT_UPLOAD_CATEGORY=22  # People & Blogs
DEFAULT_PRIVACY_STATUS=private  # private, public, unlisted
```

### 6. API Quotas and Limits

**YouTube Data API v3 Quotas (Free Tier):**
- **10,000 units per day**
- Video upload costs: **1,600 units**
- Thumbnail upload costs: **50 units**
- Maximum uploads per day: **~6 videos**

**Unit Costs:**
- Upload video: 1,600 units
- Set thumbnail: 50 units  
- Update video: 50 units
- List videos: 1 unit per video

### 7. Production Considerations

**For Higher Volume (>6 videos/day):**
1. Request quota increase from Google
2. Consider multiple Google Cloud projects
3. Implement intelligent retry logic
4. Monitor quota usage in Google Cloud Console

**Security Best Practices:**
- Store `client_secrets.json` securely (not in git)
- Use environment variables for sensitive data
- Implement token refresh logic
- Monitor API usage and costs

### 8. Testing the Setup

Once configured, test with:

```bash
python auth/test_auth.py
```

This will:
1. Authenticate with Google OAuth 2.0
2. Verify YouTube API access
3. Display your channel information
4. Check quota usage

### 9. Troubleshooting

**Common Issues:**

- **"Access blocked"**: App not verified by Google
  - Solution: Add your email as test user in OAuth consent screen

- **"Quota exceeded"**: Daily API limit reached
  - Solution: Wait until next day or request quota increase

- **"Invalid credentials"**: OAuth setup incorrect
  - Solution: Re-download client_secrets.json

- **"Insufficient permissions"**: Missing scopes
  - Solution: Add required scopes to OAuth consent screen

### 10. Next Steps

After successful setup:
1. Run authentication test
2. Test video upload with sample file
3. Configure thumbnail upload
4. Integrate with existing video pipeline
5. Set up monitoring and analytics

---

**Security Note**: Never commit `client_secrets.json` or OAuth tokens to version control. These files contain sensitive authentication data.