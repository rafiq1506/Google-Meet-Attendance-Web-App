// ==============================================================================
// GOOGLE MEET ATTENDANCE TRACKER - CLIENT LOGIC
// ==============================================================================

let currentRecords = [];
let activeFilter = "all";

// DOM Elements
const meetingInput = document.getElementById("meetingCodeInput");
const clearBtn = document.getElementById("btnClearInput");
const durationRange = document.getElementById("minDurationRange");
const durationDisplay = document.getElementById("durationDisplay");
const btnFetch = document.getElementById("btnFetch");
const btnTestDemo = document.getElementById("btnTestDemo");
const btnDemoQuick = document.getElementById("btnDemoQuick");
const btnRecent = document.getElementById("btnRecentMeetings");
const recentDrawer = document.getElementById("recentDrawer");
const recentList = document.getElementById("recentList");
const btnCloseRecent = document.getElementById("btnCloseRecent");

const resultsSection = document.getElementById("resultsSection");
const initialState = document.getElementById("initialState");
const tableBody = document.getElementById("tableBody");
const searchInput = document.getElementById("searchInput");
const btnDownloadExcel = document.getElementById("btnDownloadExcel");
const tableCountBadge = document.getElementById("tableCountBadge");

// Metric fields
const valTotal = document.getElementById("valTotal");
const valPresent = document.getElementById("valPresent");
const valAbsent = document.getElementById("valAbsent");
const valRate = document.getElementById("valRate");
const valProgressFill = document.getElementById("valProgressFill");

// Help Modal
const btnHelp = document.getElementById("btnHelp");
const helpModal = document.getElementById("helpModal");
const btnCloseHelp = document.getElementById("btnCloseHelp");
const btnGotIt = document.getElementById("btnGotIt");

// Initialize Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  // Sync duration slider
  durationRange.addEventListener("input", (e) => {
    durationDisplay.textContent = e.target.value;
  });

  // Clear input button visibility
  meetingInput.addEventListener("input", (e) => {
    clearBtn.style.display = e.target.value.trim() ? "block" : "none";
  });

  clearBtn.addEventListener("click", () => {
    meetingInput.value = "";
    clearBtn.style.display = "none";
    meetingInput.focus();
  });

  // Action buttons
  btnFetch.addEventListener("click", () => processAttendance(false));
  btnTestDemo.addEventListener("click", () => processAttendance(true));
  btnDemoQuick.addEventListener("click", () => processAttendance(true));

  // Enter key in meeting input
  meetingInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      processAttendance(false);
    }
  });

  // Search filter
  searchInput.addEventListener("input", filterAndRenderTable);

  // Status Filter Tabs
  document.querySelectorAll(".filter-tab").forEach((tab) => {
    tab.addEventListener("click", (e) => {
      document.querySelectorAll(".filter-tab").forEach((t) => t.classList.remove("active"));
      e.target.classList.add("active");
      activeFilter = e.target.dataset.filter;
      filterAndRenderTable();
    });
  });

  // Recent meetings drawer
  btnRecent.addEventListener("click", toggleRecentMeetings);
  btnCloseRecent.addEventListener("click", () => {
    recentDrawer.style.display = "none";
  });

  // Modal events
  btnHelp.addEventListener("click", () => {
    helpModal.style.display = "flex";
  });
  btnCloseHelp.addEventListener("click", () => {
    helpModal.style.display = "none";
  });
  btnGotIt.addEventListener("click", () => {
    helpModal.style.display = "none";
  });
});

// Helper to set duration from quick marks
window.setDuration = function (mins) {
  durationRange.value = mins;
  durationDisplay.textContent = mins;
};

// Toggle & Load Recent Meetings
async function toggleRecentMeetings() {
  if (recentDrawer.style.display === "block") {
    recentDrawer.style.display = "none";
    return;
  }

  recentDrawer.style.display = "block";
  recentList.innerHTML = `<div class="loading-spinner"><i class="ri-loader-4-line ri-spin"></i> Fetching records from Google Meet...</div>`;

  try {
    const res = await fetch("/api/recent-meetings");
    const data = await res.json();

    if (!data.success) {
      recentList.innerHTML = `
        <div style="padding: 1rem; color: #f87171; font-size: 0.85rem;">
          <i class="ri-alert-line"></i> ${data.message || "Could not fetch past meetings."}
        </div>
      `;
      return;
    }

    if (!data.meetings || data.meetings.length === 0) {
      recentList.innerHTML = `<div style="padding: 1rem; color: #94a3b8; font-size: 0.85rem;">No past Google Meet records found for this account.</div>`;
      return;
    }

    recentList.innerHTML = data.meetings
      .map((m) => {
        const cleanId = m.record_id.replace("conferenceRecords/", "");
        return `
          <div class="recent-item" onclick="selectMeetingCode('${cleanId}')">
            <div>
              <div class="recent-item-title">${cleanId}</div>
              <div class="recent-item-time">Started: ${m.start_time ? new Date(m.start_time).toLocaleString() : "-"}</div>
            </div>
            <i class="ri-arrow-right-line" style="color: #6366f1;"></i>
          </div>
        `;
      })
      .join("");
  } catch (err) {
    recentList.innerHTML = `<div style="padding: 1rem; color: #f87171;">Error: ${err.message}</div>`;
  }
}

window.selectMeetingCode = function (code) {
  meetingInput.value = code;
  clearBtn.style.display = "block";
  recentDrawer.style.display = "none";
  showToast(`Selected meeting: ${code}`, "info");
};

