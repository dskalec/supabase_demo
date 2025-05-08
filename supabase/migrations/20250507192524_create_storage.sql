-- Create a new storage bucket for post images
insert into storage.buckets (id, name, public)
values ('post_images', 'post_images', true);

-- Set up storage policies
create policy "Anyone can view post images"
  on storage.objects for select
  using ( bucket_id = 'post_images' );

create policy "Authenticated users can upload post images"
  on storage.objects for insert
  with check (
    bucket_id = 'post_images'
    and auth.role() = 'authenticated'
  );

create policy "Users can update their own post images"
  on storage.objects for update
  using (
    bucket_id = 'post_images'
    and auth.uid() = owner
  );

create policy "Users can delete their own post images"
  on storage.objects for delete
  using (
    bucket_id = 'post_images'
    and auth.uid() = owner
  ); 