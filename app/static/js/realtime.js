// Initialize Supabase client
const supabase = window.supabase.createClient(
  'http://127.0.0.1:54321',  // Supabase local development URL
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
);

// Real-time comment updates
function setupRealtimeComments(postId) {
  const commentsContainer = document.getElementById('comments-container');
  if (!commentsContainer) return;

  console.log('Setting up comments subscription for post:', postId);

  // Subscribe to new comments
  const commentsSubscription = supabase
    .channel(`comments-${postId}`)
    .on(
      'postgres_changes',
      {
        event: '*',  // Listen to all events
        schema: 'public',
        table: 'comments',
        filter: `post_id=eq.${postId}`
      },
      async (payload) => {
        console.log('Comment change received:', payload);
        if (payload.eventType === 'INSERT') {
          // Fetch the full comment data
          const { data: comment, error } = await supabase
            .from('comments')
            .select('id, content, created_at')
            .eq('id', payload.new.id)
            .single();
            
          if (error) {
            console.error('Error fetching comment details:', error);
            return;
          }
          
          const commentHtml = createCommentHtml(comment);
          commentsContainer.insertAdjacentHTML('beforeend', commentHtml);
          updateCommentCount();
        } else if (payload.eventType === 'DELETE') {
          const commentId = payload.old.id;
          const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
          if (commentElement) {
            commentElement.remove();
            updateCommentCount();
          }
        }
      }
    )
    .subscribe((status) => {
      console.log('Comments subscription status:', status);
      if (status === 'SUBSCRIBED') {
        console.log('Successfully subscribed to comments');
      } else if (status === 'CHANNEL_ERROR') {
        console.error('Error subscribing to comments');
      }
    });

  // Update comment count
  function updateCommentCount() {
    const count = commentsContainer.querySelectorAll('.comment').length;
    const countElement = document.getElementById('comment-count');
    if (countElement) {
      countElement.textContent = count;
    }
  }

  // Create HTML for a new comment
  function createCommentHtml(comment) {
    const date = new Date(comment.created_at);
    const formattedDate = date.toISOString().split('T')[0];  // Format as YYYY-MM-DD
    return `
<div class="card mb-3 comment" data-comment-id="${comment.id}">
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <small class="text-muted">${formattedDate}</small>
        </div>
        <p class="card-text">${comment.content}</p>
        ${comment.user_id === currentUserId ? `
        <div class="d-flex justify-content-end">
            <form action="/blog/posts/${postId}/comments/${comment.id}/delete" method="post" class="d-inline">
                <button type="submit" class="btn btn-sm btn-danger">Delete</button>
            </form>
        </div>
        ` : ''}
    </div>
</div>`;
  }
}

// Real-time post view tracking
function setupPostViewTracking(postId) {
  if (!postId) return;

  console.log('Setting up view tracking for post:', postId);

  // Subscribe to view count updates
  const viewSubscription = supabase
    .channel(`post-views-${postId}`)
    .on(
      'postgres_changes',
      {
        event: '*',  // Listen to all events
        schema: 'public',
        table: 'posts',
        filter: `id=eq.${postId}`
      },
      (payload) => {
        console.log('Post change received:', payload);
        if (payload.eventType === 'UPDATE') {
          const viewCount = payload.new.view_count;
          const viewCountElement = document.getElementById('view-count');
          if (viewCountElement) {
            viewCountElement.textContent = viewCount;
          }
        }
      }
    )
    .subscribe((status) => {
      console.log('View count subscription status:', status);
      if (status === 'SUBSCRIBED') {
        console.log('Successfully subscribed to view count updates');
      } else if (status === 'CHANNEL_ERROR') {
        console.error('Error subscribing to view count updates');
      }
    });
}

// Initialize real-time features when the page loads
document.addEventListener('DOMContentLoaded', () => {
  const postId = document.querySelector('[data-post-id]')?.dataset.postId;
  if (postId) {
    console.log('Setting up real-time features for post:', postId);
    setupRealtimeComments(postId);
    setupPostViewTracking(postId);
  }
}); 