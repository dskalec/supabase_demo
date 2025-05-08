from fastapi import APIRouter, Request, HTTPException, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..supabase_config import supabase
from postgrest.exceptions import APIError
from ..dependencies import get_current_user
from typing import Optional
import uuid
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

async def upload_image(file: Optional[UploadFile] = None) -> Optional[str]:
    if not file:
        return None
        
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_extension}"
    
    # Upload to Supabase Storage
    try:
        file_content = await file.read()
        result = supabase.storage.from_('post_images').upload(
            file_name,
            file_content,
            {"content-type": file.content_type}
        )
        
        # Get the public URL
        url = supabase.storage.from_('post_images').get_public_url(file_name)
        return url
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

async def delete_image(image_url: str) -> bool:
    if not image_url:
        return True
        
    try:
        # Extract filename from URL
        file_name = image_url.split('/')[-1]
        supabase.storage.from_('post_images').remove([file_name])
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

@router.get("/posts", name="list_posts")
async def list_posts(request: Request, user = Depends(get_current_user)):
    try:
        # First, get just the posts (this will work due to RLS policy)
        posts = supabase.table("posts").select(
            "id, title, content, image_url, created_at, view_count, user_id"
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

@router.get("/posts/new", name="new_post")
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

@router.post("/posts", name="create_post")
async def create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    try:
        # Upload image if provided
        image_url = await upload_image(image)
        
        # Create post
        result = supabase.table("posts").insert({
            "title": title,
            "content": content,
            "image_url": image_url,
            "user_id": user["id"]
        }).execute()
        
        return RedirectResponse(url="/blog/posts", status_code=303)
    except APIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/posts/{post_id}", name="get_post")
async def get_post(
    post_id: str,
    request: Request,
    user: Optional[dict] = Depends(get_current_user)
):
    """Get a single post by ID."""
    try:
        # Get the post
        response = supabase.table("posts").select(
            "id, title, content, image_url, created_at, view_count, user_id"
        ).eq("id", post_id).single().execute()
        post = response.data

        # Get comments for the post
        comments_response = supabase.table("comments").select(
            "id, content, created_at, user_id"
        ).eq("post_id", post_id).order("created_at").execute()
        
        comments = comments_response.data

        # Record view if user is authenticated
        if user:
            supabase.table("post_views").insert({
                "post_id": post_id,
                "user_id": user["id"]
            }).execute()

        return templates.TemplateResponse(
            "blog/post_detail.html",
            {
                "request": request,
                "post": post,
                "comments": comments,
                "user": user
            }
        )
    except Exception as e:
        print(f"Error getting post: {e}")
        raise HTTPException(status_code=404, detail="Post not found")

@router.get("/posts/{post_id}/edit", name="edit_post")
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

@router.post("/posts/{post_id}", name="update_post")
async def update_post(
    request: Request,
    post_id: str,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    remove_image: bool = Form(False),
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    try:
        # Get current post
        post = supabase.table("posts").select("*").eq("id", post_id).single().execute()
        
        if not post.data:
            raise HTTPException(status_code=404, detail="Post not found")
            
        if post.data["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Handle image
        image_url = post.data.get("image_url")
        if remove_image and image_url:
            await delete_image(image_url)
            image_url = None
        elif image:
            # Delete old image if exists
            if image_url:
                await delete_image(image_url)
            # Upload new image
            image_url = await upload_image(image)
            
        # Update post
        result = supabase.table("posts").update({
            "title": title,
            "content": content,
            "image_url": image_url
        }).eq("id", post_id).execute()
        
        return RedirectResponse(url=f"/blog/posts/{post_id}", status_code=303)
    except APIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/posts/{post_id}/delete", name="delete_post")
async def delete_post(
    request: Request,
    post_id: str,
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    try:
        # Get post to check ownership and get image URL
        post = supabase.table("posts").select("*").eq("id", post_id).single().execute()
        
        if not post.data:
            raise HTTPException(status_code=404, detail="Post not found")
            
        if post.data["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Delete image if exists
        if post.data.get("image_url"):
            await delete_image(post.data["image_url"])
            
        # Delete post
        result = supabase.table("posts").delete().eq("id", post_id).execute()
        
        return RedirectResponse(url="/blog/posts", status_code=303)
    except APIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/posts/{post_id}/comments", name="create_comment")
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

@router.post("/comments/{comment_id}", name="update_comment")
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

@router.post("/comments/{comment_id}/delete", name="delete_comment")
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