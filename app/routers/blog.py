from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from ..supabase_config import supabase
from postgrest.exceptions import APIError

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/posts")
async def list_posts(request: Request):
    try:
        # First, get just the posts (this will work due to RLS policy)
        posts = supabase.table("posts").select(
            "*"  # Removed the auth.users join for now
        ).order("created_at", desc=True).execute()
    
        return templates.TemplateResponse(
            "blog/posts.html",
            {
                "request": request,
                "posts": posts.data
            }
        )
    except APIError as e:
        print(f"Error fetching posts: {str(e)}")  # Debug print
        return templates.TemplateResponse(
            "blog/posts.html",
            {
                "request": request,
                "posts": []
            }
        )

@router.get("/posts/{post_id}")
async def get_post(request: Request, post_id: str):
    try:
        # First, get just the post
        post = supabase.table("posts").select(
            "*"  # Removed the auth.users join for now
        ).eq("id", post_id).single().execute()

        # Then get comments
        comments = supabase.table("comments").select(
            "*"  # Removed the auth.users join for now
        ).eq("post_id", post_id).order("created_at").execute()

        return templates.TemplateResponse(
            "blog/post_detail.html",
            {
                "request": request,
                "post": post.data,
                "comments": comments.data
            }
        )
    except APIError as e:
        print(f"Error fetching post: {str(e)}")  # Debug print
        raise HTTPException(status_code=404, detail="Post not found") 