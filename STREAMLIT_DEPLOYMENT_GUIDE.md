# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Community Cloud

### Prerequisites
- GitHub repository (✅ Already done: `https://github.com/maree217/ram-digital-twin`)
- Streamlit account (free at https://streamlit.io/)

### Step 1: Connect to Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account (`maree217`)
3. Click "New app"

### Step 2: Deploy Configuration
```
Repository: maree217/ram-digital-twin
Branch: main
Main file path: streamlit_app.py
App URL: ram-digital-twin (or custom name)
```

### Step 3: Configure Secrets (Optional but Recommended)
In the Streamlit Cloud dashboard, add these secrets for full functionality:

```toml
# Required for AI responses
GOOGLE_API_KEY = "your_gemini_api_key"

# Optional for enhanced search
PINECONE_API_KEY = "your_pinecone_key"
PINECONE_INDEX_NAME = "ram-knowledge-base"

# Optional for analytics
FIREBASE_PROJECT_ID = "your_firebase_project"
```

### Step 4: Deploy!
Click "Deploy" and your app will be live at:
`https://ram-digital-twin.streamlit.app/`

## App Features That Work Without API Keys
- ✅ Professional interface and branding
- ✅ Conversation flow and lead scoring
- ✅ Local knowledge search (3 documents)
- ✅ Contact information and scheduling links
- ✅ Full user experience demo

## Enhanced Features with API Keys
- 🚀 AI-powered responses via Google Gemini
- 🔍 Advanced vector search via Pinecone
- 📊 Analytics tracking via Firebase

## Client Access
Once deployed, share this URL with clients:
`https://ram-digital-twin.streamlit.app/`

## Maintenance
- Updates to GitHub automatically trigger redeployment
- Monitor usage and performance in Streamlit Cloud dashboard
- Manage secrets and configuration through web interface

---

**Ready for immediate client use! 🎯**