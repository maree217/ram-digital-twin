#!/usr/bin/env python3
"""
Manual Firebase setup instructions and testing
"""
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def provide_manual_setup_instructions():
    """Provide instructions for manual Firebase setup"""
    
    logger.info("🔧 Manual Firebase Setup Instructions")
    logger.info("=" * 50)
    
    logger.info("✅ Firebase project 'ram-digital-twin' has been created!")
    logger.info("")
    logger.info("📋 To complete the setup:")
    logger.info("")
    logger.info("1. 🌐 Open Firebase Console:")
    logger.info("   https://console.firebase.google.com/project/ram-digital-twin")
    logger.info("")
    logger.info("2. 🔥 Enable Firestore:")
    logger.info("   - Go to Firestore Database")
    logger.info("   - Click 'Create database'")
    logger.info("   - Choose 'Start in test mode' for now")
    logger.info("   - Select a location (us-central1 recommended)")
    logger.info("")
    logger.info("3. 🔑 Create Service Account:")
    logger.info("   - Go to Project Settings > Service Accounts")
    logger.info("   - Click 'Generate new private key'")
    logger.info("   - Download the JSON file")
    logger.info("   - Save it as 'firebase-service-account.json' in this directory")
    logger.info("")
    logger.info("4. 🔧 Update Environment:")
    logger.info("   - Run this script again after downloading the service account key")
    logger.info("")
    
    # Check if service account key exists
    key_file = Path("firebase-service-account.json")
    if key_file.exists():
        logger.info("✅ Found firebase-service-account.json")
        
        try:
            with open(key_file, 'r') as f:
                key_data = json.load(f)
            
            update_env_with_firebase_config(key_data)
            logger.info("✅ Updated .env file with Firebase configuration")
            
            # Test Firebase connection
            test_firebase_connection()
            
        except Exception as e:
            logger.error(f"❌ Error reading service account key: {e}")
    else:
        logger.warning("⚠️ firebase-service-account.json not found")
        logger.info("Please download it from Firebase Console and run this script again")

def update_env_with_firebase_config(key_data: dict):
    """Update .env file with Firebase configuration"""
    
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning("⚠️ .env file not found")
        return
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update Firebase configuration
    project_id = key_data['project_id']
    private_key = key_data['private_key'].replace('\n', '\\n')
    
    replacements = {
        "FIREBASE_PROJECT_ID=ram-digital-twin": f"FIREBASE_PROJECT_ID={project_id}",
        "FIREBASE_PRIVATE_KEY_ID=your_firebase_key_id": f"FIREBASE_PRIVATE_KEY_ID={key_data['private_key_id']}",
        "FIREBASE_PRIVATE_KEY=your_firebase_private_key": f"FIREBASE_PRIVATE_KEY=\"{private_key}\"",
        "FIREBASE_CLIENT_EMAIL=your_firebase_client_email": f"FIREBASE_CLIENT_EMAIL={key_data['client_email']}",
        "FIREBASE_CLIENT_ID=your_firebase_client_id": f"FIREBASE_CLIENT_ID={key_data['client_id']}"
    }
    
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
    
    # Write back
    with open(env_file, 'w') as f:
        f.write(content)

def test_firebase_connection():
    """Test Firebase connection"""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Initialize Firebase
        key_file = Path("firebase-service-account.json")
        cred = credentials.Certificate(str(key_file))
        
        # Initialize app if not already done
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        # Test Firestore connection
        db = firestore.client()
        
        # Try to write a test document
        test_doc = {
            'test': True,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Firebase connection test'
        }
        
        doc_ref = db.collection('test').document('connection_test')
        doc_ref.set(test_doc)
        
        logger.info("✅ Firebase connection test successful!")
        
        # Clean up test document
        doc_ref.delete()
        
        return True
        
    except ImportError:
        logger.warning("⚠️ firebase-admin not installed")
        logger.info("Firebase configuration updated, but connection not tested")
        return False
    except Exception as e:
        logger.error(f"❌ Firebase connection test failed: {e}")
        return False

if __name__ == "__main__":
    provide_manual_setup_instructions()