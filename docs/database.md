# Database Schema

## Tables

### Posts
```sql
create table posts (
  id uuid default uuid_generate_v4() primary key,
  title text not null,
  content text not null,
  user_id uuid references auth.users not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

### Comments
```sql
create table comments (
  id uuid default uuid_generate_v4() primary key,
  content text not null,
  post_id uuid references posts on delete cascade not null,
  user_id uuid references auth.users not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

## Row Level Security (RLS) Policies

### Posts
- Anyone can read posts
- Only authenticated users can create posts
- Users can only update/delete their own posts

### Comments
- Anyone can read comments
- Only authenticated users can create comments
- Users can only update/delete their own comments

## Automatic Updates
- `updated_at` column in posts table is automatically updated via trigger

## Test Data
When running locally, the following test data is available:

### Test User
- Email: test@example.com
- Password: password
- User ID: a96ea053-60dd-4ff5-85cb-e9f0e4480f5e

### Sample Content
- Two blog posts by the test user
- One comment on the "Welcome to the Blog" post

## Database Migrations
All database changes are tracked in `supabase/migrations/`. The initial schema is in `20250507192523_create_blog_schema.sql`.

## Seed Data
Test data for local development is in `supabase/seed.sql`. This data is automatically loaded when running `supabase db reset`. 