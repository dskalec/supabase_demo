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
          // Fetch the full comment data with display name
          const { data: comment, error } = await supabase
            .from('comments_with_users')
            .select('id, content, created_at, user_id, display_name')
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
        <div class="d-flex justify-content-between align-items-start">
            <p class="card-text">${comment.content}</p>
            ${comment.user_id === currentUserId ? `
            <div class="btn-group">
                <button type="button" class="btn btn-sm btn-outline-primary" 
                        onclick="editComment('${comment.id}', '${comment.content}')">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16">
                        <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                    </svg>
                    Edit
                </button>
                <form method="POST" action="/blog/comments/${comment.id}/delete" class="d-inline"
                      onsubmit="return confirm('Are you sure you want to delete this comment?');">
                    <button type="submit" class="btn btn-sm btn-outline-danger">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                            <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                        </svg>
                        Delete
                    </button>
                </form>
            </div>
            ` : ''}
        </div>
        <p class="card-subtitle text-muted">
            Posted by ${comment.display_name || 'Unknown'} on ${formattedDate}
        </p>
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