// Process Attendance
async function processAttendance(isDemo = false) {
  const meetingCode = meetingInput.value.trim();
  const minDuration = parseFloat(durationRange.value) || 30.0;

  if (!isDemo && !meetingCode) {
    showToast("Please enter a Google Meet code or URL, or click 'Run Test (Demo)'", "error");
    meetingInput.focus();
    return;
  }

  // Loading state
  const activeBtn = isDemo ? btnTestDemo : btnFetch;
  const originalHtml = activeBtn.innerHTML;
  activeBtn.disabled = true;
  activeBtn.innerHTML = `<i class="ri-loader-4-line ri-spin"></i> <span>Processing...</span>`;

  try {
    const response = await fetch("/api/attendance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        meeting_code: isDemo ? "demo" : meetingCode,
        min_duration: minDuration,
        is_demo: isDemo
      })
    });

    const result = await response.json();

    if (!result.success) {
      showToast(result.message || "Failed to process attendance.", "error");
      return;
    }

    // Success: Populate Summary Metrics
    currentRecords = result.records || [];
    valTotal.textContent = result.summary.total;
    valPresent.textContent = result.summary.present;
    valAbsent.textContent = result.summary.absent;
    valRate.textContent = `${result.summary.attendance_rate}%`;
    valProgressFill.style.width = `${result.summary.attendance_rate}%`;

    // Download Button
    btnDownloadExcel.href = result.download_url;

    // Render Table
    filterAndRenderTable();

    // Show Results, hide placeholder
    initialState.style.display = "none";
    resultsSection.style.display = "block";
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

    showToast(`Attendance processed! ${result.summary.present} present of ${result.summary.total} attendees.`, "success");
  } catch (error) {
    showToast(`Error: ${error.message}`, "error");
  } finally {
    activeBtn.disabled = false;
    activeBtn.innerHTML = originalHtml;
  }
}

// Filter and Render Table
function filterAndRenderTable() {
  const query = searchInput.value.toLowerCase().trim();

  const filtered = currentRecords.filter((rec) => {
    // Status Filter
    if (activeFilter !== "all" && rec.status !== activeFilter) {
      return false;
    }
    // Search Query
    if (query) {
      const name = (rec.name || "").toLowerCase();
      const email = (rec.email || "").toLowerCase();
      return name.includes(query) || email.includes(query);
    }
    return true;
  });

  tableCountBadge.textContent = `${filtered.length} of ${currentRecords.length} attendees`;

  // Check if any attendee has an actual valid email (@ address)
  const hasRealEmail = currentRecords.some((r) => r.email && r.email.includes("@"));

  // Dynamically update the table headers
  const thead = document.querySelector("#attendeesTable thead");
  if (thead) {
    thead.innerHTML = `
      <tr>
        <th style="width: 50px;">#</th>
        <th class="col-name" style="min-width: 260px;">Participant Name</th>
        ${hasRealEmail ? "<th>Email</th>" : ""}
        <th>Active Duration</th>
        <th>Sessions</th>
        <th>Status</th>
        <th>Join Time</th>
        <th>Leave Time</th>
      </tr>
    `;
  }

  const colSpanCount = hasRealEmail ? 8 : 7;

  if (filtered.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="${colSpanCount}" style="text-align: center; padding: 2rem; color: #94a3b8;">
          <i class="ri-search-eye-line" style="font-size: 1.5rem; display: block; margin-bottom: 0.5rem;"></i>
          No matching participants found.
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = filtered
    .map((rec, idx) => {
      const initial = (rec.name || "?").trim().charAt(0).toUpperCase();
      const isPresent = rec.status === "Present";
      const statusBadge = isPresent
        ? `<span class="status-badge present"><i class="ri-checkbox-circle-fill"></i> Present</span>`
        : `<span class="status-badge absent"><i class="ri-close-circle-fill"></i> Absent</span>`;

      const emailTd = hasRealEmail ? `<td class="email-cell">${escapeHtml(rec.email || "-")}</td>` : "";

      return `
        <tr>
          <td style="color: #64748b; font-weight: 600;">${idx + 1}</td>
          <td class="col-name">
            <div class="name-cell">
              <span class="name-avatar">${initial}</span>
              <span>${escapeHtml(rec.name || "Unknown")}</span>
            </div>
          </td>
          ${emailTd}
          <td><span class="duration-tag">${rec.duration_minutes} min</span></td>
          <td><span class="badge-session">${rec.session_count || 1} session</span></td>
          <td>${statusBadge}</td>
          <td style="color: #94a3b8; font-size: 0.82rem; white-space: nowrap;">${formatDateTime(rec.join_time)}</td>
          <td style="color: #94a3b8; font-size: 0.82rem; white-space: nowrap;">${formatDateTime(rec.leave_time)}</td>
        </tr>
      `;
    })
    .join("");
}

// Helpers to format email and date/time cleanly
function formatDateTime(val) {
  if (!val || val === "-") return "-";
  try {
    const d = new Date(val);
    if (isNaN(d.getTime())) return val;
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
  } catch (e) {
    return val;
  }
}

function formatEmail(email) {
  if (!email || email === "-") return '<span style="color: #64748b;">-</span>';
  if (email.startsWith("users/")) {
    const id = email.replace("users/", "");
    const shortId = id.length > 8 ? `${id.slice(0, 4)}...${id.slice(-4)}` : id;
    return `<span class="badge-session" title="${escapeHtml(email)}"><i class="ri-google-fill"></i> Google ID (${shortId})</span>`;
  }
  return escapeHtml(email);
}

// Toast notification helper
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const icon =
    type === "success"
      ? '<i class="ri-checkbox-circle-fill" style="color: #10b981; font-size: 1.1rem;"></i>'
      : type === "error"
      ? '<i class="ri-error-warning-fill" style="color: #ef4444; font-size: 1.1rem;"></i>'
      : '<i class="ri-information-fill" style="color: #06b6d4; font-size: 1.1rem;"></i>';

  toast.innerHTML = `${icon} <span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// HTML escape helper
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
