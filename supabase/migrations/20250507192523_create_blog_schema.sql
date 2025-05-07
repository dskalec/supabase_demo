-- Create extensions
create extension if not exists "uuid-ossp";

-- Posts table
create table posts (
  id uuid default uuid_generate_v4() primary key,
  title text not null,
  content text not null,
  user_id uuid references auth.users not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Comments table
create table comments (
  id uuid default uuid_generate_v4() primary key,
  content text not null,
  post_id uuid references posts on delete cascade not null,
  user_id uuid references auth.users not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS
alter table posts enable row level security;
alter table comments enable row level security;

-- Policies for posts
create policy "Anyone can read posts"
  on posts for select
  using (true);

create policy "Authenticated users can create posts"
  on posts for insert
  with check (auth.role() = 'authenticated');

create policy "Users can update their own posts"
  on posts for update
  using (auth.uid() = user_id);

create policy "Users can delete their own posts"
  on posts for delete
  using (auth.uid() = user_id);

-- Policies for comments
create policy "Anyone can read comments"
  on comments for select
  using (true);

create policy "Authenticated users can create comments"
  on comments for insert
  with check (auth.role() = 'authenticated');

create policy "Users can update their own comments"
  on comments for update
  using (auth.uid() = user_id);

create policy "Users can delete their own comments"
  on comments for delete
  using (auth.uid() = user_id);

-- Create function to update updated_at timestamp
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = timezone('utc'::text, now());
  return new;
end;
$$ language plpgsql;

-- Create trigger for updating updated_at
create trigger update_posts_updated_at
  before update on posts
  for each row
  execute function update_updated_at_column();
