from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..supabase_config import supabase
from postgrest.exceptions import APIError
from ..dependencies import get_current_user
from typing import Optional

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

@router.get("/posts/new")
async def new_post_form(request: Request, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    return templates.TemplateResponse(
        "blog/post_form.html",
        {
            "request": request,
            "user": user,
            "title": "New Post"
        }
    )

@router.post("/posts")
async def create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        post = supabase.table("posts").insert({
            "title": title,
            "content": content,
            "user_id": user["id"]
        }).execute()
        
        return RedirectResponse(url=f"/blog/posts/{post.data[0]['id']}", status_code=303)
    except APIError as e:
        print(f"Error creating post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create post")

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
                "user": user,
                "title": post.data["title"]
            }
        )
    except APIError as e:
        print(f"Error fetching post: {str(e)}")  # Debug print
        raise HTTPException(status_code=404, detail="Post not found") 

@router.get("/posts/{post_id}/edit")
async def edit_post_form(request: Request, post_id: str, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    try:
        post = supabase.table("posts").select("*").eq("id", post_id).single().execute()
        
        if post.data["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to edit this post")
        
        return templates.TemplateResponse(
            "blog/post_form.html",
            {
                "request": request,
                "post": post.data,
                "user": user,
                "title": f"Edit: {post.data['title']}"
            }
        )
    except APIError as e:
        print(f"Error fetching post: {str(e)}")
        raise HTTPException(status_code=404, detail="Post not found")

@router.post("/posts/{post_id}")
async def update_post(
    request: Request,
    post_id: str,
    title: str = Form(...),
    content: str = Form(...),
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # First check if user owns the post
        post = supabase.table("posts").select("*").eq("id", post_id).single().execute()
        if post.data["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to edit this post")
        
        # Update the post
        updated_post = supabase.table("posts").update({
            "title": title,
            "content": content
        }).eq("id", post_id).execute()
        
        return RedirectResponse(url=f"/blog/posts/{post_id}", status_code=303)
    except APIError as e:
        print(f"Error updating post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update post")

@router.post("/posts/{post_id}/delete")
async def delete_post_post(request: Request, post_id: str, user = Depends(get_current_user)):
    return await delete_post(request, post_id, user)

@router.delete("/posts/{post_id}")
async def delete_post(request: Request, post_id: str, user = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # First check if user owns the post
        post = supabase.table("posts").select("*").eq("id", post_id).single().execute()
        if post.data["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
        # Delete the post
        supabase.table("posts").delete().eq("id", post_id).execute()
        
        return RedirectResponse(url="/blog/posts", status_code=303)
    except APIError as e:
        print(f"Error deleting post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete post")

@router.post("/posts/{post_id}/comments")
async def create_comment(
    request: Request,
    post_id: str,
    content: str = Form(...),
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        comment = supabase.table("comments").insert({
            "content": content,
            "post_id": post_id,
            "user_id": user["id"]
        }).execute()
        
        return RedirectResponse(url=f"/blog/posts/{post_id}#comments", status_code=303)
    except APIError as e:
        print(f"Error creating comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create comment")

@router.post("/comments/{comment_id}")
async def update_comment(
    request: Request,
    comment_id: str,
    content: str = Form(...),
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # First check if user owns the comment
        comment = supabase.table("comments").select("*").eq("id", comment_id).single().execute()
        if comment.data["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
        
        # Update the comment
        updated_comment = supabase.table("comments").update({
            "content": content
        }).eq("id", comment_id).execute()
        
        return RedirectResponse(url=f"/blog/posts/{comment.data['post_id']}#comments", status_code=303)
    except APIError as e:
        print(f"Error updating comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update comment")

@router.post("/comments/{comment_id}/delete")
async def delete_comment_post(request: Request, comment_id: str, user = Depends(get_current_user)):
    return await delete_comment(request, comment_id, user)

@router.delete("/comments/{comment_id}")
async def delete_comment(request: Request, comment_id: str, user = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # First check if user owns the comment
        comment = supabase.table("comments").select("*").eq("id", comment_id).single().execute()
        if comment.data["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
        post_id = comment.data["post_id"]
        # Delete the comment
        supabase.table("comments").delete().eq("id", comment_id).execute()
        
        return RedirectResponse(url=f"/blog/posts/{post_id}#comments", status_code=303)
    except APIError as e:
        print(f"Error deleting comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete comment") 