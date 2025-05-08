-- Add a view_count column to posts
alter table posts add column view_count integer default 0;

-- Create a table to track post views
create table post_views (
  id uuid default uuid_generate_v4() primary key,
  post_id uuid references posts on delete cascade not null,
  user_id uuid references auth.users,
  viewed_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS on post_views
alter table post_views enable row level security;

-- Allow anyone to insert view records
create policy "Anyone can record post views"
  on post_views for insert
  with check (true);

-- Allow anyone to read view records
create policy "Anyone can read post views"
  on post_views for select
  using (true);

-- Create a function to increment view count
create or replace function increment_view_count()
returns trigger as $$
begin
  update posts
  set view_count = view_count + 1
  where id = NEW.post_id;
  return NEW;
end;
$$ language plpgsql security definer;

-- Create a trigger to increment view count on post view
create trigger increment_post_view_count
  after insert on post_views
  for each row
  execute function increment_view_count();

-- Drop and recreate the posts_with_users view to include view_count
drop view if exists posts_with_users;
create view posts_with_users as
select 
    p.*,
    u.display_name
from posts p
left join user_display_names u on p.user_id = u.user_id;

-- Drop existing real-time configuration
drop publication if exists supabase_realtime;

-- Create a new publication for real-time
create publication supabase_realtime;

-- Enable real-time for all tables
alter publication supabase_realtime add table posts;
alter publication supabase_realtime add table comments;
alter publication supabase_realtime add table post_views;

-- Grant necessary permissions
grant usage on schema public to anon, authenticated;
grant all on all tables in schema public to anon, authenticated;
grant all on all sequences in schema public to anon, authenticated;
grant all on all functions in schema public to anon, authenticated; 