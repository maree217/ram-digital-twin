#!/usr/bin/env python3
"""
Firebase setup script for Ram Digital Twin project
Creates Firebase project and configures Firestore
"""
import os
import sys
import json
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_firebase_project():
    """Set up Firebase project using Firebase CLI"""
    
    try:
        logger.info("🚀 Setting up Firebase project...")
        
        # Check if Firebase CLI is available
        result = subprocess.run(["firebase", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ Firebase CLI not found. Please install it first:")
            logger.info("npm install -g firebase-tools")
            return False
        
        logger.info(f"✅ Firebase CLI version: {result.stdout.strip()}")
        
        # Check if already logged in
        result = subprocess.run(["firebase", "projects:list"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ Not logged in to Firebase. Please run: firebase login")
            return False
        
        project_id = "ram-digital-twin"
        
        # Check if project already exists
        if project_id in result.stdout:
            logger.info(f"✅ Firebase project '{project_id}' already exists")
        else:
            # Create new project
            logger.info(f"🔨 Creating new Firebase project: {project_id}")
            create_result = subprocess.run([
                "firebase", "projects:create", project_id,
                "--display-name", "Ram Digital Twin"
            ], capture_output=True, text=True)
            
            if create_result.returncode == 0:
                logger.info(f"✅ Project '{project_id}' created successfully")
            else:
                logger.error(f"❌ Failed to create project: {create_result.stderr}")
                # Project might already exist or name might be taken
                logger.info("Continuing with existing project...")
        
        # Initialize Firebase in current directory
        logger.info("🔧 Initializing Firebase configuration...")
        
        # Create firebase.json if it doesn't exist
        firebase_config = {
            "firestore": {
                "rules": "firestore.rules",
                "indexes": "firestore.indexes.json"
            },
            "hosting": {
                "public": "public",
                "ignore": [
                    "firebase.json",
                    "**/.*",
                    "**/node_modules/**"
                ],
                "rewrites": [
                    {
                        "source": "**",
                        "destination": "/index.html"
                    }
                ]
            }
        }
        
        with open("firebase.json", "w") as f:
            json.dump(firebase_config, f, indent=2)
        
        logger.info("✅ Created firebase.json")
        
        # Create Firestore rules
        firestore_rules = '''rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Conversations collection
    match /conversations/{conversationId} {
      allow read, write: if true; // For demo purposes - restrict in production
    }
    
    // Leads collection  
    match /leads/{leadId} {
      allow read, write: if true; // For demo purposes - restrict in production
    }
    
    // Analytics collection
    match /analytics/{document} {
      allow read, write: if true; // For demo purposes - restrict in production
    }
  }
}'''
        
        with open("firestore.rules", "w") as f:
            f.write(firestore_rules)
        
        logger.info("✅ Created firestore.rules")
        
        # Create Firestore indexes
        firestore_indexes = {
            "indexes": [
                {
                    "collectionGroup": "conversations",
                    "queryScope": "COLLECTION",
                    "fields": [
                        {"fieldPath": "startTime", "order": "DESCENDING"},
                        {"fieldPath": "status", "order": "ASCENDING"}
                    ]
                },
                {
                    "collectionGroup": "leads",
                    "queryScope": "COLLECTION", 
                    "fields": [
                        {"fieldPath": "leadScore", "order": "DESCENDING"},
                        {"fieldPath": "status", "order": "ASCENDING"}
                    ]
                }
            ],
            "fieldOverrides": []
        }
        
        with open("firestore.indexes.json", "w") as f:
            json.dump(firestore_indexes, f, indent=2)
        
        logger.info("✅ Created firestore.indexes.json")
        
        # Use the project
        logger.info(f"🎯 Setting Firebase project to: {project_id}")
        use_result = subprocess.run([
            "firebase", "use", project_id
        ], capture_output=True, text=True)
        
        if use_result.returncode != 0:
            logger.warning(f"⚠️ Could not use project directly: {use_result.stderr}")
            logger.info("Continuing with manual project selection...")
        
        # Generate service account key
        logger.info("🔑 Setting up service account...")
        
        # Create service account via gcloud if available
        gcloud_result = subprocess.run(["gcloud", "--version"], capture_output=True, text=True)
        if gcloud_result.returncode == 0:
            logger.info("✅ Google Cloud CLI available")
            
            # Create service account
            sa_email = f"ram-digital-twin@{project_id}.iam.gserviceaccount.com"
            
            create_sa_result = subprocess.run([
                "gcloud", "iam", "service-accounts", "create", "ram-digital-twin",
                "--display-name", "Ram Digital Twin Service Account",
                "--project", project_id
            ], capture_output=True, text=True)
            
            if create_sa_result.returncode == 0 or "already exists" in create_sa_result.stderr:
                logger.info("✅ Service account ready")
                
                # Generate key
                key_file = "firebase-service-account.json"
                key_result = subprocess.run([
                    "gcloud", "iam", "service-accounts", "keys", "create", key_file,
                    "--iam-account", sa_email,
                    "--project", project_id
                ], capture_output=True, text=True)
                
                if key_result.returncode == 0:
                    logger.info(f"✅ Service account key generated: {key_file}")
                    
                    # Extract key details for .env
                    with open(key_file, 'r') as f:
                        key_data = json.load(f)
                    
                    update_env_with_firebase_config(key_data, project_id)
                    
                    # Add to .gitignore
                    with open(".gitignore", "a") as f:
                        f.write(f"\n# Firebase service account\n{key_file}\n")
                    
                    logger.info("✅ Updated .env with Firebase configuration")
                else:
                    logger.error(f"❌ Failed to generate service account key: {key_result.stderr}")
        else:
            logger.warning("⚠️ Google Cloud CLI not available, manual setup required")
            logger.info("Please manually create a service account key and update .env file")
        
        logger.info("🎉 Firebase setup completed!")
        logger.info(f"📋 Next steps:")
        logger.info(f"   1. Ensure Firestore is enabled in Firebase console")
        logger.info(f"   2. Update security rules if needed")
        logger.info(f"   3. Test the integration")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error setting up Firebase: {e}")
        return False

def update_env_with_firebase_config(key_data: dict, project_id: str):
    """Update .env file with Firebase configuration"""
    
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning("⚠️ .env file not found")
        return
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update Firebase configuration
    replacements = {
        "FIREBASE_PROJECT_ID=ram-digital-twin": f"FIREBASE_PROJECT_ID={project_id}",
        "FIREBASE_PRIVATE_KEY_ID=your_firebase_key_id": f"FIREBASE_PRIVATE_KEY_ID={key_data['private_key_id']}",
        "FIREBASE_PRIVATE_KEY=your_firebase_private_key": f"FIREBASE_PRIVATE_KEY={json.dumps(key_data['private_key'])}",
        "FIREBASE_CLIENT_EMAIL=your_firebase_client_email": f"FIREBASE_CLIENT_EMAIL={key_data['client_email']}",
        "FIREBASE_CLIENT_ID=your_firebase_client_id": f"FIREBASE_CLIENT_ID={key_data['client_id']}"
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Write back
    with open(env_file, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    success = setup_firebase_project()
    sys.exit(0 if success else 1)