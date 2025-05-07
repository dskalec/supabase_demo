-- Insert a test user (this is just for local development)
INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at, raw_user_meta_data)
VALUES (
  'a96ea053-60dd-4ff5-85cb-e9f0e4480f5e',
  'test@example.com',
  '$2a$10$5.gHAjF7MzUFNhHJNrV8JOb8hQZxf5AZGcTgZstZhsQtxH7Mq/Aru', -- password is 'password'
  now(),
  '{"name": "Test User"}'
) ON CONFLICT DO NOTHING;

-- Insert some test posts
INSERT INTO posts (title, content, user_id)
VALUES
  ('Welcome to the Blog', 'This is our first blog post. Welcome!', 'a96ea053-60dd-4ff5-85cb-e9f0e4480f5e'),
  ('Getting Started with Supabase', 'Supabase is an amazing open source alternative to Firebase...', 'a96ea053-60dd-4ff5-85cb-e9f0e4480f5e');

-- Insert some test comments
INSERT INTO comments (content, post_id, user_id)
SELECT 
  'This is a great first post!',
  id,
  'a96ea053-60dd-4ff5-85cb-e9f0e4480f5e'
FROM posts
WHERE title = 'Welcome to the Blog'; 