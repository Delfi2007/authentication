# 🌐 Google OAuth Setup Guide

## Step 1: Create Google Cloud Project

1. **Go to**: [Google Cloud Console](https://console.cloud.google.com/)
2. **Sign in** with your Google account
3. **Create a new project** or select existing one

## Step 2: Enable Google+ API

1. In the Google Cloud Console, go to **"APIs & Services" > "Library"**
2. Search for **"Google+ API"**
3. Click **"Enable"**

## Step 3: Create OAuth Credentials

1. Go to **"APIs & Services" > "Credentials"**
2. Click **"Create Credentials"** > **"OAuth client ID"**
3. If prompted, configure the **OAuth consent screen**:
   - User Type: **External**
   - App name: Your app name (e.g., "Face Recognition Auth")
   - User support email: Your email
   - Developer contact: Your email
   - Click **"Save and Continue"**
   - Add scopes: `userinfo.email` and `userinfo.profile`
   - Click **"Save and Continue"**
   - Add test users (your email) for testing
   - Click **"Save and Continue"**

4. **Create OAuth Client ID**:
   - Application type: **Web application**
   - Name: "Face Recognition Auth Client"
   - Authorized redirect URIs: Add these:
     - `http://localhost:5000/auth/google/callback`
     - `http://127.0.0.1:5000/auth/google/callback`
   - Click **"Create"**

5. **Copy your credentials**:
   - **Client ID**: `something.apps.googleusercontent.com`
   - **Client Secret**: `your-secret-key`

## Step 4: Update Your Application

Open `app.py` and replace these lines:

```python
app.config['GOOGLE_CLIENT_ID'] = 'YOUR_GOOGLE_CLIENT_ID'  # Paste your Client ID here
app.config['GOOGLE_CLIENT_SECRET'] = 'YOUR_GOOGLE_CLIENT_SECRET'  # Paste your Client Secret here
```

## Step 5: Test Google Login

1. Start your Flask server: `py app.py`
2. Open browser: `http://localhost:5000`
3. Click **"Login with Google"**
4. Sign in with your Google account
5. You should be redirected to the success page!

## 🔐 Security Notes

- The current setup uses `OAUTHLIB_INSECURE_TRANSPORT = '1'` for **development only**
- **For production**:
  - Remove this line
  - Use HTTPS
  - Update redirect URIs to your production URL
  - Store secrets in environment variables, not in code

## ✅ Features

After Google login:
- User is automatically created in database
- Can optionally register face for dual authentication
- Google + Face = Maximum security!
- Avatar from Google account is stored
- Email and name are automatically populated

## 🎯 Usage

Users can now:
1. **Login with Google** - Quick and secure
2. **Register face after Google login** - For future face-only authentication
3. **Use both methods** - Maximum security with Google + Face recognition
4. **Manual face registration** - No Google account needed for face-only auth
