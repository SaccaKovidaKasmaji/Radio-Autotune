const API_BASE = "";
let stasiunAktif = null;
let sdrKota = null;

async function cekStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    if (res.ok) {
      document.getElementById("status-badge").className = "badge badge-online";
      document.getElementById("status-badge").textContent = "API Online";
    }
  } catch {
    document.getElementById("status-badge").className = "badge badge-offline";
    document.getElementById("status-badge").textContent = "API Offline";
  }
}

async function muatSdrInfo() {
  try {
    const res = await fetch(`${API_BASE}/api/sdr-info`);
    const json = await res.json();
    sdrKota = json.kota;
    const el = document.getElementById("sdr-lokasi");
    if (el) el.textContent = `📡 SDR aktif di: ${json.kota}, ${json.provinsi}`;
  } catch (e) {
    console.error("Gagal muat SDR info:", e);
  }
}

async function muatProvinsi() {
  try {
    const res  = await fetch(`${API_BASE}/api/provinsi`);
    const json = await res.json();
    const sel  = document.getElementById("sel-provinsi");
    json.data.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p;
      opt.textContent = p;
      sel.appendChild(opt);
    });
  } catch (e) {
    console.error("Gagal muat provinsi:", e);
  }
}

async function muatKota() {
  const provinsi = document.getElementById("sel-provinsi").value;
  const selKota  = document.getElementById("sel-kota");
  selKota.innerHTML = '<option value="">-- Semua Kota --</option>';
  document.getElementById("stasiun-grid").innerHTML = "";
  document.getElementById("stat-section").style.display = "none";
  if (!provinsi) return;
  try {
    const res  = await fetch(`${API_BASE}/api/wilayah/${encodeURIComponent(provinsi)}`);
    const json = await res.json();
    json.data.forEach(k => {
      const opt = document.createElement("option");
      opt.value = k;
      opt.textContent = k;
      selKota.appendChild(opt);
    });
    muatStasiun();
  } catch (e) {
    console.error("Gagal muat kota:", e);
  }
}

async function muatStasiun() {
  const provinsi = document.getElementById("sel-provinsi").value;
  const kota     = document.getElementById("sel-kota").value;
  if (!provinsi) return;
  let url = `${API_BASE}/api/stasiun?provinsi=${encodeURIComponent(provinsi)}`;
  if (kota) url += `&kota=${encodeURIComponent(kota)}`;
  try {
    const res  = await fetch(url);
    const json = await res.json();
    tampilkanStasiun(json.data);
    updateStats(json.data);
  } catch (e) {
    console.error("Gagal muat stasiun:", e);
  }
}

function tampilkanStasiun(data) {
  const grid = document.getElementById("stasiun-grid");
  const ph   = document.getElementById("placeholder");
  grid.innerHTML = "";
  if (!data || data.length === 0) {
    ph.textContent = "Tidak ada stasiun ditemukan";
    ph.style.display = "block";
    return;
  }
  ph.style.display = "none";
  data.forEach(s => {
    const card = document.createElement("div");
    const bisaPlay = !sdrKota || s.kota === sdrKota;
    card.className = "stasiun-card" + (!bisaPlay ? " disabled" : "");
    if (stasiunAktif && stasiunAktif.nama_stasiun === s.nama_stasiun) {
      card.classList.add("aktif");
    }
    card.innerHTML = `
      <div class="freq">${s.frekuensi_mhz.toFixed(1)}<span class="unit"> MHz</span></div>
      <div class="nama">${s.nama_stasiun}</div>
      <div class="kota">${s.kota}</div>
      <div class="pilih-btn">${bisaPlay ? "Klik untuk pilih" : "📍 SDR tidak di area ini"}</div>
    `;
    if (bisaPlay) card.onclick = () => pilihStasiun(s);
    grid.appendChild(card);
  });
}

async function pilihStasiun(stasiun) {
  try {
    const res = await fetch(`${API_BASE}/api/pilih`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(stasiun)
    });
    if (res.ok) {
      stasiunAktif = stasiun;
      tampilkanNotif(
        `Radio sedang pindah ke ${stasiun.nama_stasiun} — ${stasiun.frekuensi_mhz.toFixed(1)} MHz`,
        "success"
      );
      const streamRes = await fetch(`${API_BASE}/api/stream-url`);
      const streamJson = await streamRes.json();
      const player = document.getElementById("audio-player");
      const label = document.getElementById("now-playing");
      if (player && streamJson.url) {
        player.src = streamJson.url + "/stream";
        player.load();
        player.play();
        label.textContent = `🎵 Sedang memutar: ${stasiun.nama_stasiun} ${stasiun.frekuensi_mhz.toFixed(1)} MHz`;
      }
      muatStasiun();
    } else {
      tampilkanNotif("Gagal mengirim ke hardware", "error");
    }
  } catch (e) {
    tampilkanNotif("Tidak bisa terhubung ke API", "error");
  }
}

function tampilkanNotif(pesan, tipe) {
  const area = document.getElementById("notif-area");
  area.innerHTML = `<div class="notif notif-${tipe}">${pesan}</div>`;
  setTimeout(() => area.innerHTML = "", 4000);
}

function updateStats(data) {
  if (!data || data.length === 0) return;
  const freqs = data.map(s => s.frekuensi_mhz);
  document.getElementById("stat-total").textContent = data.length;
  document.getElementById("stat-min").textContent   = Math.min(...freqs).toFixed(1) + " MHz";
  document.getElementById("stat-max").textContent   = Math.max(...freqs).toFixed(1) + " MHz";
  document.getElementById("stat-section").style.display = "flex";
}

async function jalankanScraping() {
  const btn = document.getElementById("btn-scrape");
  const status = document.getElementById("scrape-status");
  btn.disabled = true;
  btn.textContent = "⏳ Sedang scraping...";
  status.textContent = "Proses ini memakan waktu 3-5 menit";
  try {
    const res = await fetch(`${API_BASE}/api/scrape`, { method: "POST" });
    if (res.ok) {
      status.textContent = "✅ Scraping dimulai! Tunggu 3-5 menit lalu refresh halaman.";
    } else {
      status.textContent = "❌ Gagal memulai scraping";
    }
  } catch (e) {
    status.textContent = "❌ Tidak bisa terhubung ke API";
  }
  setTimeout(() => {
    btn.disabled = false;
    btn.textContent = "🔄 Update Data Stasiun";
  }, 10000);
}

cekStatus();
muatProvinsi();
muatSdrInfo();