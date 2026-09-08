# Notebooks

Colab notebooks eksperimen (`.ipynb`).

- **Pipeline utama** (ekstraksi → FAISS/HDBSCAN → evaluasi) `NB01`–`NB05` berada di
  repo `Automatic-Photo-Clustering-System-Optimization-HDBSCAN`
  (`notebooks/eksperimen_baru/`).
- **`EXP_*`** = eksperimen terisolasi / titik pembanding (mis. enhancement
  classical vs restorasi deep learning). **Bukan** bagian rantai pipeline utama;
  sekali-jalan pada subset kecil.
- **`LABEL_*`** = alat labeling/verifikasi manusia. `LABEL_Cluster_Verification`
  memverifikasi cluster HDBSCAN NB05 (contact-sheet) dengan mekanisme merge/split,
  resumable, menghasilkan `face_labels_verified.csv` (ground-truth untuk Purity/ARI/NMI).
