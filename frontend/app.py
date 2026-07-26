import json
import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

SUPPORTED_FORMATS = ["mp3", "mp4", "wav", "m4a", "ogg", "webm", "flac", "mpeg", "mpga"]
MAX_SIZE_MB = 25

LANGUAGES = {
    "Auto-détection": "",
    "Français": "fr",
    "English": "en",
    "Español": "es",
    "Deutsch": "de",
    "Italiano": "it",
    "Português": "pt",
    "日本語": "ja",
    "中文": "zh",
    "العربية": "ar",
}

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Meeting Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    #MainMenu, header, footer { visibility: hidden; }

    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 18px;
        padding: 2.6rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    .hero h1 { font-size: 2.5rem; margin: 0 0 .45rem; font-weight: 900; letter-spacing: -.5px; }
    .hero p  { font-size: 1.05rem; opacity: .85; margin: 0; }

    /* Pipeline steps */
    .pipeline {
        display: flex;
        justify-content: center;
        gap: 0;
        margin: 1.2rem 0 2rem;
    }
    .step {
        display: flex;
        align-items: center;
        gap: .5rem;
        padding: .5rem 1.2rem;
        border-radius: 20px;
        font-size: .88rem;
        font-weight: 600;
        background: #f1f5f9;
        color: #64748b;
    }
    .step-active { background: #e0f2fe; color: #0369a1; }
    .step-done   { background: #dcfce7; color: #15803d; }
    .step-arrow  { color: #cbd5e1; font-size: 1.1rem; padding: 0 .3rem; }

    /* Cards */
    .card {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
    }
    .card h3 {
        margin: 0 0 1rem;
        font-size: .85rem;
        color: #0f172a;
        text-transform: uppercase;
        letter-spacing: .7px;
        font-weight: 700;
    }

    /* Summary box */
    .summary-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 4px solid #0ea5e9;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        font-size: 1rem;
        color: #0f172a;
        line-height: 1.6;
        margin-bottom: 1.4rem;
    }

    /* Key point list */
    .kp-item {
        display: flex;
        align-items: flex-start;
        gap: .7rem;
        padding: .55rem 0;
        border-bottom: 1px solid #f8fafc;
        font-size: .95rem;
        color: #1e293b;
    }
    .kp-item:last-child { border-bottom: none; }
    .kp-num {
        min-width: 24px;
        height: 24px;
        background: #0f3460;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: .75rem;
        font-weight: 700;
        flex-shrink: 0;
        margin-top: .05rem;
    }

    /* Decision card */
    .decision-card {
        background: #fafaf9;
        border: 1px solid #e7e5e4;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: .9rem 1rem;
        margin-bottom: .7rem;
    }
    .decision-text { font-weight: 600; color: #1c1917; font-size: .95rem; }
    .decision-ctx  { color: #78716c; font-size: .85rem; margin-top: .3rem; }

    /* Priority badges */
    .badge {
        display: inline-block;
        padding: .2rem .65rem;
        border-radius: 10px;
        font-size: .75rem;
        font-weight: 700;
        letter-spacing: .3px;
    }
    .badge-high   { background: #fee2e2; color: #b91c1c; }
    .badge-medium { background: #fef9c3; color: #854d0e; }
    .badge-low    { background: #dcfce7; color: #15803d; }

    /* Sentiment badge */
    .sent-positive { background: #dcfce7; color: #15803d; }
    .sent-neutral  { background: #f1f5f9; color: #475569; }
    .sent-mixed    { background: #fef9c3; color: #854d0e; }
    .sent-tense    { background: #fee2e2; color: #b91c1c; }

    /* Meta chips */
    .meta-chip {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        border-radius: 8px;
        padding: .3rem .8rem;
        font-size: .82rem;
        font-weight: 500;
        margin: .2rem .1rem;
    }

    /* Transcript */
    .transcript-box {
        background: #1e1e2e;
        color: #cdd6f4;
        border-radius: 12px;
        padding: 1.4rem;
        font-family: 'Courier New', monospace;
        font-size: .87rem;
        line-height: 1.7;
        max-height: 500px;
        overflow-y: auto;
        white-space: pre-wrap;
    }

    /* Progress */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0f3460, #0ea5e9);
        border-radius: 8px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _priority_badge(priority: str) -> str:
    cls = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}.get(priority, "badge-medium")
    labels = {"high": "Haute", "medium": "Moyenne", "low": "Basse"}
    return f'<span class="badge {cls}">{labels.get(priority, priority)}</span>'


def _sentiment_badge(sentiment: str | None) -> str:
    if not sentiment:
        return ""
    cls = f"sent-{sentiment}"
    labels = {"positive": "Positif", "neutral": "Neutre", "mixed": "Mitigé", "tense": "Tendu"}
    return f'<span class="badge {cls}">{labels.get(sentiment, sentiment)}</span>'


def _format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s" if m else f"{s}s"


def _plain_text_export(r: dict) -> str:
    m = r["meeting"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"RÉUNION : {m['title']}",
        f"Analysé le : {now}",
        f"Fichier : {r['filename']} | Durée : {_format_duration(r.get('audio_duration_seconds'))}",
        "",
        "═" * 60,
        "RÉSUMÉ EXÉCUTIF",
        "═" * 60,
        m["summary"],
        "",
    ]
    if m.get("participants"):
        lines += ["─" * 40, "PARTICIPANTS", "─" * 40]
        lines += [f"  • {p}" for p in m["participants"]]
        lines.append("")

    if m.get("topics_discussed"):
        lines += ["─" * 40, "SUJETS ABORDÉS", "─" * 40]
        lines += [f"  • {t}" for t in m["topics_discussed"]]
        lines.append("")

    if m.get("key_points"):
        lines += ["─" * 40, "POINTS CLÉS", "─" * 40]
        lines += [f"  {i+1}. {p}" for i, p in enumerate(m["key_points"])]
        lines.append("")

    if m.get("decisions"):
        lines += ["─" * 40, "DÉCISIONS PRISES", "─" * 40]
        for i, d in enumerate(m["decisions"], 1):
            lines.append(f"  {i}. {d['decision']}")
            if d.get("context"):
                lines.append(f"     Contexte : {d['context']}")
        lines.append("")

    if m.get("action_items"):
        lines += ["─" * 40, "ACTIONS À FAIRE", "─" * 40]
        for a in m["action_items"]:
            priority_map = {"high": "HAUTE", "medium": "MOY.", "low": "BASSE"}
            prio = priority_map.get(a.get("priority", "medium"), "MOY.")
            resp = a.get("responsible") or "—"
            dead = a.get("deadline") or "—"
            lines.append(f"  □ {a['task']}")
            lines.append(f"    Responsable : {resp} | Délai : {dead} | Priorité : {prio}")
        lines.append("")

    lines += [
        "═" * 60,
        "TRANSCRIPTION COMPLÈTE",
        "═" * 60,
        r["transcript"],
    ]
    return "\n".join(lines)


# ── Tab renderers ─────────────────────────────────────────────────────────────

def _render_summary_tab(m: dict, r: dict) -> None:
    # Meta chips
    chips_html = ""
    if m.get("language"):
        chips_html += f'<span class="meta-chip">🌐 {m["language"].upper()}</span>'
    chips_html += f'<span class="meta-chip">⏱ {_format_duration(r.get("audio_duration_seconds"))}</span>'
    chips_html += f'<span class="meta-chip">📝 {r["transcript_length"]:,} caractères</span>'
    chips_html += f'<span class="meta-chip">⚡ {r["processing_time"]}s</span>'
    if m.get("sentiment"):
        chips_html += _sentiment_badge(m["sentiment"])
    st.markdown(chips_html, unsafe_allow_html=True)
    st.markdown("")

    # Executive summary
    st.markdown(f'<div class="summary-box">{m["summary"]}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        kps = m.get("key_points") or []
        if kps:
            st.markdown('<div class="card"><h3>Points clés</h3>', unsafe_allow_html=True)
            items_html = "".join(
                f'<div class="kp-item"><div class="kp-num">{i+1}</div><div>{p}</div></div>'
                for i, p in enumerate(kps)
            )
            st.markdown(items_html + "</div>", unsafe_allow_html=True)
        else:
            st.info("Aucun point clé extrait.")

    with col2:
        participants = m.get("participants") or []
        topics = m.get("topics_discussed") or []

        if participants:
            st.markdown('<div class="card"><h3>Participants</h3>', unsafe_allow_html=True)
            p_html = "".join(
                f'<div style="padding:.4rem 0; border-bottom:1px solid #f1f5f9; font-size:.93rem;">'
                f'👤 {p}</div>'
                for p in participants
            )
            st.markdown(p_html + "</div>", unsafe_allow_html=True)

        if topics:
            st.markdown('<div class="card"><h3>Sujets abordés</h3>', unsafe_allow_html=True)
            t_html = "".join(
                f'<div style="padding:.35rem 0; border-bottom:1px solid #f1f5f9; font-size:.9rem;">'
                f'📌 {t}</div>'
                for t in topics
            )
            st.markdown(t_html + "</div>", unsafe_allow_html=True)


def _render_decisions_tab(m: dict) -> None:
    decisions = m.get("decisions") or []
    if not decisions:
        st.info("Aucune décision formelle identifiée dans cette réunion.")
        return

    st.markdown(f"**{len(decisions)} décision(s) prise(s)**")
    st.markdown("")
    for i, d in enumerate(decisions, 1):
        ctx = f'<div class="decision-ctx">💬 {d["context"]}</div>' if d.get("context") else ""
        st.markdown(
            f'<div class="decision-card">'
            f'<div class="decision-text">{i}. {d["decision"]}</div>'
            f'{ctx}'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_actions_tab(m: dict) -> None:
    actions = m.get("action_items") or []
    if not actions:
        st.info("Aucune action à faire identifiée dans cette réunion.")
        return

    high = [a for a in actions if a.get("priority") == "high"]
    medium = [a for a in actions if a.get("priority") == "medium"]
    low = [a for a in actions if a.get("priority") == "low"]

    col_h, col_m, col_l = st.columns(3)
    col_h.metric("Haute priorité", len(high), delta=None)
    col_m.metric("Priorité moyenne", len(medium), delta=None)
    col_l.metric("Basse priorité", len(low), delta=None)
    st.markdown("")

    # DataFrame view
    df_data = []
    for a in actions:
        df_data.append({
            "Tâche": a["task"],
            "Responsable": a.get("responsible") or "—",
            "Délai": a.get("deadline") or "—",
            "Priorité": {"high": "🔴 Haute", "medium": "🟡 Moyenne", "low": "🟢 Basse"}.get(
                a.get("priority", "medium"), "🟡 Moyenne"
            ),
        })

    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_transcript_tab(transcript: str, filename: str) -> None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{len(transcript):,} caractères transcrits**")
    with col2:
        st.download_button(
            "Télécharger .txt",
            data=transcript,
            file_name=f"{filename.rsplit('.', 1)[0]}_transcript.txt",
            mime="text/plain",
            use_container_width=True,
        )
    st.markdown(
        f'<div class="transcript-box">{transcript}</div>',
        unsafe_allow_html=True,
    )


def display_results(r: dict) -> None:
    m = r["meeting"]
    filename_stem = r.get("filename", "meeting").rsplit(".", 1)[0]

    st.markdown("---")
    st.markdown(f"## {m['title']}")

    tab_summary, tab_decisions, tab_actions, tab_transcript = st.tabs([
        f"Résumé & Points clés",
        f"Décisions ({len(m.get('decisions') or [])})",
        f"Actions ({len(m.get('action_items') or [])})",
        "Transcription",
    ])

    with tab_summary:
        _render_summary_tab(m, r)

    with tab_decisions:
        _render_decisions_tab(m)

    with tab_actions:
        _render_actions_tab(m)

    with tab_transcript:
        _render_transcript_tab(r["transcript"], r["filename"])

    # Download buttons
    st.markdown("---")
    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        st.download_button(
            "Télécharger JSON complet",
            data=json.dumps(r, ensure_ascii=False, indent=2),
            file_name=f"{filename_stem}_summary.json",
            mime="application/json",
            use_container_width=True,
            type="primary",
        )
    with dl2:
        st.download_button(
            "Télécharger rapport TXT",
            data=_plain_text_export(r),
            file_name=f"{filename_stem}_rapport.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl3:
        actions = m.get("action_items") or []
        if actions:
            df = pd.DataFrame([{
                "Tâche": a["task"],
                "Responsable": a.get("responsible") or "",
                "Délai": a.get("deadline") or "",
                "Priorité": a.get("priority", "medium"),
            } for a in actions])
            st.download_button(
                "Télécharger actions CSV",
                data=df.to_csv(index=False, encoding="utf-8-sig"),
                file_name=f"{filename_stem}_actions.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ── Main UI ───────────────────────────────────────────────────────────────────

st.markdown(
    """
<div class="hero">
    <h1>🎙️ AI Meeting Summarizer</h1>
    <p>Uploadez un enregistrement de réunion — l'IA transcrit et génère automatiquement
    points clés, décisions et actions à faire avec responsables et deadlines.</p>
</div>
""",
    unsafe_allow_html=True,
)

# Pipeline visual
st.markdown(
    """
<div class="pipeline">
    <span class="step">📤 1. Upload audio</span>
    <span class="step-arrow">→</span>
    <span class="step">🎤 2. Transcription Whisper</span>
    <span class="step-arrow">→</span>
    <span class="step">🧠 3. Analyse LLaMA 3.3</span>
    <span class="step-arrow">→</span>
    <span class="step">📋 4. Résumé structuré</span>
</div>
""",
    unsafe_allow_html=True,
)

# ── Upload + options ──────────────────────────────────────────────────────────
col_upload, col_options = st.columns([2, 1], gap="large")

with col_upload:
    st.markdown("### 🎵 Fichier audio")
    audio_file = st.file_uploader(
        "Déposez votre enregistrement ici",
        type=SUPPORTED_FORMATS,
        help=f"Formats supportés : {', '.join(SUPPORTED_FORMATS).upper()} | Max : {MAX_SIZE_MB} MB",
        label_visibility="collapsed",
    )
    if audio_file:
        size_mb = audio_file.size / (1024 * 1024)
        if size_mb > MAX_SIZE_MB:
            st.error(
                f"Fichier trop grand ({size_mb:.1f} MB). "
                f"Groq Whisper accepte jusqu'à {MAX_SIZE_MB} MB. "
                "Compressez l'audio en MP3 mono 64 kbps avec Audacity ou ffmpeg."
            )
            audio_file = None
        else:
            st.success(
                f"**{audio_file.name}** chargé — {size_mb:.1f} MB"
            )
            st.audio(audio_file)

with col_options:
    st.markdown("### ⚙️ Options")
    language_label = st.selectbox("Langue de l'enregistrement", list(LANGUAGES.keys()), index=0)
    language_code = LANGUAGES[language_label]
    st.caption("L'auto-détection fonctionne très bien pour la majorité des langues.")

# ── Analyze button ────────────────────────────────────────────────────────────
st.markdown("")
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze = st.button(
        "Analyser la réunion",
        use_container_width=True,
        type="primary",
        disabled=audio_file is None,
    )

if audio_file is None:
    st.info(
        f"Uploadez un fichier audio de réunion ({', '.join(f.upper() for f in SUPPORTED_FORMATS[:6])}…) "
        f"pour démarrer l'analyse. Taille max : {MAX_SIZE_MB} MB."
    )

# ── Analysis pipeline ─────────────────────────────────────────────────────────
if analyze and audio_file is not None:
    progress_bar = st.progress(0)
    status_msg = st.empty()

    status_msg.markdown("🎤 **Étape 1/2** — Transcription de l'audio avec Groq Whisper…")
    progress_bar.progress(15)

    try:
        form_data = {}
        if language_code:
            form_data["language"] = language_code

        response = requests.post(
            f"{BACKEND_URL}/api/analyze",
            files={"audio_file": (audio_file.name, audio_file.getvalue(), "audio/mpeg")},
            data=form_data,
            timeout=300,
        )
    except requests.exceptions.ConnectionError:
        progress_bar.empty()
        status_msg.empty()
        st.error(
            f"Impossible de joindre le backend sur `{BACKEND_URL}`. "
            "Vérifiez qu'il est démarré (`uvicorn backend.main:app --reload`)."
        )
        st.stop()
    except requests.exceptions.Timeout:
        progress_bar.empty()
        status_msg.empty()
        st.error("Le serveur a mis trop de temps à répondre (>5 min). Réessayez avec un fichier plus court.")
        st.stop()

    progress_bar.progress(75)
    status_msg.markdown("🧠 **Étape 2/2** — Analyse structurée avec LLaMA 3.3 70B…")

    if response.status_code == 200:
        progress_bar.progress(100)
        status_msg.empty()
        progress_bar.empty()
        display_results(response.json())
    else:
        progress_bar.empty()
        status_msg.empty()
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        st.error(f"Erreur {response.status_code} : {detail}")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ℹ️ À propos")
    st.markdown(
        """
**AI Meeting Summarizer** combine deux modèles Groq :

1. **Whisper Large V3 Turbo**
   Transcription audio ultra-rapide, multilingue.

2. **LLaMA 3.3 70B**
   Analyse structurée : points clés, décisions, actions.

**Formats audio supportés :**
MP3, MP4, WAV, M4A, OGG, WEBM, FLAC

**Limite :** 25 MB (contrainte Groq Whisper).
Pour les fichiers plus grands, compressez en MP3 mono :
```
ffmpeg -i input.wav -ac 1 -b:a 64k output.mp3
```
"""
    )
    st.markdown("---")
    st.markdown("**Exports disponibles :**")
    st.markdown("- JSON complet (API-ready)\n- Rapport TXT formaté\n- Actions CSV (Excel-compatible)")
    st.markdown("---")
    st.markdown(
        f"**Backend :** `{BACKEND_URL}`\n\n[Swagger UI]({BACKEND_URL}/docs)"
    )
