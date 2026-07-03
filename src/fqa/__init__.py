"""Face Quality Assessment (FQA).

Semua skor dihitung pada resolusi NATIVE (sebelum resize) untuk menghindari
bias interpolasi yang mencampur sinyal blur asli dengan bias resolusi
(terbukti empiris — lihat CLAUDE.md).

Rencana fungsi:
    compute_sub_scores(face_bgr, landmark) -> dict
        blur        : Variance of Laplacian native  (Pech-Pacheco et al., 2000)
        resolution  : rasio bbox / 112              (ad-hoc)
        illumination: Gaussian mean + minmax contrast (Zuiderveld, 1994)
        noise       : estimator Immerkær (sigma)     (Immerkær, 1996)
        pose        : yaw ratio dari 5-point landmark (ad-hoc)

    Sub-skor granular WAJIB dipertahankan terpisah — jangan di-collapse ke satu
    angka untuk routing (dibutuhkan untuk membedakan jenis degradasi).

STATUS: belum diimplementasikan di repo ini. Menunggu keputusan sumber kode
(impor kode asli vs implementasi ulang dari spesifikasi CLAUDE.md).
"""
