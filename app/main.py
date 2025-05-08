from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .supabase_config import supabase
from .routers import blog

app = FastAPI(title="Blog Demo")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(blog.router, prefix="/blog", tags=["blog"])

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Blog Demo",
        }
    ) 