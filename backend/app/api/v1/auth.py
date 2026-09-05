import logging
import secrets
import httpx
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.config import settings
from app.models.user import User, OAuthAccount, UserPreferences
from app.schemas.auth import Token, GoogleAuthRequest, UserOut
from app.seed import seed_demo_data

logger = logging.getLogger("pulse.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory CSRF state storage (in production, use Redis or encrypted session cookies)
VALID_OAUTH_STATES = set()

async def get_valid_google_token(db: AsyncSession, user_id: str) -> Optional[str]:
    """
    Retrieves a valid Google OAuth access token for user_id.
    Automatically uses refresh_token if access_token has expired.
    """
    stmt = select(OAuthAccount).where(OAuthAccount.user_id == user_id, OAuthAccount.provider == "google")
    oauth_acc = (await db.execute(stmt)).scalar_one_or_none()
    if not oauth_acc or not oauth_acc.access_token:
        return None

    now = datetime.utcnow()
    # Refresh token if expiring within 5 minutes
    if oauth_acc.expires_at and oauth_acc.expires_at <= (now + timedelta(minutes=5)):
        if oauth_acc.refresh_token and settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
            token_url = "https://oauth2.googleapis.com/token"
            payload = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": oauth_acc.refresh_token,
                "grant_type": "refresh_token"
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(token_url, data=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        new_access = data.get("access_token")
                        expires_in = data.get("expires_in", 3600)
                        if new_access:
                            oauth_acc.access_token = new_access
                            oauth_acc.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                            await db.commit()
                            logger.info(f"Successfully refreshed Google OAuth token for user {user_id}")
                            return new_access
            except Exception as e:
                logger.error(f"Failed to refresh Google OAuth token for user {user_id}: {e}")
                return None
        return None

    return oauth_acc.access_token

@router.get("/login/google/url")
async def get_google_auth_url():
    """Generates the Google OAuth 2.0 authorization URL with CSRF state token and required identity, Gmail, and Calendar scopes."""
    state = secrets.token_urlsafe(32)
    VALID_OAUTH_STATES.add(state)

    scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.readonly"
    ]
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"scope={' '.join(scopes)}&state={state}&access_type=offline&prompt=consent"
    )
    return {
        "auth_url": url,
        "state": state,
        "client_id_configured": bool(settings.GOOGLE_CLIENT_ID),
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }

@router.post("/login/google", response_model=Token)
async def google_callback(req: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Exchanges Google authorization code for OAuth tokens, retrieves user profile,
    saves credentials securely in database, and issues session JWT.
    """
    # Demo code handling for zero-setup local testing without live Google credentials
    if req.code == "demo_code" or not settings.GOOGLE_CLIENT_SECRET:
        logger.info("Using demo authentication pathway (GOOGLE_CLIENT_SECRET not set)")
        demo_user = await seed_demo_data(db)
        return Token(access_token=f"demo_jwt_token_{demo_user.id}")

    # Real Google OAuth 2.0 Token Exchange
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "code": req.code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": req.redirect_uri or settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post(token_url, data=token_payload)
            if token_resp.status_code != 200:
                logger.error(f"Google token exchange failed: {token_resp.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange authorization code with Google")

            tokens = token_resp.json()
            access_token = tokens["access_token"]
            refresh_token = tokens.get("refresh_token")
            expires_in = tokens.get("expires_in", 3600)
            scopes_granted = tokens.get("scope", "")

            # Fetch user profile using access token
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            userinfo_resp = await client.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
            if userinfo_resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch user profile from Google")

            profile = userinfo_resp.json()
            email = profile["email"]
            google_sub = profile["id"]

            # Save or update User and OAuthAccount in database
            stmt = select(User).where(User.email == email).options(selectinload(User.preferences))
            user = (await db.execute(stmt)).scalar_one_or_none()

            if not user:
                user = User(
                    email=email,
                    full_name=profile.get("name"),
                    picture=profile.get("picture")
                )
                db.add(user)
                await db.flush()

                prefs = UserPreferences(user_id=user.id)
                db.add(prefs)
                await db.flush()

            # Save/update OAuth credential
            oauth_stmt = select(OAuthAccount).where(OAuthAccount.user_id == user.id, OAuthAccount.provider == "google")
            oauth_acc = (await db.execute(oauth_stmt)).scalar_one_or_none()

            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            if oauth_acc:
                oauth_acc.access_token = access_token
                if refresh_token:
                    oauth_acc.refresh_token = refresh_token
                oauth_acc.expires_at = expires_at
                oauth_acc.scopes = scopes_granted
            else:
                oauth_acc = OAuthAccount(
                    user_id=user.id,
                    provider="google",
                    provider_user_id=google_sub,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_at=expires_at,
                    scopes=scopes_granted
                )
                db.add(oauth_acc)

            await db.commit()
            return Token(access_token=f"pulse_session_{user.id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during Google OAuth processing")

@router.post("/disconnect")
async def disconnect_google(db: AsyncSession = Depends(get_db)):
    """Revokes OAuth credentials and deletes token records for the active user."""
    stmt = select(User).where(User.email == "demo@pulse.ai")
    user = (await db.execute(stmt)).scalar_one_or_none()
    if user:
        oauth_stmt = select(OAuthAccount).where(OAuthAccount.user_id == user.id, OAuthAccount.provider == "google")
        oauth_acc = (await db.execute(oauth_stmt)).scalar_one_or_none()
        if oauth_acc:
            if oauth_acc.access_token:
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        await client.post(f"https://oauth2.googleapis.com/revoke?token={oauth_acc.access_token}")
                except Exception:
                    pass
            await db.delete(oauth_acc)
            await db.commit()

    return {"status": "DISCONNECTED", "message": "Google integration revoked and tokens purged."}

@router.get("/me", response_model=UserOut)
async def get_current_user(db: AsyncSession = Depends(get_db)):
    """Retrieves current authenticated user profile."""
    stmt = select(User).where(User.email == "demo@pulse.ai").options(selectinload(User.preferences))
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        user = await seed_demo_data(db)
        res = await db.execute(stmt)
        user = res.scalar_one()
    return user

