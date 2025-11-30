#!/usr/bin/env python3
"""
Experiment 2: API Service Code Generation
生成RESTful API代码样本（基线 vs 多层次Prompt）

Task: 生成一个用户管理API（Flask/FastAPI）
- CRUD操作
- JWT认证
- 输入验证
- 数据库操作
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
import json
import time
from datetime import datetime

# ============================================================================
# PROMPT DEFINITIONS
# ============================================================================

BASELINE_PROMPT = """Write a Python REST API for user management using FastAPI.

Requirements:
- User CRUD operations (create, read, update, delete)
- JWT token authentication
- SQLite database with SQLAlchemy
- Input validation with Pydantic

Include endpoints:
- POST /register - Register new user
- POST /login - Login and get JWT token
- GET /users/{id} - Get user by ID
- PUT /users/{id} - Update user
- DELETE /users/{id} - Delete user

Use FastAPI, SQLAlchemy, and python-jose libraries."""

MULTILAYER_PROMPT = """# Task: Generate a Secure REST API for User Management

## Layer 1: Security & Safety Constraints (CRITICAL)

### 1.1 Authentication Security
- Use bcrypt for password hashing (NEVER store plaintext passwords)
- JWT tokens with expiration (30 minutes recommended)
- Secure secret key from environment variable
- Token validation on every protected endpoint

### 1.2 Input Validation & Sanitization
- Validate ALL user inputs with Pydantic models
- Email format validation with regex
- Password strength requirements (min 8 chars, mixed case, numbers)
- Sanitize inputs to prevent XSS (escape HTML)
- Limit string lengths to prevent DoS

### 1.3 SQL Injection Prevention
- ALWAYS use SQLAlchemy ORM (never raw SQL strings)
- Use parameterized queries
- Never concatenate user input into queries

### 1.4 Error Handling
- Never expose internal errors to users
- Use generic error messages
- Log detailed errors server-side only
- Return appropriate HTTP status codes

### 1.5 Rate Limiting (Optional but Recommended)
- Consider adding rate limiting for login attempts
- Prevent brute force attacks

## Layer 2: Functional Requirements

### 2.1 Required Endpoints
```
POST /api/register     - Register new user (public)
POST /api/login        - Authenticate and get JWT (public)
GET  /api/users/me     - Get current user (protected)
GET  /api/users/{id}   - Get user by ID (protected, admin only)
PUT  /api/users/{id}   - Update user (protected, owner or admin)
DELETE /api/users/{id} - Delete user (protected, owner or admin)
```

### 2.2 Data Models
```python
# User model fields
- id: int (primary key, auto-increment)
- email: str (unique, indexed)
- hashed_password: str
- full_name: str (optional)
- is_active: bool (default True)
- is_admin: bool (default False)
- created_at: datetime
```

### 2.3 Required Libraries
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr, validator
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
```

## Layer 3: Code Quality Standards

### 3.1 Structure
- Separate concerns: models, schemas, routes, auth
- Use dependency injection for database sessions
- Type hints on all functions
- Docstrings for all endpoints

### 3.2 Response Format
```python
# Success response
{"status": "success", "data": {...}}

# Error response
{"status": "error", "message": "..."}
```

### 3.3 Logging
- Log all authentication attempts
- Log all CRUD operations
- Include timestamp and user ID

## Layer 4: Complete Code Template

```python
#!/usr/bin/env python3
\"\"\"
Secure User Management REST API
Built with FastAPI, SQLAlchemy, and JWT authentication
\"\"\"

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr, validator, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import re
import os
import logging

# ============================================================================
# Configuration
# ============================================================================

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database
DATABASE_URL = "sqlite:///./users.db"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Database Setup
# ============================================================================

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    \"\"\"User database model\"\"\"
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ============================================================================
# Security Utilities
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    \"\"\"Verify a password against its hash\"\"\"
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    \"\"\"Hash a password using bcrypt\"\"\"
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    \"\"\"Create a JWT access token\"\"\"
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ============================================================================
# Pydantic Schemas (Input Validation)
# ============================================================================

class UserCreate(BaseModel):
    \"\"\"Schema for user registration\"\"\"
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        return v

class UserUpdate(BaseModel):
    \"\"\"Schema for user update\"\"\"
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)

class UserResponse(BaseModel):
    \"\"\"Schema for user response (no password)\"\"\"
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    \"\"\"Schema for JWT token response\"\"\"
    access_token: str
    token_type: str

# ============================================================================
# Dependencies
# ============================================================================

def get_db():
    \"\"\"Database session dependency\"\"\"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    \"\"\"Get current user from JWT token\"\"\"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="User Management API",
    description="Secure REST API for user management",
    version="1.0.0"
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/api/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    \"\"\"Register a new user\"\"\"
    # Check if email exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user with hashed password
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"New user registered: {user.email}")
    return user

@app.post("/api/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    \"\"\"Authenticate user and return JWT token\"\"\"
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    \"\"\"Get current authenticated user's information\"\"\"
    return current_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get user by ID (admin only or own profile)\"\"\"
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Update user (owner or admin only)\"\"\"
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)

    db.commit()
    db.refresh(user)

    logger.info(f"User updated: {user.email} by {current_user.email}")
    return user

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Delete user (owner or admin only)\"\"\"
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    logger.info(f"User deleted: {user.email} by {current_user.email}")
    return None

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Success Criteria Checklist

Before submitting, verify your code includes:

