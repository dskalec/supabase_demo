-- Create a view for user display names
create or replace view user_display_names as
select 
    id as user_id,
    coalesce(
        raw_user_meta_data->>'display_name',
        email,
        'Unknown'
    ) as display_name
from auth.users;

-- Grant access to the view
grant select on user_display_names to authenticated;
grant select on user_display_names to anon;

-- Create a view for posts with user display names
create or replace view posts_with_users as
select 
    p.*,
    u.display_name
from posts p
left join user_display_names u on p.user_id = u.user_id;

-- Grant access to the view
grant select on posts_with_users to authenticated;
grant select on posts_with_users to anon;

-- Create a view for comments with user display names
create or replace view comments_with_users as
select 
    c.*,
    u.display_name
from comments c
left join user_display_names u on c.user_id = u.user_id;

-- Grant access to the view
grant select on comments_with_users to authenticated;
grant select on comments_with_users to anon; 