const socket = new WebSocket("ws://localhost:8000/ws");

socket.onmessage = function(event) {
    const notificationList = document.getElementById("notification-list");
    const newNotification = document.createElement("li");
    newNotification.innerText = event.data;
    notificationList.appendChild(newNotification);
};
