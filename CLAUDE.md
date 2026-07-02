

```markdown
# FotoQu — Face Clustering Pipeline (Skripsi S1)

## Konteks Proyek
Sistem pengelompokan foto otomatis berbasis identifikasi wajah untuk 
dataset foto dokumentasi organisasi. Dua kontribusi utama penelitian:
1. Face Quality Assessment (FQA) sebelum embedding extraction
2. Adaptive Enhancement berbasis hasil FQA — tanpa membuang foto 
   kualitas rendah (berbeda dari pendekatan konvensional)

Pembimbing telah menetapkan: UMAP tidak digunakan. Enhancement 
diprioritaskan dengan classical CV methods karena keterbatasan 
Compute Unit Google Colab Pro.

## Pipeline Utama
```
Dataset Foto
  → Face Detection & Alignment  (InsightFace buffalo_l / SCRFD)
  → Face Quality Assessment      (FQA, 5 komponen)
  → Adaptive Enhancement         (jika skor komposit < threshold θ)
  → ArcFace Embedding Extraction (buffalo_l, 512-dim)
  → HDBSCAN Clustering
  → Evaluasi (DBCV, Silhouette, DBI, noise rate, coverage)
```

## Komponen FQA — sudah terimplementasi

Semua dihitung di resolusi NATIVE (sebelum resize), BUKAN setelah 
resize — untuk menghindari artefak interpolasi yang mencampur sinyal 
blur asli dengan bias resolusi (terbukti empiris di sesi pengembangan).

| Komponen | Metode | Referensi |
|---|---|---|
| Blur | Variance of Laplacian (native) | Pech-Pacheco et al., 2000 |
| Resolusi | Rasio bbox / 112 (score 0-1) | Ad-hoc (belum ada sitasi) |
| Illumination | Gaussian score (mean) + minmax (contrast) | Zuiderveld, 1994 |
| Noise | Estimator Immerkær (σ) | Immerkær, 1996 |
| Pose | Yaw ratio dari 5-point landmark InsightFace | Ad-hoc (belum ada sitasi) |

### Sub-scores yang disimpan di compute_sub_scores()
```python
{
  'blur': blur_s,                     # 0-1, tinggi = bagus
  'resolution': res_s,                # 0-1, tinggi = bagus
  'illumination': illum_s,            # gabungan mean + contrast
  'noise': noise_s,                   # 0-1, tinggi = bersih (sudah dibalik)
  '_mean_brightness_raw': ...,        # piksel mentah, dibutuhkan Gamma
  '_contrast_score': ...,             # contrast ternormalisasi terpisah
  '_illum_mean_s': ...,               # Gaussian score mean, terpisah
}
```

**PENTING**: jangan collapse sub-scores ke satu angka tunggal untuk 
routing. Sub-skor granular dibutuhkan untuk membedakan jenis degradasi 
dan memilih teknik enhancement yang tepat.

## Komponen Adaptive Enhancement — sudah terimplementasi

Urutan eksekusi WAJIB dipertahankan (kausal, tidak boleh dibalik):
```
SR (Bicubic) → Denoising (NLM) → Illumination → Sharpening (Laplacian)
```
Sharpening sebelum denoising = noise ikut dikuatkan (sudah terbukti 
secara matematis di sesi pengembangan).

| Teknik | Fungsi | Trigger kondisi |
|---|---|---|
| Bicubic SR | apply_bicubic_sr() | resolution_s < 0.7 |
| NLM Denoising | apply_nlm_denoising() | noise_s < 0.6 |
| Gamma Correction | apply_gamma_correction() | illum_mean_s < 0.7 |
| CLAHE | apply_clahe() | contrast_s < 0.6 |
| Laplacian Sharpening | apply_laplacian_sharpening() | blur_s < 0.6 |

**Semua threshold di atas adalah PLACEHOLDER** — belum dikalibrasi. 
Kalibrasi final menunggu Skenario B (uji Mann-Whitney U pada dataset 
berlabel penuh, n ≥ 64 per grup).

**Bug yang sudah diperbaiki dan TIDAK BOLEH diulang**:
- Jangan resize sebelum menghitung skor blur — bias resolusi (terbukti 
  empiris, mengubah arah ranking IMG_1780 vs IMG_1807)
- Jangan gunakan skor gabungan (illum_s) sebagai gate illumination — 
  dual-gating bug menyebabkan sebagian foto tidak terenhance meski 
  seharusnya (terbukti di IMG_4781, mean=83.24 lolos gate mentah tapi 
  tidak lolos gate skor). Sekarang route_illumination dipanggil selalu.
- Jangan gunakan Haar Cascade — false-positive terbukti pada foto buram 
  (IMG_1780), false-negative pada pose ekstrem. Wajib InsightFace.
- Jangan validasi efek laplacian_sharpening dengan variance of Laplacian 
  — sirkular. Gunakan Tenengrad (Sobel) sebagai metrik independen.
- Output pipeline WAJIB 112×112 piksel (kontrak input ArcFace) terlepas 
  dari enhancement apa yang dijalankan.

## Skenario Evaluasi (Desain Ablasi)

| Skenario | Deskripsi | Tujuan |
|---|---|---|
| A | HDBSCAN saja (baseline internal) | Kontrol — bukan Rafiul |
| B | FQA scoring tanpa enhancement | Validasi korelasi FQA-noise (Mann-Whitney U), kalibrasi θ |
| C | FQA + Enhancement penuh | Kontribusi utama |

**Catatan kritis**: Rafiul memakai DBSCAN, Ade memakai HDBSCAN — 
perbandingan langsung metrik tidak valid (dua variabel berubah 
sekaligus). Rafiul hanya referensi eksternal, bukan baseline internal.

## Metrik Evaluasi

- **Primer**: DBCV (sesuai untuk HDBSCAN, tidak asumsi cluster konveks)
- **Sekunder**: Silhouette Score, DBI (untuk komparabilitas dengan Rafiul)
- **Tambahan**: Noise rate, coverage rate, waktu komputasi
- **Cluster Purity**: membutuhkan ground-truth label per wajah

**JANGAN** validasi hasil clustering dengan metrik yang sama keluarganya 
dengan mekanisme yang dievaluasi (contoh: jangan ukur efek Laplacian 
sharpening dengan variance of Laplacian).

## Environment & Stack

```
Runtime    : Google Colab Pro — Compute Unit TERBATAS
             CPU-only untuk FQA & Enhancement (ringan, O(H*W))
             GPU hanya untuk ArcFace embedding extraction (berat)
