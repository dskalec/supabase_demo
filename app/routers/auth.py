from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..supabase_config import supabase
from postgrest.exceptions import APIError
from gotrue.errors import AuthApiError

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse(
        "auth/signup.html",
        {
            "request": request,
            "title": "Sign Up"
        }
    )

@router.post("/signup")
async def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...)
):
    try:
        # Sign up the user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": name
                }
            }
        })
        
        # Redirect to login page with success message
        return RedirectResponse(
            url="/auth/login?message=Please check your email to confirm your account",
            status_code=303
        )
    except APIError as e:
        return templates.TemplateResponse(
            "auth/signup.html",
            {
                "request": request,
                "title": "Sign Up",
                "error": str(e)
            }
        )

@router.get("/login")
async def login_page(request: Request, message: str = None):
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "title": "Login",
            "message": message
        }
    )

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        # Sign in the user
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # Store both access and refresh tokens
        request.session["supabase_session"] = {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
        
        # Redirect to home page
        return RedirectResponse(url="/", status_code=303)
    except AuthApiError as e:
        # Handle invalid credentials specifically
        if "Invalid login credentials" in str(e):
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "title": "Login",
                    "error": "Invalid email or password. Please try again.",
                    "email": email  # Preserve the email for better UX
                }
            )
        # Handle other auth errors
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "title": "Login",
                "error": str(e),
                "email": email
            }
        )
    except Exception as e:
        # Handle unexpected errors
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "title": "Login",
                "error": "An unexpected error occurred. Please try again.",
                "email": email
            }
        )

@router.get("/logout")
async def logout(request: Request):
    # Clear session
    request.session.clear()
    
    # Sign out the user
    supabase.auth.sign_out()
    
    return RedirectResponse(url="/", status_code=303) 