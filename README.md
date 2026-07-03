# FotoQu — Face Clustering Pipeline

Sistem pengelompokan foto otomatis berbasis identifikasi wajah untuk dataset
foto dokumentasi organisasi. Skripsi S1 Teknik Informatika, UIN Alauddin Makassar.

Dua kontribusi utama:
1. **Face Quality Assessment (FQA)** sebelum ekstraksi embedding.
2. **Adaptive Enhancement** berbasis hasil FQA — tanpa membuang foto kualitas
   rendah (berbeda dari pendekatan konvensional yang men-*filter* foto buruk).

Enhancement diprioritaskan dengan **classical CV** (bukan deep learning) karena
keterbatasan Compute Unit Google Colab Pro. UMAP tidak digunakan (arahan pembimbing).

## Pipeline

```
Dataset Foto
  → Face Detection & Alignment  (InsightFace buffalo_l)
  → Face Quality Assessment      (FQA, 5 komponen)
  → Adaptive Enhancement         (jika skor komposit < threshold θ)
  → ArcFace Embedding Extraction (buffalo_l, 512-dim, L2-normalized)
  → HDBSCAN Clustering
  → Evaluasi (DBCV, Silhouette, DBI, noise rate, coverage)
```

## Struktur Repositori

```
fotoqu/
├── CLAUDE.md              # konteks & spesifikasi teknis untuk Claude Code
├── README.md             # dokumen ini
├── requirements.txt      # dependency pipeline utama
├── src/
│   ├── fqa/              # Face Quality Assessment (blur, resolusi, illum, noise, pose)
│   ├── enhancement/     # Enhancement classical (Bicubic SR, NLM, Gamma, CLAHE, Laplacian)
│   └── pipeline/        # Integrasi (process_photo, route_enhancement)
├── notebooks/           # Colab notebooks eksperimen (.ipynb)
├── data/
│   ├── raw/             # foto asli — TIDAK di-push (.gitignore)
│   └── processed/       # crop wajah, embedding — TIDAK di-push (.gitignore)
└── docs/                # draft metodologi, catatan temuan
```

## Status

Modul `src/fqa`, `src/enhancement`, `src/pipeline` masih berupa scaffold —
lihat `__init__.py` masing-masing untuk rencana fungsi dan status implementasi.
Spesifikasi lengkap tiap komponen ada di `CLAUDE.md`.

## Stack

InsightFace `buffalo_l` · OpenCV · NumPy/SciPy · HDBSCAN · scikit-learn ·
FAISS · Pandas · Streamlit. Runtime: Google Colab Pro (CPU untuk FQA/enhancement,
GPU untuk ArcFace).
