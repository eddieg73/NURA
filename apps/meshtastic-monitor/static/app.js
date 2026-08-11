// The Meshtastic Monitor-v2 — the Leaflet-map + the live-poll + the CSV!
const $ = (s) => document.querySelector(s);
const map = L.map("map").setView([28.5, -82.5], 8);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '© OpenStreetMap', maxZoom: 18
}).addTo(map);
const markers = {};

function fmt(t) { return t ? t.replace("T", " ").slice(0, 19) : "—"; }
function esc(s) { return String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function shortId(id) { return id ? "!" + String(id).slice(-4) : "—"; }

async function loadStats() {
  const d = await (await fetch("/api/stats")).json();
  $("#stat-packets").textContent = `packets: ${d.total_packets}`;
  $("#stat-nodes").textContent = `nodes: ${d.known_nodes}`;
  $("#stat-pos").textContent = `positions: ${d.positions}`;
  $("#stat-last").textContent = `last: ${fmt(d.last_packet)}`;
}

async function loadMessages() {
  const rows = await (await fetch("/api/messages?limit=100")).json();
  const tb = $("#msg-table tbody"); tb.innerHTML = "";
  for (const p of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${fmt(p.timestamp)}</td><td>${esc(shortId(p.sender_id))}</td>
      <td>${esc((p.text_data || "").slice(0, 80))}</td><td>${p.snr ?? "—"}</td><td>${p.rssi ?? "—"}</td>`;
    tb.appendChild(tr);
  }
}

async function loadNodes() {
  const rows = await (await fetch("/api/nodes")).json();
  const tb = $("#nodes-table tbody"); tb.innerHTML = "";
  for (const n of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${esc(n.node_id)}</td><td>${esc(n.long_name || n.short_name || "—")}</td>
      <td>${esc(n.hardware_model || "—")}</td><td>${fmt(n.last_seen)}</td><td>${n.packets_seen}</td>`;
    tb.appendChild(tr);
  }
}

async function loadPositions() {
  const rows = await (await fetch("/api/positions")).json();
  const seen = new Set();
  for (const p of rows) {
    if (p.latitude == null || p.longitude == null) continue;
    seen.add(p.sender_id);
    const latlng = [p.latitude, p.longitude];
    if (markers[p.sender_id]) {
      markers[p.sender_id].setLatLng(latlng).bindPopup(`<b>${esc(p.sender_id)}</b><br>${p.latitude.toFixed(5)}, ${p.longitude.toFixed(5)}<br>alt: ${p.altitude ?? "—"} m`).openPopup();
    } else {
      markers[p.sender_id] = L.marker(latlng).addTo(map)
        .bindPopup(`<b>${esc(p.sender_id)}</b><br>${p.latitude.toFixed(5)}, ${p.longitude.toFixed(5)}<br>alt: ${p.altitude ?? "—"} m`);
    }
  }
  for (const id of Object.keys(markers)) {
    if (!seen.has(id)) map.removeLayer(markers[id]), delete markers[id];
  }
}

async function refresh() { await Promise.all([loadStats(), loadMessages(), loadNodes(), loadPositions()]); }
$("#btn-refresh").addEventListener("click", refresh);
refresh();
setInterval(refresh, 10000); // the live-poll every 10s!
