import { API_BASE_URL, getToken, fetchUserData } from "../api/api.js";

const token = getToken();
const postId = new URLSearchParams(window.location.search).get("id");

if (!token) {
    window.location.href = "login.html";
}

document.addEventListener("DOMContentLoaded", () => {
    initPostPage();
});

// 🔄 Initialize Page
async function initPostPage() {
    await fetchPost();
    await fetchComments();
    await fetchLikes();
    setupShareButton();
}

// 📜 Fetch Post Details
async function fetchPost() {
    try {
        const response = await fetch(`${API_BASE_URL}/articles/${postId}`);
        if (!response.ok) throw new Error("Post not found.");
        const post = await response.json();

        document.getElementById("post-title").textContent = post.title;
        document.getElementById("post-author").textContent = `By: ${post.author.username}`;
        document.getElementById("post-content").textContent = post.content;

        const userData = await fetchUserData();
        if (userData.id === post.author.id) {
            document.getElementById("post-actions").style.display = "block";
            document.getElementById("edit-post-btn").addEventListener("click", editPost);
            document.getElementById("delete-post-btn").addEventListener("click", deletePost);
        }

        setupShareLinks(post.title);
    } catch (error) {
        console.error("Error fetching post:", error);
    }
}

// 💬 Fetch Comments
async function fetchComments() {
    try {
        const response = await fetch(`${API_BASE_URL}/articles/${postId}/comments`);
        if (!response.ok) throw new Error("Failed to load comments.");
        const comments = await response.json();

        const commentsContainer = document.getElementById("comments-container");
        commentsContainer.innerHTML = "";

        const userData = await fetchUserData();

        comments.forEach(comment => {
            const commentEl = document.createElement("div");
            commentEl.classList.add("comment");
            commentEl.innerHTML = `
                <p><strong>${comment.author.username}</strong>: ${comment.content}</p>
                ${comment.author.id === userData.id ? `<button class="delete-comment-btn" data-id="${comment.id}">Delete</button>` : ""}
            `;
            commentsContainer.appendChild(commentEl);
        });

        // Attach delete event listener
        document.querySelectorAll(".delete-comment-btn").forEach(btn => {
            btn.addEventListener("click", () => deleteComment(btn.getAttribute("data-id")));
        });
    } catch (error) {
        console.error("Error fetching comments:", error);
    }
}

// ➕ Add a New Comment
document.getElementById("comment-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const commentText = document.getElementById("comment-text").value;

    try {
        const response = await fetch(`${API_BASE_URL}/articles/${postId}/comments`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ content: commentText })
        });

        if (!response.ok) throw new Error("Failed to add comment.");
        document.getElementById("comment-text").value = "";
        fetchComments();
    } catch (error) {
        console.error("Error adding comment:", error);
    }
});

// ❌ Delete a Comment
async function deleteComment(commentId) {
    if (confirm("Are you sure you want to delete this comment?")) {
        try {
            const response = await fetch(`${API_BASE_URL}/articles/${postId}/comments/${commentId}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (!response.ok) throw new Error("Failed to delete comment.");
            fetchComments();
        } catch (error) {
            console.error("Error deleting comment:", error);
        }
    }
}

// ❤️ Fetch Likes
async function fetchLikes() {
    try {
        const response = await fetch(`${API_BASE_URL}/articles/${postId}/likes`);
        if (!response.ok) throw new Error("Failed to load likes.");
        const { like_count, liked_by_user } = await response.json();

        document.getElementById("like-count").textContent = like_count;
        const likeBtn = document.getElementById("like-btn");
        likeBtn.textContent = liked_by_user ? "👎 Unlike" : "👍 Like";

        likeBtn.onclick = () => toggleLike(liked_by_user);
    } catch (error) {
        console.error("Error fetching likes:", error);
    }
}

// 👍 Like/Unlike Post
async function toggleLike(isLiked) {
    const method = isLiked ? "DELETE" : "POST";

    try {
        const response = await fetch(`${API_BASE_URL}/articles/${postId}/likes`, {
            method: method,
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) throw new Error("Failed to update like.");
        fetchLikes();
    } catch (error) {
        console.error("Error updating like:", error);
    }
}

// 📤 Share Post
function setupShareButton() {
    const shareBtn = document.getElementById("share-btn");
    shareBtn.addEventListener("click", () => {
        const postUrl = window.location.href;

        if (navigator.share) {
            navigator.share({
                title: document.getElementById("post-title").textContent,
                url: postUrl,
            })
            .then(() => console.log("Post shared successfully!"))
            .catch((error) => console.error("Error sharing post:", error));
        } else {
            navigator.clipboard.writeText(postUrl).then(() => {
                const messageEl = document.getElementById("share-message");
                messageEl.textContent = "🔗 Link copied!";
                messageEl.style.color = "green";
                setTimeout(() => (messageEl.textContent = ""), 2000);
            });
        }
    });
}

// 🔗 Setup Social Share Links
function setupShareLinks(postTitle) {
    const postURL = `${window.location.origin}/post.html?id=${postId}`;
    document.getElementById("whatsappShare").href = `https://wa.me/?text=${encodeURIComponent(postTitle + " " + postURL)}`;
    document.getElementById("twitterShare").href = `https://twitter.com/intent/tweet?url=${encodeURIComponent(postURL)}&text=${encodeURIComponent(postTitle)}`;
    document.getElementById("facebookShare").href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(postURL)}`;

    document.getElementById("copyLinkBtn").addEventListener("click", () => {
        navigator.clipboard.writeText(postURL).then(() => alert("Link copied to clipboard!"));
    });
}
