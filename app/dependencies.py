from fastapi import Request
from .supabase_config import supabase

async def get_current_user(request: Request):
    try:
        # Get the session tokens from the request
        session_data = request.session.get("supabase_session")
        if not session_data:
            return None
            
        # Set the session with both tokens
        supabase.auth.set_session(
            access_token=session_data["access_token"],
            refresh_token=session_data["refresh_token"]
        )
        
        # Get the user
        user = supabase.auth.get_user()
        
        if not user:
            return None
            
        user_data = {
            "id": user.user.id,
            "email": user.user.email,
            "display_name": user.user.user_metadata.get("display_name", user.user.email)
        }
        return user_data
    except Exception as e:
        print(f"Debug - Error getting user: {str(e)}")  # Debug print
        return None 
