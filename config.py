"""
Configuration and environment management for Project Data-Exorcism.
Centralizes all configuration with validation and type safety.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import logging

load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation"""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    
    @classmethod
    def from_env(cls):
        """Initialize from environment variables with validation"""
        required_keys = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY_ID', 
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL',
            'FIREBASE_CLIENT_ID'
        ]
        
        missing = [k for k in required_keys if not os.getenv(k)]
        if missing:
            raise ValueError(f"Missing Firebase config: {missing}")
        
        # Handle escaped newlines in private key
        private_key = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
        
        return cls(
            project_id=os.getenv('FIREBASE_PROJECT_ID', ''),
            private_key_id=os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
            private_key=private_key,
            client_email=os.getenv('FIREBASE_CLIENT_EMAIL', ''),
            client_id=os.getenv('FIREBASE_CLIENT_ID', '')
        )

@dataclass
class BlockchainConfig:
    """Blockchain and wallet configuration"""
    l2_rpc_url: str = os.getenv('L2_RPC_URL', 'https://arb1.arbitrum.io/rpc')
    treasury_address: str = os.getenv('TREASURY_ADDRESS', '')
    private_key: Optional[str] = os.getenv('WALLET_PRIVATE_KEY')
    chain_id: int = int(os.getenv('CHAIN_ID', '42161'))
    
    def validate(self):
        """Validate blockchain configuration"""
        if not self.treasury_address:
            raise ValueError("TREASURY_ADDRESS must be set")
        if not self.private_key:
            logging.warning("WALLET_PRIVATE_KEY not set - transaction signing disabled")

@dataclass 
class SystemConfig:
    """System operation configuration"""
    collection_interval: int = int(os.getenv('COLLECTION_INTERVAL', '60'))
    max_packet_size: int = int(os.getenv('MAX_PACKET_SIZE', '10240'))
    min_stress_threshold: float = float(os.getenv('MIN_STRESS_THRESHOLD', '0.7'))
    
class Config:
    """Main configuration singleton"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize all configuration components"""
        try:
            self.firebase = FirebaseConfig.from_env()
            self.blockchain = BlockchainConfig()
            self.system = SystemConfig()
            self.log_level = os.getenv('LOG_LEVEL', 'INFO')
            
            # Validate configurations
            self.blockchain.validate()
            
        except Exception as e:
            logging.error(f"Configuration initialization failed: {e}")
            raise
    
    def get_firebase_credentials(self) -> dict:
        """Get Firebase credentials as dict for initialization"""
        return {
            "type": "service_account",
            "project_id": self.firebase.project_id,
            "private_key_id": self.firebase.private_key_id,
            "private_key": self.firebase.private_key,
            "client_email": self.firebase.client_email,
            "client_id": self.firebase.client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.firebase.client_email}"
        }

# Global configuration instance
config = Config()