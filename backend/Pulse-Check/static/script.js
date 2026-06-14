const API_BASE = "/monitors";

const form = document.getElementById("register-form");
const statusMsg = document.getElementById("register-status");
const tbody = document.getElementById("monitors-body");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const id = document.getElementById("id").value.trim();
  const timeout = parseInt(document.getElementById("timeout").value, 10);
  const alert_email = document.getElementById("alert_email").value.trim();

  statusMsg.textContent = "Registering...";

  try {
    const res = await fetch(API_BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, timeout, alert_email }),
    });
    const data = await res.json();

    if (res.ok) {
      statusMsg.textContent = data.message;
      form.reset();
      refreshMonitors();
    } else {
      statusMsg.textContent = `Error: ${data.detail || "Could not register monitor."}`;
    }
  } catch (err) {
    statusMsg.textContent = `Network error: ${err.message}`;
  }
});

async function sendAction(id, action) {
  try {
    const res = await fetch(`${API_BASE}/${encodeURIComponent(id)}/${action}`, {
      method: "POST",
    });
    const data = await res.json();
    if (!res.ok) {
      alert(`Error: ${data.detail || "Action failed."}`);
    }
    refreshMonitors();
  } catch (err) {
    alert(`Network error: ${err.message}`);
  }
}

async function deleteMonitor(id) {
  if (!confirm(`Delete monitor '${id}'?`)) return;
  try {
    const res = await fetch(`${API_BASE}/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
    if (!res.ok) {
      const data = await res.json();
      alert(`Error: ${data.detail || "Delete failed."}`);
    }
    refreshMonitors();
  } catch (err) {
    alert(`Network error: ${err.message}`);
  }
}

function formatTime(seconds) {
  if (seconds <= 0) return "0s";
  return `${seconds.toFixed(1)}s`;
}

async function refreshMonitors() {
  try {
    const res = await fetch(API_BASE);
    const monitors = await res.json();

    if (!monitors.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="empty">No monitors yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = monitors
      .map((m) => {
        const badgeClass = m.status; // active | paused | down
        return `
          <tr>
            <td>${m.id}</td>
            <td><span class="badge ${badgeClass}">${m.status}</span></td>
            <td>${formatTime(m.time_remaining)}</td>
            <td>${m.timeout}s</td>
            <td>${m.heartbeat_count}</td>
            <td>${m.alert_email}</td>
            <td>
              <button class="secondary" onclick="sendAction('${m.id}', 'heartbeat')">Heartbeat</button>
              <button class="secondary" onclick="sendAction('${m.id}', 'pause')" ${m.status === "down" ? "disabled" : ""}>Pause</button>
              <button class="danger" onclick="deleteMonitor('${m.id}')">Delete</button>
            </td>
          </tr>
        `;
      })
      .join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty">Failed to load monitors: ${err.message}</td></tr>`;
  }
}

// Initial load + polling
refreshMonitors();
setInterval(refreshMonitors, 1000);
