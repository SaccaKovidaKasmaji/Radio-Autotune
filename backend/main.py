import sys, traceback
try:
    from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from sqlalchemy.orm import Session
    from pydantic import BaseModel
    from typing import Optional
    import os, firebase_admin
    from firebase_admin import credentials, firestore as fs
    from database import get_db, RadioStation, init_db
    from scraper import jalankan_scraping
except Exception as e:
    print(f"IMPORT ERROR: {e}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

app = FastAPI(title="Radio Auto-Tune API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

fdb = None

class PilihStasiun(BaseModel):
    nama_stasiun: str
    frekuensi_mhz: float
    kota: str
    provinsi: str

class StasiunInput(PilihStasiun):
    format_musik: Optional[str] = None

class FrekuensiOut(BaseModel):
    nama_stasiun: str
    frekuensi_mhz: float
    kota: str

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/api/status")
def status(): return {"status": "online"}

@app.get("/api/sdr-info")
def get_sdr_info():
    kota = os.environ.get("SDR_KOTA", "Kota Bandung")
    provinsi = os.environ.get("SDR_PROVINSI", "Jawa Barat")
    return {"kota": kota, "provinsi": provinsi}

@app.get("/api/stream-url")
def get_stream_url():
    url = os.environ.get("STREAM_URL", "")
    return {"url": url}

@app.get("/api/provinsi")
def get_provinsi(db: Session=Depends(get_db)):
    rows = db.query(RadioStation.provinsi).distinct().order_by(RadioStation.provinsi).all()
    return {"data": [r[0] for r in rows]}

@app.get("/api/wilayah/{provinsi}")
def get_kota(provinsi: str, db: Session=Depends(get_db)):
    rows = db.query(RadioStation.kota).filter(RadioStation.provinsi.ilike(f"%{provinsi}%")).distinct().order_by(RadioStation.kota).all()
    if not rows: raise HTTPException(404, f"Tidak ada data untuk provinsi {provinsi}")
    return {"provinsi": provinsi, "data": [r[0] for r in rows]}

@app.get("/api/stasiun")
def get_stasiun(provinsi: Optional[str]=Query(None), kota: Optional[str]=Query(None), limit: int=Query(100), db: Session=Depends(get_db)):
    q = db.query(RadioStation)
    if provinsi: q = q.filter(RadioStation.provinsi.ilike(f"%{provinsi}%"))
    if kota: q = q.filter(RadioStation.kota.ilike(f"%{kota}%"))
    data = q.order_by(RadioStation.frekuensi_mhz).limit(limit).all()
    return {"total": len(data), "data": data}

@app.get("/api/frekuensi/{provinsi}", response_model=list[FrekuensiOut])
def get_frekuensi(provinsi: str, kota: Optional[str]=Query(None), db: Session=Depends(get_db)):
    q = db.query(RadioStation).filter(RadioStation.provinsi.ilike(f"%{provinsi}%")).order_by(RadioStation.frekuensi_mhz)
    if kota: q = q.filter(RadioStation.kota.ilike(f"%{kota}%"))
    data = q.all()
    if not data: raise HTTPException(404, f"Tidak ada data untuk {provinsi}")
    return [FrekuensiOut(nama_stasiun=s.nama_stasiun, frekuensi_mhz=s.frekuensi_mhz, kota=s.kota) for s in data]

@app.post("/api/pilih")
def pilih_stasiun(body: PilihStasiun):
    try:
        if not firebase_admin._apps:
            cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/serviceAccountKey.json")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        db = fs.client()
        db.collection("settings").document("current_settings").set(body.dict())
        return {"pesan": "Diterima", "data": body}
    except Exception as e:
        raise HTTPException(500, f"Gagal push Firebase: {str(e)}")

@app.post("/api/stasiun", status_code=201)
def tambah_stasiun(body: StasiunInput, db: Session=Depends(get_db)):
    if db.query(RadioStation).filter(RadioStation.nama_stasiun==body.nama_stasiun, RadioStation.frekuensi_mhz==body.frekuensi_mhz).first():
        raise HTTPException(409, "Stasiun sudah ada")
    s = RadioStation(**body.dict())
    db.add(s); db.commit(); db.refresh(s)
    return {"pesan": "Berhasil ditambahkan", "data": s}

@app.post("/api/scrape")
def trigger_scrape(bg: BackgroundTasks):
    bg.add_task(jalankan_scraping)
    return {"pesan": "Scraping dimulai"}

# frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
frontend_path = "/app/frontend"
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

"""
import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/status")
def status():
    return {"status": "online"}
"""
