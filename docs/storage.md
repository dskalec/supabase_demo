# Image Upload with Supabase Storage

This document explains how image uploads are implemented in the blog application using Supabase Storage.

## Storage Bucket Setup

The application uses a dedicated storage bucket called `post_images` for storing post images. The bucket is configured with the following settings:

```sql
-- Create a new storage bucket for post images
insert into storage.buckets (id, name, public)
values ('post_images', 'post_images', true);
```

## Row Level Security (RLS) Policies

The storage bucket has the following RLS policies to ensure secure access:

```sql
-- Anyone can view post images
create policy "Anyone can view post images"
  on storage.objects for select
  using ( bucket_id = 'post_images' );

-- Only authenticated users can upload images
create policy "Authenticated users can upload post images"
  on storage.objects for insert
  with check (
    bucket_id = 'post_images'
    and auth.role() = 'authenticated'
  );

-- Users can only update their own images
create policy "Users can update their own post images"
  on storage.objects for update
  using (
    bucket_id = 'post_images'
    and auth.uid() = owner
  );

-- Users can only delete their own images
create policy "Users can delete their own post images"
  on storage.objects for delete
  using (
    bucket_id = 'post_images'
    and auth.uid() = owner
  );
```

## Database Schema

The `posts` table includes an `image_url` column to store the public URL of uploaded images:

```sql
create table posts (
  -- ... other columns ...
  image_url text,
  -- ... other columns ...
);
```

## Implementation Details

### File Upload Process

1. When a user uploads an image:
   - A unique filename is generated using UUID
   - The file is uploaded to the `post_images` bucket
   - The public URL is stored in the post's `image_url` column

2. When updating a post:
   - If a new image is uploaded, the old image is deleted
   - If the image is removed, the old image is deleted
   - The `image_url` is updated accordingly

3. When deleting a post:
   - The associated image is automatically deleted from storage
   - The post record is deleted from the database

### Helper Functions

The application includes two main helper functions for managing images:

```python
async def upload_image(file: Optional[UploadFile] = None) -> Optional[str]:
    """Upload an image to Supabase Storage and return its public URL."""
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
    """Delete an image from Supabase Storage."""
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
```

## Usage in Templates

### Post Form

The post form includes an image upload field:

```html
<div class="mb-3">
    <label for="image" class="form-label">Post Image</label>
    <input type="file" class="form-control" id="image" name="image" accept="image/*">
    {% if post and post.image_url %}
        <div class="mt-2">
            <img src="{{ post.image_url }}" alt="Current post image" class="img-thumbnail" style="max-height: 200px;">
            <div class="form-check mt-2">
                <input class="form-check-input" type="checkbox" id="remove_image" name="remove_image">
                <label class="form-check-label" for="remove_image">
                    Remove current image
                </label>
            </div>
        </div>
    {% endif %}
</div>
```

### Post Display

Posts can display their images in both list and detail views:

```html
<!-- In post list -->
{% if post.image_url %}
    <div class="mb-3">
        <img src="{{ post.image_url }}" alt="Post thumbnail" class="img-thumbnail" style="max-height: 200px;">
    </div>
{% endif %}

<!-- In post detail -->
{% if post.image_url %}
    <div class="mb-4">
        <img src="{{ post.image_url }}" alt="Post image" class="img-fluid rounded">
    </div>
{% endif %}
```

## Security Considerations

1. **File Type Validation**: The file input only accepts image files using `accept="image/*"`
2. **Unique Filenames**: UUIDs are used to prevent filename collisions
3. **RLS Policies**: Strict access control through RLS policies
4. **Automatic Cleanup**: Images are automatically deleted when posts are deleted or updated
5. **Public Access**: Images are publicly viewable but only authenticated users can upload/delete

## Best Practices

1. Always use `enctype="multipart/form-data"` in forms that handle file uploads
2. Handle image uploads asynchronously to prevent blocking
3. Implement proper error handling for failed uploads
4. Clean up unused images to prevent storage bloat
5. Use appropriate image sizes and formats for web display 