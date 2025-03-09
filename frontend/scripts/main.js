// Dark Mode Toggle
document.getElementById("dark-mode-toggle").addEventListener("click", function() {
    document.body.classList.toggle("dark-mode");
});

// Search Functionality
function searchPosts() {
    const query = document.getElementById("search-input").value.toLowerCase();
    const posts = document.querySelectorAll(".post");
    
    posts.forEach(post => {
        const title = post.querySelector("h3").innerText.toLowerCase();
        post.style.display = title.includes(query) ? "block" : "none";
    });
}
