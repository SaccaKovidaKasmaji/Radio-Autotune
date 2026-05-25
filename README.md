## Requirements & Setup

### Cloud (sudah di-deploy, tidak perlu setup ulang)
- Backend sudah berjalan di Google Cloud Run
- Database dan Firebase sudah terkonfigurasi
- Akses web: `https://radio-api-840408387614.asia-southeast2.run.app`

### Hardware (perlu di-setup lokal)
Download manual dan taruh di folder `hardware/`:
- **rtl_fm.exe** — dari [osmocom RTL-SDR](https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr)
- **ffplay.exe** — dari [gyan.dev FFmpeg builds](https://www.gyan.dev/ffmpeg/builds/)
- **ffmpeg71.exe** — dari [BtbN FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases)
- **serviceAccountKey.json** — dari Firebase Console (tidak di-share karena keamanan)

### Driver
- Install **Zadig** untuk RTL-SDR driver: [zadig.akeo.ie](https://zadig.akeo.ie)
- Install **VB-Audio Virtual Cable**: [vb-audio.com/Cable](https://vb-audio.com/Cable/)

### Python Dependencies
```cmd
pip install firebase-admin
```

### Menjalankan Hardware
```cmd
cd hardware
python polling.py
```

### Streaming Audio (opsional)
1. Jalankan **Icecast** sebagai server streaming
2. Jalankan **BUTT** dengan input CABLE Output → server Icecast
3. Jalankan **Cloudflare Tunnel**: `cloudflared tunnel --url http://localhost:8000`