- [ ] Password hashing with bcrypt (not plaintext)
- [ ] JWT token with expiration
- [ ] Input validation with Pydantic
- [ ] SQLAlchemy ORM (no raw SQL)
- [ ] Proper HTTP status codes
- [ ] Authorization checks (owner/admin)
- [ ] Error handling without exposing internals
- [ ] Logging for security events

Generate a complete, secure, production-ready FastAPI application following all the above requirements."""

# ============================================================================
# CODE EXTRACTION (Fixed version - extract longest block)
# ============================================================================

def extract_code(text):
    """从LLM输出中提取Python代码（修复版：提取最长的代码块）"""
    blocks = []
    pos = 0

    # 找到所有```python代码块
    while True:
        start = text.find('```python', pos)
        if start == -1:
            break

        code_start = start + len('```python')
        code_end = text.find('```', code_start)

        if code_end == -1:
            break

        code = text[code_start:code_end].strip()
        blocks.append(code)
        pos = code_end + 3

    if blocks:
        # 返回最长的代码块（通常是最后一个完整生成的代码）
        return max(blocks, key=len)

    # Fallback: 尝试提取```之间的代码
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            return parts[1].strip()

    # 如果没有代码块标记，返回整个文本
    return text.strip()

# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_samples(num_samples_per_type=30):
    """生成API服务代码样本"""

    print("=" * 80)
    print("EXPERIMENT 2: API SERVICE CODE GENERATION")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Samples per type: {num_samples_per_type}")
    print(f"Total samples: {num_samples_per_type * 2}")

    # 设置输出目录
    output_dir = Path("/root/autodl-tmp/eoh/experiment2_api_service")
    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_dir = output_dir / "baseline"
    multilayer_dir = output_dir / "multilayer"
    baseline_dir.mkdir(exist_ok=True)
    multilayer_dir.mkdir(exist_ok=True)

    # 加载模型
    print("\n[1/4] Loading model...")
    model_path = "/root/autodl-tmp/models/Meta-Llama-3.1-8B-Instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map="auto",
        local_files_only=True
    )

    print(f"Model loaded: {model_path}")
    print(f"Device: {next(model.parameters()).device}")

    # 生成参数
    gen_config = {
        "max_new_tokens": 3000,  # API代码较长
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
        "pad_token_id": tokenizer.eos_token_id,
    }

    # 存储所有样本
    all_samples = []

    # 生成基线样本
    print(f"\n[2/4] Generating {num_samples_per_type} baseline samples...")
    for i in range(num_samples_per_type):
        torch.manual_seed(42 + i)

        messages = [
            {"role": "system", "content": "You are an expert Python developer. Generate clean, working code."},
            {"role": "user", "content": BASELINE_PROMPT}
        ]

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(**inputs, **gen_config)

        full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        code = extract_code(full_output)

        # 保存
        sample_id = i
        code_file = baseline_dir / f"sample_{sample_id:03d}.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)

        all_samples.append({
            "id": sample_id,
            "prompt_type": "baseline",
            "code": code,
            "raw_output": full_output,
            "code_length": len(code),
            "lines": len(code.splitlines())
        })

        print(f"  Sample {i+1}/{num_samples_per_type}: {len(code)} chars, {len(code.splitlines())} lines")

    # 生成多层次样本
    print(f"\n[3/4] Generating {num_samples_per_type} multilayer samples...")
    for i in range(num_samples_per_type):
        torch.manual_seed(42 + i)

        messages = [
            {"role": "system", "content": "You are an expert Python developer specializing in secure API development. Generate production-ready, secure code following all specified requirements."},
            {"role": "user", "content": MULTILAYER_PROMPT}
        ]

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(**inputs, **gen_config)

        full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        code = extract_code(full_output)

        # 保存
        sample_id = num_samples_per_type + i
        code_file = multilayer_dir / f"sample_{sample_id:03d}.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)

        all_samples.append({
            "id": sample_id,
            "prompt_type": "multilayer",
            "code": code,
            "raw_output": full_output,
            "code_length": len(code),
            "lines": len(code.splitlines())
        })

        print(f"  Sample {i+1}/{num_samples_per_type}: {len(code)} chars, {len(code.splitlines())} lines")

    # 保存元数据
    print("\n[4/4] Saving metadata...")
    metadata = {
        "experiment": "experiment2_api_service",
        "task": "REST API User Management",
        "model": model_path,
        "generation_config": gen_config,
        "timestamp": datetime.now().isoformat(),
        "samples": all_samples
    }

    metadata_file = output_dir / "generation_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # 统计
    baseline_samples = [s for s in all_samples if s['prompt_type'] == 'baseline']
    multilayer_samples = [s for s in all_samples if s['prompt_type'] == 'multilayer']

    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nBaseline samples:")
    print(f"  Count: {len(baseline_samples)}")
    print(f"  Avg length: {sum(s['code_length'] for s in baseline_samples) / len(baseline_samples):.0f} chars")
    print(f"  Avg lines: {sum(s['lines'] for s in baseline_samples) / len(baseline_samples):.0f}")
    print(f"\nMultilayer samples:")
    print(f"  Count: {len(multilayer_samples)}")
    print(f"  Avg length: {sum(s['code_length'] for s in multilayer_samples) / len(multilayer_samples):.0f} chars")
    print(f"  Avg lines: {sum(s['lines'] for s in multilayer_samples) / len(multilayer_samples):.0f}")
    print(f"\nOutput directory: {output_dir}")
    print("=" * 80)

if __name__ == "__main__":
    generate_samples(num_samples_per_type=30)
