# How to Get Slack User IDs

When you want to mention specific users in Slack notifications, you need their **User IDs** (not their display names, which can change).

Slack User IDs are permanent identifiers that look like: `U01234ABCDE`

## 🔍 Method 1: Copy Member ID (Easiest)

1. **Open Slack** and navigate to your workspace
2. **Click on the user's profile** (click their avatar or name)
3. **Click "More"** (three dots menu)
4. **Select "Copy member ID"**
5. The User ID is now in your clipboard (format: `U01234ABCDE`)

## 🔍 Method 2: View Profile URL

1. **Right-click** on the user's name anywhere in Slack
2. **Select "View profile"**
3. Look at the **browser URL**, it will show:
   ```
   https://yourworkspace.slack.com/team/U01234ABCDE
   ```
4. The User ID is the part after `/team/` (e.g., `U01234ABCDE`)

## 🔍 Method 3: Using Slack API (Advanced)

If you need to get multiple user IDs:

1. Go to https://api.slack.com/methods/users.list/test
2. Select your workspace and token
3. Click "Test Method"
4. Find users in the JSON response with their IDs

## 📝 Adding User IDs to .env File

Once you have the User IDs, add them to your `.env` file:

```env
# Single user
SLACK_MENTION_USERS=U01234ABCDE

# Multiple users (comma-separated, no spaces needed but allowed)
SLACK_MENTION_USERS=U01234ABCDE,U56789FGHIJ

# Multiple users (with spaces for readability)
SLACK_MENTION_USERS=U01234ABCDE, U56789FGHIJ, U99999ZZZZZ
```

## 💬 How Mentions Appear in Slack

When the notification is sent, the message will end with:

```
Please cast your vote here asap: [link]
Thank you!

cc <@U01234ABCDE> <@U56789FGHIJ>
```

In the Slack channel, this will appear as:

```
Please cast your vote here asap: [link]
Thank you!

cc @Pedro @Andrew Clews
```

The mentioned users will receive a notification.

## 🎯 Example Configuration

If Pedro's User ID is `U01ABC123` and Andrew's is `U02DEF456`:

```env
SLACK_MENTION_USERS=U01ABC123,U02DEF456
```

## ⚠️ Important Notes

- User IDs are **permanent** - they don't change even if the user changes their display name
- User IDs are **workspace-specific** - they're different in each Slack workspace
- User IDs are **not secret** - they're safe to store in your `.env` file
- Leave `SLACK_MENTION_USERS` empty or remove it if you don't want to mention anyone

## 🧪 Testing

After adding User IDs to your `.env` file, run the script:

```bash
python monitor_council_votes.py
```

If there are alerts, check your Slack channel to verify the mentions appear correctly.

---

**Tip:** You can always test by mentioning yourself first to make sure it works!

