from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from ..supabase_config import supabase
from postgrest.exceptions import APIError
from ..dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/posts")
async def list_posts(request: Request, user = Depends(get_current_user)):
    try:
        # Use the posts_with_users view instead of the posts table
        posts = supabase.table("posts_with_users").select(
            "*"
        ).order("created_at", desc=True).execute()
    
        return templates.TemplateResponse(
            "blog/posts.html",
            {
                "request": request,
                "posts": posts.data,
                "user": user,
                "title": "Blog Posts"  # Added title for consistency
            }
        )
    except APIError as e:
        print(f"Error fetching posts: {str(e)}")  # Debug print
        return templates.TemplateResponse(
            "blog/posts.html",
            {
                "request": request,
                "posts": [],
                "user": user,
                "title": "Blog Posts"  # Added title for consistency
            }
        )

@router.get("/posts/{post_id}")
async def get_post(request: Request, post_id: str, user = Depends(get_current_user)):
    try:
        # Use the posts_with_users view instead of the posts table
        post = supabase.table("posts_with_users").select(
            "*"
        ).eq("id", post_id).single().execute()

        # Use the comments_with_users view instead of the comments table
        comments = supabase.table("comments_with_users").select(
            "*"
        ).eq("post_id", post_id).order("created_at").execute()

        return templates.TemplateResponse(
            "blog/post_detail.html",
            {
                "request": request,
                "post": post.data,
                "comments": comments.data,
                "user": user
            }
        )
    except APIError as e:
        print(f"Error fetching post: {str(e)}")  # Debug print
        raise HTTPException(status_code=404, detail="Post not found") 