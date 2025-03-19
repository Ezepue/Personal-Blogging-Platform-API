const API_BASE_URL = "http://127.0.0.1:8000";
const token = sessionStorage.getItem("access_token");


// Redirect if not logged in
if (!token) {
    window.location.href = "login.html";
}

// Handle logout safely
document.getElementById("logoutBtn")?.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "login.html";
});

// Form submission handler
document.getElementById("create-article-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();

    // Get form elements
    const titleInput = document.getElementById("title");
    const contentInput = document.getElementById("content");
    const messageEl = document.getElementById("message");
    const submitBtn = document.getElementById("submitBtn");

    // Trim and validate inputs
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();

    if (!title || !content) {
        messageEl.textContent = "Title and content are required.";
        messageEl.style.color = "red";
        return;
    }

    try {
        // Disable submit button during request
        submitBtn.disabled = true;
        submitBtn.textContent = "Submitting...";

        const response = await fetch(`${API_BASE_URL}/articles`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ title, content })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to create article.");
        }

        messageEl.textContent = "Article created successfully!";
        messageEl.style.color = "green";

        // Clear inputs
        titleInput.value = "";
        contentInput.value = "";

        // Redirect to home after 2 seconds
        setTimeout(() => {
            window.location.href = "index.html";
        }, 2000);
    } catch (error) {
        console.error("Error:", error);
        messageEl.textContent = error.message;
        messageEl.style.color = "red";
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.textContent = "Create Article";
    }
});
