# backend/services/age_verification_service.py
import asyncio
import hashlib
import secrets
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import jwt
import aiohttp

class AgeVerificationService:
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET_KEY')
        self.verification_providers = {
            'veriff': {
                'api_key': os.getenv('VERIFF_API_KEY'),
                'base_url': 'https://api.veriff.com'
            },
            'jumio': {
                'api_key': os.getenv('JUMIO_API_KEY'),
                'secret': os.getenv('JUMIO_SECRET'),
                'base_url': 'https://api.jumio.com'
            }
        }
        
    async def initiate_age_verification(self, user_id: str, 
                                      method: str = 'document') -> Dict[str, Any]:
        """Initiate age verification process"""
        
        verification_id = f"age_ver_{user_id}_{datetime.now().timestamp()}"
        
        if method == 'document':
            return await self._document_verification(user_id, verification_id)
        elif method == 'facial':
            return await self._facial_age_estimation(user_id, verification_id)
        elif method == 'credit_card':
            return await self._credit_card_verification(user_id, verification_id)
        elif method == 'email':
            return await self._email_age_verification(user_id, verification_id)
        else:
            raise ValueError(f"Unsupported verification method: {method}")
    
    async def _document_verification(self, user_id: str, 
                                   verification_id: str) -> Dict[str, Any]:
        """Verify age using government ID documents"""
        
        # Generate verification session
        session_data = {
            'verification_id': verification_id,
            'user_id': user_id,
            'method': 'document',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        # Create verification session with provider
        provider = self.verification_providers['veriff']
        
        payload = {
            'verification_id': verification_id,
            'callback_url': f"{os.getenv('APP_URL')}/api/verify/callback",
            'user_data': {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{provider['base_url']}/sessions",
                    headers={'X-AUTH-CLIENT': provider['api_key']},
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    return {
                        'verification_id': verification_id,
                        'session_url': result.get('session_url'),
                        'status': 'pending',
                        'expires_at': session_data['expires_at'],
                        'instructions': 'Please upload a government-issued ID document'
                    }
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def _facial_age_estimation(self, user_id: str, 
                                   verification_id: str) -> Dict[str, Any]:
        """Estimate age using facial recognition"""
        
        # This would integrate with services like Amazon Rekognition or specialized age estimation APIs
        return {
            'verification_id': verification_id,
            'method': 'facial',
            'status': 'ready',
            'instructions': 'Please take a selfie for age estimation'
        }
    
    def generate_age_verification_token(self, user_id: str, 
                                      verified_age: int) -> str:
        """Generate JWT token for age verification"""
        
        payload = {
            'user_id': user_id,
            'verified_age': verified_age,
            'verification_date': datetime.now().isoformat(),
            'exp': datetime.now() + timedelta(days=365)  # Expires in 1 year
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return token
    
    def verify_age_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify age verification token"""
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return {
                'user_id': payload['user_id'],
                'verified_age': payload['verified_age'],
                'is_valid': True,
                'expires_at': datetime.fromtimestamp(payload['exp'])
            }
        except jwt.ExpiredSignatureError:
            return {'is_valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'is_valid': False, 'error': 'Invalid token'}