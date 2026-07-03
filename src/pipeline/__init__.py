"""Integrasi pipeline: foto -> deteksi/alignment -> FQA -> enhancement -> embedding.

Rencana fungsi:
    process_photo(path, model) -> list[face_record]
        Deteksi wajah (InsightFace buffalo_l, gate det_score) + ekstraksi
        embedding ArcFace 512-dim (L2-normalized via face.normed_embedding).

    route_enhancement(face_bgr, sub_scores) -> face_112
        Terapkan teknik enhancement sesuai sub-score FQA. route_illumination
        dipanggil SELALU (hindari dual-gating bug — lihat CLAUDE.md).

STATUS: belum diimplementasikan di repo ini.
"""
