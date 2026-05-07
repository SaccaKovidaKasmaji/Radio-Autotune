import firebase_admin
from firebase_admin import credentials, firestore
import os

_db = None

def get_firestore():
    global _db
    if _db is None:
        if not firebase_admin._apps:
            cred_path = os.environ.get(
                "GOOGLE_APPLICATION_CREDENTIALS",
                "serviceAccountKey.json"
            )
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db

def push_frekuensi(nama_stasiun, frekuensi_mhz, kota, provinsi):
    db = get_firestore()
    db.collection("settings").document("current_settings").set({
        "nama_stasiun":  nama_stasiun,
        "frekuensi_mhz": frekuensi_mhz,
        "kota":          kota,
        "provinsi":      provinsi,
        "updated_at":    firestore.SERVER_TIMESTAMP
    })
    print(f"Firestore diupdate: {nama_stasiun} {frekuensi_mhz} MHz")