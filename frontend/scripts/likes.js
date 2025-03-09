document.addEventListener("DOMContentLoaded", function() {
    const likeButtons = document.querySelectorAll(".like-btn");

    likeButtons.forEach(button => {
        button.addEventListener("click", function() {
            const postId = this.dataset.postId;
            toggleLike(postId, this);
        });
    });
});

function toggleLike(postId, button) {
    fetch(`/api/like/${postId}`, { method: "POST" })
        .then(response => response.json())
        .then(data => {
            button.innerText = data.liked ? "❤️ Unlike" : "🤍 Like";
        });
}
