from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .supabase_config import supabase

app = FastAPI(title="Blog Demo")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def home(request: Request):
    try:
        # Test Supabase connection
        response = supabase.table("dummy").select("*").execute()
        supabase_status = "Connected to Supabase!"
    except Exception as e:
        supabase_status = f"Supabase connection error: {str(e)}"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Blog Demo",
            "supabase_status": supabase_status
        }
    ) 