import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import firebase_admin
from firebase_admin import credentials, firestore
from src.config import settings

logger = logging.getLogger(__name__)

class ConversationTracker:
    """Track conversations for business analytics and conversion optimization"""
    
    def __init__(self):
        self.db = None
        self._init_firebase()
    
    def _init_firebase(self):
        """Initialize Firebase connection"""
        try:
            if not firebase_admin._apps:
                # Initialize with service account
                if hasattr(settings, 'firebase_service_account_path'):
                    cred = credentials.Certificate(settings.firebase_service_account_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Fallback initialization for development
                    firebase_admin.initialize_app()
                
                self.db = firestore.client()
                logger.info("✅ Firebase initialized for conversation tracking")
            else:
                self.db = firestore.client()
                
        except Exception as e:
            logger.warning(f"Firebase not available: {e}")
            self.db = None
    
    async def start_conversation(self, conversation_id: str, user_info: Dict = None) -> bool:
        """Start tracking a new conversation"""
        if not self.db:
            return False
            
        try:
            conversation_data = {
                'conversation_id': conversation_id,
                'started_at': datetime.utcnow(),
                'user_info': user_info or {},
                'interaction_count': 0,
                'stage_progression': ['discovery'],
                'lead_score_history': [0],
                'engagement_indicators': [],
                'conversion_achieved': False,
                'last_activity': datetime.utcnow(),
                'session_duration': 0,
                'messages': []
            }
            
            self.db.collection('conversations').document(conversation_id).set(conversation_data)
            logger.info(f"📊 Started tracking conversation: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting conversation tracking: {e}")
            return False
    
    async def record_interaction(self, conversation_id: str, user_message: str, 
                               assistant_response: str, stage: str, lead_score: int,
                               knowledge_sources: int = 0) -> bool:
        """Record each interaction with analytics"""
        if not self.db:
            return False
            
        try:
            interaction_data = {
                'timestamp': datetime.utcnow(),
                'user_message': user_message,
                'assistant_response': assistant_response,
                'response_length': len(assistant_response),
                'stage': stage,
                'lead_score': lead_score,
                'knowledge_sources_used': knowledge_sources,
                'engagement_quality': self._calculate_engagement_quality(user_message, assistant_response)
            }
            
            # Update conversation document
            conv_ref = self.db.collection('conversations').document(conversation_id)
            
            # Get current data
            conv_doc = conv_ref.get()
            if conv_doc.exists:
                conv_data = conv_doc.to_dict()
                
                # Update analytics
                conv_data['interaction_count'] = conv_data.get('interaction_count', 0) + 1
                conv_data['last_activity'] = datetime.utcnow()
                conv_data['stage_progression'].append(stage)
                conv_data['lead_score_history'].append(lead_score)
                
                # Add messages
                conv_data['messages'].append(interaction_data)
                
                # Track engagement indicators
                if self._is_conversion_indicator(user_message):
                    conv_data['engagement_indicators'].append({
                        'type': 'conversion_interest',
                        'timestamp': datetime.utcnow(),
                        'message': user_message[:100]
                    })
                
                # Check for conversion
                if self._is_conversion_achieved(user_message):
                    conv_data['conversion_achieved'] = True
                    conv_data['conversion_timestamp'] = datetime.utcnow()
                
                # Update session duration
                start_time = conv_data.get('started_at')
                if start_time:
                    duration = (datetime.utcnow() - start_time).total_seconds()
                    conv_data['session_duration'] = duration
                
                conv_ref.update(conv_data)
                logger.info(f"📊 Recorded interaction {conv_data['interaction_count']} for {conversation_id}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
            return False
    
    def _calculate_engagement_quality(self, user_message: str, assistant_response: str) -> int:
        """Calculate engagement quality score (1-10)"""
        score = 5  # Base score
        
        user_lower = user_message.lower()
        
        # High engagement indicators
        if len(user_message) > 100:
            score += 2  # Detailed messages
        
        if any(word in user_lower for word in ['specific', 'experience', 'how', 'what', 'when', 'why']):
            score += 1  # Question engagement
        
        if any(word in user_lower for word in ['budget', 'timeline', 'team', 'organization']):
            score += 2  # Business context
        
        if any(word in user_lower for word in ['meeting', 'call', 'consultation', 'discuss']):
            score += 3  # Conversion interest
        
        # Response quality factors
        if len(assistant_response) > 1000:
            score += 1  # Comprehensive response
        
        return min(score, 10)
    
    def _is_conversion_indicator(self, message: str) -> bool:
        """Check if message indicates conversion interest"""
        message_lower = message.lower()
        conversion_keywords = [
            'meeting', 'call', 'consultation', 'discuss further', 'help us',
            'next steps', 'move forward', 'schedule', 'contact', 'interested'
        ]
        return any(keyword in message_lower for keyword in conversion_keywords)
    
    def _is_conversion_achieved(self, message: str) -> bool:
        """Check if message indicates conversion achieved"""
        message_lower = message.lower()
        conversion_keywords = [
            'schedule a call', 'book a meeting', 'set up consultation',
            'contact you', 'phone number', 'calendar', 'availability'
        ]
        return any(keyword in message_lower for keyword in conversion_keywords)
    
    async def get_conversation_analytics(self, conversation_id: str) -> Dict[str, Any]:
        """Get analytics for a specific conversation"""
        if not self.db:
            return {}
            
        try:
            conv_ref = self.db.collection('conversations').document(conversation_id)
            conv_doc = conv_ref.get()
            
            if conv_doc.exists:
                data = conv_doc.to_dict()
                
                # Calculate derived metrics
                analytics = {
                    'conversation_id': conversation_id,
                    'interaction_count': data.get('interaction_count', 0),
                    'session_duration_minutes': data.get('session_duration', 0) / 60,
                    'final_lead_score': data.get('lead_score_history', [0])[-1],
                    'final_stage': data.get('stage_progression', ['unknown'])[-1],
                    'conversion_achieved': data.get('conversion_achieved', False),
                    'engagement_indicators_count': len(data.get('engagement_indicators', [])),
                    'average_response_length': self._calculate_avg_response_length(data.get('messages', [])),
                    'engagement_quality_score': self._calculate_overall_engagement(data.get('messages', []))
                }
                
                return analytics
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting conversation analytics: {e}")
            return {}
    
    def _calculate_avg_response_length(self, messages: List[Dict]) -> int:
        """Calculate average response length"""
        if not messages:
            return 0
        
        total_length = sum(msg.get('response_length', 0) for msg in messages)
        return total_length // len(messages)
    
    def _calculate_overall_engagement(self, messages: List[Dict]) -> float:
        """Calculate overall engagement score"""
        if not messages:
            return 0.0
        
        total_quality = sum(msg.get('engagement_quality', 5) for msg in messages)
        return total_quality / len(messages)
    
    async def get_daily_analytics(self, date: datetime = None) -> Dict[str, Any]:
        """Get analytics for a specific day"""
        if not self.db:
            return {}
            
        target_date = date or datetime.utcnow()
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        try:
            query = self.db.collection('conversations').where(
                'started_at', '>=', start_of_day
            ).where(
                'started_at', '<=', end_of_day
            )
            
            docs = query.stream()
            conversations = [doc.to_dict() for doc in docs]
            
            if not conversations:
                return {'date': target_date.date(), 'total_conversations': 0}
            
            # Calculate aggregated metrics
            analytics = {
                'date': target_date.date(),
                'total_conversations': len(conversations),
                'total_interactions': sum(conv.get('interaction_count', 0) for conv in conversations),
                'conversions_achieved': sum(1 for conv in conversations if conv.get('conversion_achieved', False)),
                'conversion_rate': 0,
                'avg_interactions_per_conversation': 0,
                'avg_session_duration_minutes': 0,
                'avg_final_lead_score': 0,
                'stage_distribution': {},
                'quality_conversations': 0  # 3+ interactions
            }
            
            # Calculate rates and averages
            if analytics['total_conversations'] > 0:
                analytics['conversion_rate'] = (analytics['conversions_achieved'] / analytics['total_conversations']) * 100
                analytics['avg_interactions_per_conversation'] = analytics['total_interactions'] / analytics['total_conversations']
                
                total_duration = sum(conv.get('session_duration', 0) for conv in conversations)
                analytics['avg_session_duration_minutes'] = (total_duration / analytics['total_conversations']) / 60
                
                final_scores = [conv.get('lead_score_history', [0])[-1] for conv in conversations]
                analytics['avg_final_lead_score'] = sum(final_scores) / len(final_scores)
                
                # Quality conversations (3+ interactions)
                analytics['quality_conversations'] = sum(1 for conv in conversations if conv.get('interaction_count', 0) >= 3)
            
            # Stage distribution
            final_stages = [conv.get('stage_progression', ['unknown'])[-1] for conv in conversations]
            for stage in final_stages:
                analytics['stage_distribution'][stage] = analytics['stage_distribution'].get(stage, 0) + 1
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting daily analytics: {e}")
            return {'date': target_date.date(), 'error': str(e)}