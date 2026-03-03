const API_BASE_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");
const userId = localStorage.getItem("user_id");

// 🚪 Redirect if not logged in
if (!token) {
    window.location.href = "login.html";
}

// 📩 Fetch Notifications from API
async function fetchNotifications() {
    try {
        const response = await fetch(`${API_BASE_URL}/notifications`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) throw new Error("Failed to fetch notifications");

        const notifications = await response.json();
        displayNotifications(notifications);
    } catch (error) {
        console.error("Error fetching notifications:", error);
    }
}

// 🖥️ Display Notifications
function displayNotifications(notifications) {
    const list = document.getElementById("notifications-list");
    if (!list) return;

    list.innerHTML = notifications.length ? "" : "<li>No new notifications</li>";

    notifications.forEach(notification => {
        const li = document.createElement("li");
        li.textContent = notification.message;
        list.appendChild(li);
    });
}

// 🔄 Setup WebSocket Connection
function setupWebSocket() {
    if (!userId || !token) return console.error("User ID or token missing!");

    const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${userId}?token=${token}`);

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        showNotificationPopup(data.message);
        fetchNotifications(); // Refresh list when a new notification arrives
    };

    socket.onerror = function (error) {
        console.error("WebSocket Error:", error);
    };

    socket.onclose = function () {
        console.warn("WebSocket closed, reconnecting in 5s...");
        setTimeout(setupWebSocket, 5000); // Auto-reconnect after 5 seconds
    };
}

// 🔔 Show Popup Notification
function showNotificationPopup(message) {
    const popup = document.createElement("div");
    popup.classList.add("notification-popup");
    popup.textContent = message;

    document.body.appendChild(popup);

    setTimeout(() => {
        popup.remove();
    }, 5000);
}

// 🚀 Initialize Page
document.addEventListener("DOMContentLoaded", () => {
    fetchNotifications();
    setupWebSocket();
});
