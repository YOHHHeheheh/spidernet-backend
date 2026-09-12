import re
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from app.core.config import settings
import json
import uuid
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PHONE_REGEX = re.compile(r'^(?:\+91|91)?[6-9]\d{9}$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
UPI_REGEX = re.compile(r'^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$')
CCTNS_REGEX = re.compile(r'^FIR-\d{4}-\d{3,6}$')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], role: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt

def validate_query_input(query: str) -> bool:
    # Relaxed validation to allow names, IDs, emails, phones, and FIRs
    if len(query) < 2 or len(query) > 100:
        return False
    # Allow alphanumeric, spaces, underscores, dots, hyphens, @
    if re.match(r'^[a-zA-Z0-9_\-\.\s@\+]+$', query):
        return True
    return False

def log_audit_event(officer_badge: str, ip_address: str, action: str, query_parameter: str):
    timestamp_utc = datetime.now(timezone.utc).isoformat()
    event_id = str(uuid.uuid4())
    
    log_data = {
        "event_id": event_id,
        "officer_badge": officer_badge,
        "ip_address": ip_address,
        "action": action,
        "query_parameter": query_parameter,
        "timestamp_utc": timestamp_utc
    }
    
    # Create deterministic string for hashing
    hash_input = f"{event_id}|{officer_badge}|{action}|{query_parameter}|{timestamp_utc}"
    sha256_hash = hashlib.sha256(hash_input.encode()).hexdigest()
    
    log_data["sha256_integrity_hash"] = sha256_hash
    
    # Append to immutable audit log file
    log_file_path = "audit_log.jsonl"
    with open(log_file_path, "a") as f:
        f.write(json.dumps(log_data) + "\n")
    
    return log_data
