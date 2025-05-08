from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .supabase_config import supabase
from starlette.middleware.sessions import SessionMiddleware
from .routers import blog, auth
from .dependencies import get_current_user

app = FastAPI(title="Blog Demo")

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",  # In production, use a secure secret key
    session_cookie="supabase_session"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(blog.router, prefix="/blog", tags=["blog"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def home(request: Request, user = Depends(get_current_user)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Blog Demo",
            "user": user
        }
    ) 