Language   : Python 3.x
Core libs  : InsightFace buffalo_l, OpenCV, NumPy, HDBSCAN,
             Scikit-Learn, FAISS, Streamlit, Pandas
Storage    : Google Drive (dataset), GitHub (code)
```

## Aturan Wajib untuk Claude Code

1. **Selalu sertakan justifikasi teknis** — rumus matematis, Big-O, 
   atau referensi paper. Tidak ada saran tanpa dasar.

2. **Pertimbangkan Compute Unit** — setiap solusi kode harus 
   menyebutkan kompleksitas dan apakah butuh GPU atau cukup CPU.

3. **Berpikir kritis** — jangan setujui pernyataan Ade jika salah 
   secara teori. Koreksi dengan bukti.

4. **Kode harus dapat dipertanggungjawabkan secara ilmiah** — ini 
   skripsi, bukan sekadar kode yang "jalan".

5. **Bahasa Indonesia** untuk respons, kecuali istilah teknis, nama 
   fungsi, nama library.

6. **Output dimensi konsisten** — semua wajah keluar dari pipeline 
   sebagai array 112×112 grayscale sebelum ArcFace.

## Status Implementasi

- [x] Face Detection (InsightFace, dengan gate det_score ≥ 0.5)
- [x] FQA: Blur, Resolusi, Illumination, Noise (tervalidasi)
- [x] FQA: Pose (terimplementasi, validasi terbatas — catat keterbatasan)
- [x] Skor komposit FQA (placeholder weights, belum dikalibrasi)
- [x] Routing enhancement (bug dual-gating sudah diperbaiki)
- [x] Semua 5 teknik enhancement (Bicubic, NLM, Gamma, CLAHE, Sharpen)
- [ ] Konstruksi dataset + ground-truth labeling (~600-900 wajah)
- [ ] Kalibrasi threshold θ dan bobot komposit (menunggu Skenario B)
- [ ] Komponen pose: validasi lebih ketat (menunggu dataset berlabel)
- [ ] Skenario A, B, C eksperimen penuh
- [ ] Evaluasi DBCV/Silhouette/DBI
- [ ] Streamlit frontend (FotoQu app)

## Literatur Utama (sudah disitasi)

- Meena, Vats, & Kumar (2022) — 5 faktor degradasi FR
- Pech-Pacheco et al. (2000) — Variance of Laplacian (blur)
- Immerkær (1996) — Fast noise variance estimation
- Zuiderveld (1994) — CLAHE
- Campello et al. (2013); McInnes et al. (2017) — HDBSCAN
- Survei FIQA ACM Computing Surveys (2022) — filosofi selective enhancement
- Rafiul Muiz K. (2025) — baseline skripsi (DBSCAN+FAISS)
```
