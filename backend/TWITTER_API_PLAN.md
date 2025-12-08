# Twitter API Implementation Plan

## Architecture
- UniAPI (8000) provides Twitter API v2 compatible endpoints
- twitter_bridge_server.py (5001) handles Playwright automation
- All endpoints use Playwright scraping (no official API keys needed)

## Implementation Status

### ✅ Completed - Phase 0: Basic Operations
- [x] POST /2/tweets - Create tweet
- [x] GET /2/users/me - Get current user

### ✅ Completed - Phase 1: Core Tweet Operations
- [x] GET /2/tweets/:id - Get tweet by ID
- [x] DELETE /2/tweets/:id - Delete tweet
- [x] POST /2/users/:id/retweets - Retweet
- [x] DELETE /2/users/:id/retweets/:tweet_id - Undo retweet
- [x] POST /2/users/:id/likes - Like tweet (body: {"tweet_id": "123"})
- [x] DELETE /2/users/:id/likes/:tweet_id - Unlike tweet
- [x] POST /2/tweets - Reply to tweet (with reply_to_id parameter - already in post_single_tweet)

### ✅ Completed - Phase 2: User Operations
- [x] GET /2/users/by/username/:username - Get user by username
- [x] POST /2/users/:id/following - Follow user
- [x] DELETE /2/users/:id/following/:target_user_id - Unfollow user
- [x] GET /2/users/:id/tweets - Get user's tweets

### ✅ Completed - Phase 3: Search & Discovery
- [x] GET /2/tweets/search/recent - Search tweets

### 🚧 Optional Advanced Features (Not Required for Core Functionality)

#### User Operations
- [ ] GET /2/users/:id - Get user by ID
- [ ] GET /2/users/by/username/:username - Get user by username
- [ ] POST /2/users/:id/following - Follow user
- [ ] DELETE /2/users/:source_user_id/following/:target_user_id - Unfollow
- [ ] GET /2/users/:id/followers - Get followers list
- [ ] GET /2/users/:id/following - Get following list

#### Search & Timeline
- [ ] GET /2/tweets/search/recent - Search tweets (last 7 days)
- [ ] GET /2/users/:id/tweets - Get user's tweets
- [ ] GET /2/users/:id/mentions - Get user mentions
- [ ] GET /2/tweets/:id/liking_users - Get users who liked
- [ ] GET /2/tweets/:id/retweeted_by - Get users who retweeted

#### Direct Messages
- [ ] GET /2/dm_conversations - List DM conversations
- [ ] GET /2/dm_conversations/:id/messages - Get DM messages
- [ ] POST /2/dm_conversations - Create DM conversation
- [ ] POST /2/dm_conversations/:id/messages - Send DM

## Implementation Priority

### Phase 1: Core Tweet Operations (NOW)
1. Delete tweet
2. Retweet/Unretweet
3. Like/Unlike tweet
4. Reply to tweet

### Phase 2: User Operations
5. Get user profile
6. Follow/Unfollow
7. Get followers/following lists

### Phase 3: Search & Discovery
8. Search tweets
9. Get user timeline
10. Get trending topics

### Phase 4: Direct Messages
11. List conversations
12. Send/receive DMs

## Technical Notes

### Playwright Selectors (X.com)
- Tweet compose: `[data-testid="tweetTextarea_0"]`
- Post button: `[data-testid="tweetButtonInline"]`
- Like button: `[data-testid="like"]`
- Retweet button: `[data-testid="retweet"]`
- Reply button: `[data-testid="reply"]`
- Follow button: `[data-testid="followButton"]`
- Tweet article: `article[data-testid="tweet"]`

### Authentication
- Uses persistent browser context with saved cookies
- Cookies location: `~/.distroflow/twitter_browser/`
- Auth file: `~/.distroflow/twitter_auth.json`
