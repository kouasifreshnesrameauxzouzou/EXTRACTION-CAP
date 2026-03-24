"""
╔══════════════════════════════════════════════════════════════════╗
║    NSIA VIE ASSURANCES — Extraction Polices Groupes              ║
║    Base NSIACIF · Application Actuarielle                        ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import pymssql
import io
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION PAGE
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NSIA · Extraction Polices Groupes",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# CSS — NSIA NAVY / GOLD BRANDING
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Variables couleurs NSIA ──────────────────────────────── */
:root {
    --navy:    #0D2B55;
    --navy-dk: #08193A;
    --gold:    #C9A84C;
    --gold-lt: #E8C97A;
    --cream:   #F9F5EE;
    --white:   #FFFFFF;
    --red-err: #C0392B;
    --green:   #1A7A4A;
    --border:  #D4C5A9;
    --text-dk: #1A1A2E;
    --text-md: #4A5568;
}

/* ── Reset global ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text-dk);
}
.stApp {
    background: var(--cream);
}

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--navy-dk) !important;
    border-right: 3px solid var(--gold);
}
[data-testid="stSidebar"] * {
    color: var(--cream) !important;
}
[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.08) !important;
    color: var(--cream) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] label {
    color: var(--gold-lt) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* ── En-tête bannière ─────────────────────────────────────── */
.nsia-header {
    background: linear-gradient(135deg, var(--navy-dk) 0%, var(--navy) 60%, #1A4070 100%);
    border-radius: 12px;
    padding: 32px 40px;
    margin-bottom: 28px;
    border-bottom: 4px solid var(--gold);
    position: relative;
    overflow: hidden;
}
.nsia-header::before {
    content: '';
    position: absolute;
    right: -40px; top: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(201,168,76,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.nsia-header::after {
    content: '';
    position: absolute;
    left: 30px; bottom: -30px;
    width: 120px; height: 120px;
    background: radial-gradient(circle, rgba(201,168,76,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.nsia-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--white);
    margin: 0 0 4px 0;
    line-height: 1.2;
}
.nsia-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: var(--gold-lt);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 400;
    margin: 0;
}
.gold-line {
    width: 60px; height: 3px;
    background: var(--gold);
    margin: 12px 0 16px 0;
    border-radius: 2px;
}

/* ── Cartes sections ──────────────────────────────────────── */
.card {
    background: var(--white);
    border-radius: 10px;
    padding: 28px 32px;
    margin-bottom: 20px;
    border: 1px solid var(--border);
    box-shadow: 0 2px 12px rgba(13,43,85,0.07);
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: var(--navy);
    font-weight: 600;
    margin: 0 0 6px 0;
}
.card-title span {
    color: var(--gold);
}
.card-divider {
    height: 2px;
    background: linear-gradient(90deg, var(--gold), transparent);
    margin: 10px 0 20px 0;
    border: none;
}

/* ── Badge statuts ────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.badge-ok   { background:#E8F5EE; color:#1A7A4A; border:1px solid #A8D8B9; }
.badge-err  { background:#FDECEA; color:#C0392B; border:1px solid #F5A99B; }
.badge-wait { background:#FEF9EC; color:#956A00; border:1px solid #F0D080; }

/* ── Métriques en haut ────────────────────────────────────── */
.metric-row {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
}
.metric-box {
    flex: 1;
    background: var(--navy);
    border-radius: 10px;
    padding: 20px 24px;
    border-left: 4px solid var(--gold);
    text-align: center;
}
.metric-val {
    font-family: 'Playfair Display', serif;
    font-size: 1.9rem;
    color: var(--gold);
    font-weight: 700;
    line-height: 1;
}
.metric-lbl {
    font-size: 0.75rem;
    color: rgba(249,245,238,0.7);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 4px;
}

/* ── Boutons ──────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--navy) 0%, #1A4070 100%) !important;
    color: var(--cream) !important;
    border: 2px solid var(--gold) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 10px 28px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--gold) !important;
    color: var(--navy-dk) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(201,168,76,0.35) !important;
}

/* ── Download button ──────────────────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1A7A4A 0%, #145E38 100%) !important;
    color: white !important;
    border: 2px solid #3CB371 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
    font-size: 1rem !important;
    padding: 12px !important;
}

/* ── File uploader ────────────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed var(--gold) !important;
    background: rgba(201,168,76,0.04) !important;
    border-radius: 10px !important;
}

/* ── Dataframe ────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
}

/* ── Alertes ──────────────────────────────────────────────── */
.stSuccess { border-left: 4px solid var(--green) !important; }
.stError   { border-left: 4px solid var(--red-err) !important; }
.stWarning { border-left: 4px solid var(--gold) !important; }
.stInfo    { border-left: 4px solid var(--navy) !important; }

/* ── Info template ────────────────────────────────────────── */
.template-hint {
    background: rgba(13,43,85,0.05);
    border-left: 3px solid var(--navy);
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    font-size: 0.85rem;
    color: var(--text-md);
    margin-top: 12px;
}
.template-hint code {
    background: var(--navy);
    color: var(--gold-lt);
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 0.8rem;
}

/* ── Progress ─────────────────────────────────────────────── */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--navy), var(--gold)) !important;
}

/* ── Selectbox ────────────────────────────────────────────── */
[data-baseweb="select"] {
    border-color: var(--border) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# CONSTANTES SQL
# ─────────────────────────────────────────────────────────────────
SQL_TEMPLATE = """
SELECT DISTINCT
    P.JPPOLIP_WNPLAN AS NUMERO_CONVENTION,
    P.JPPOLIP_WNUPO  AS NUMERO_POLICE,
    ISNULL(SOUSCRIPTEUR.JAIDENP_NOMTOT, 
           RTRIM(LTRIM(COALESCE(SOUSCRIPTEUR.JAIDENP_PREAD, '') + ' ' + 
                       COALESCE(SOUSCRIPTEUR.JAIDENP_NOMAD, '')))
    ) AS [NOM SOUSCRIPTEUR],
    ISNULL(ASSURE.JAIDENP_NOMTOT, 
           RTRIM(LTRIM(COALESCE(ASSURE.JAIDENP_PREAD, '') + ' ' + 
                       COALESCE(ASSURE.JAIDENP_NOMAD, '')))
    ) AS [NOM ASSURE],
    ASSURE.JAIDENP_DNAAD AS [DATE NAISSANCE ASSURE],
    S.X.value('(MTKBGC)[1]', 'nvarchar(50)') AS CAPITAUX,
    X.X.value('(DSERE)[1]',  'nvarchar(50)') AS PERIODICITE,
    dbo.periodicite_police(P.JPPOLIP_WNUPO, 'G') AS FRACTIONNEMENT
FROM SUN_COTEDIVOIRE.dbo.JPPOLIP P
LEFT JOIN SUN_COTEDIVOIRE.dbo.JAIDENP SOUSCRIPTEUR 
    ON P.JPPOLIP_WUCLI = SOUSCRIPTEUR.JAIDENP_WNUAD
LEFT JOIN SUN_COTEDIVOIRE.dbo.JAIDENP ASSURE 
    ON P.JPPOLIP_JAASSUP_WNUAD = ASSURE.JAIDENP_WNUAD
LEFT OUTER JOIN (
    SELECT JPPOLIP_WNUPO, CONVERT(XML, FICXML) AS FICXML 
    FROM SUN_COTEDIVOIRE.dbo.JPPOLIP 
    WHERE JPPOLIP_WNUPO > 0
) Z ON P.JPPOLIP_WNUPO = Z.JPPOLIP_WNUPO
OUTER APPLY Z.FICXML.nodes('//JPPOLIP') X(X)
OUTER APPLY Z.FICXML.nodes('//JPPOLIP/JAASSUP/JAGAADP') S(X)
WHERE P.JPPOLIP_WNPLAN IN ({placeholders})
ORDER BY P.JPPOLIP_WNPLAN, P.JPPOLIP_WNUPO, [NOM ASSURE]
"""

COLONNES_SORTIE = [
    "NUMERO_CONVENTION",
    "NUMERO_POLICE",
    "NOM SOUSCRIPTEUR",
    "NOM ASSURE",
    "DATE NAISSANCE ASSURE",
    "CAPITAUX",
    "PERIODICITE",
    "FRACTIONNEMENT",
]

# ─────────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────────

def get_connection(server: str, database: str, username: str, password: str) -> pymssql.Connection:
    """Établit une connexion SQL Server via pymssql."""
    # Séparer host et instance si format HOST\INSTANCE
    if "\\" in server:
        host, instance = server.split("\\", 1)
    else:
        host, instance = server, None

    return pymssql.connect(
        server=host,
        instance=instance if instance else "",
        user=username,
        password=password,
        database=database,
        timeout=60,
        login_timeout=30,
        tds_version="7.4",
    )


def read_conventions_from_excel(uploaded_file) -> list[int]:
    """
    Lit un fichier Excel et retourne la liste des numéros de convention.
    Cherche automatiquement la colonne contenant les conventions.
    """
    df = pd.read_excel(uploaded_file, dtype=str)

    # Noms de colonnes acceptés (insensible à la casse)
    candidates = [
        "numero_convention", "convention", "wnplan", "jppolip_wnplan",
        "num_convention", "n_convention", "numero convention",
    ]

    col_found = None
    for col in df.columns:
        if col.strip().lower().replace(" ", "_") in candidates:
            col_found = col
            break

    # Si pas trouvé, prendre la première colonne
    if col_found is None:
        col_found = df.columns[0]

    nums = (
        df[col_found]
        .dropna()
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", "", regex=True)
    )
    # Garder seulement les valeurs numériques
    nums = nums[nums.str.match(r"^\d+$")]
    return sorted(set(int(x) for x in nums))


def run_extraction(conn: pyodbc.Connection, conventions: list[int]) -> pd.DataFrame:
    """Exécute la requête SQL et retourne un DataFrame."""
    placeholders = ", ".join(str(c) for c in conventions)
    sql = SQL_TEMPLATE.format(placeholders=placeholders)
    df = pd.read_sql(sql, conn)
    return df


def to_excel_bytes(df: pd.DataFrame, sheet_conventions: list[int]) -> bytes:
    """Génère un fichier Excel stylisé en mémoire."""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # ── Feuille principale ─────────────────────────────────
        df.to_excel(writer, sheet_name="Extraction", index=False, startrow=3)
        wb  = writer.book
        ws  = writer.sheets["Extraction"]

        # Formats
        navy  = "#0D2B55"
        gold  = "#C9A84C"
        cream = "#F9F5EE"

        fmt_title = wb.add_format({
            "bold": True, "font_size": 14, "font_color": navy,
            "font_name": "Calibri", "bottom": 2, "bottom_color": gold,
        })
        fmt_meta = wb.add_format({
            "italic": True, "font_size": 9, "font_color": "#6B7280",
            "font_name": "Calibri",
        })
        fmt_header = wb.add_format({
            "bold": True, "font_size": 10, "font_color": "#FFFFFF",
            "bg_color": navy, "border": 1, "border_color": gold,
            "align": "center", "valign": "vcenter", "font_name": "Calibri",
            "text_wrap": True,
        })
        fmt_conv = wb.add_format({
            "font_size": 9, "font_name": "Calibri",
            "bg_color": "#E8F0FB", "border": 1, "border_color": "#D0D7E8",
            "align": "center", "num_format": "0",
        })
        fmt_police = wb.add_format({
            "font_size": 9, "font_name": "Calibri",
            "bg_color": cream, "border": 1, "border_color": "#E5E1D8",
            "bold": True, "num_format": "0",
        })
        fmt_text = wb.add_format({
            "font_size": 9, "font_name": "Calibri",
            "bg_color": cream, "border": 1, "border_color": "#E5E1D8",
        })
        fmt_date = wb.add_format({
            "font_size": 9, "font_name": "Calibri",
            "bg_color": cream, "border": 1, "border_color": "#E5E1D8",
            "num_format": "dd/mm/yyyy", "align": "center",
        })
        fmt_num = wb.add_format({
            "font_size": 9, "font_name": "Calibri",
            "bg_color": cream, "border": 1, "border_color": "#E5E1D8",
            "num_format": "#,##0", "align": "right",
        })
        fmt_alt_text = wb.add_format({
            "font_size": 9, "font_name": "Calibri",
            "bg_color": "#F3F0E9", "border": 1, "border_color": "#E5E1D8",
        })
        fmt_total_lbl = wb.add_format({
            "bold": True, "font_size": 10, "font_color": "#FFFFFF",
            "bg_color": navy, "border": 1, "border_color": gold,
            "align": "right", "font_name": "Calibri",
        })
        fmt_total_val = wb.add_format({
            "bold": True, "font_size": 10, "font_color": navy,
            "bg_color": gold, "border": 1, "border_color": navy,
            "num_format": "#,##0", "align": "center", "font_name": "Calibri",
        })

        # En-tête document
        ws.merge_range("A1:H1", "NSIA VIE ASSURANCES — Extraction Polices Groupes", fmt_title)
        ws.write(
            "A2",
            f"Extraction générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')} · "
            f"{len(sheet_conventions)} convention(s) · {len(df):,} lignes",
            fmt_meta,
        )

        # En-têtes colonnes (row 3 = index 3)
        for col_idx, col_name in enumerate(df.columns):
            ws.write(3, col_idx, col_name, fmt_header)

        # Données avec alternance de couleurs
        for row_idx, row in enumerate(df.itertuples(index=False), start=4):
            is_alt = (row_idx % 2 == 1)
            fmt_t = fmt_alt_text if is_alt else fmt_text

            # col 0 : NUMERO_CONVENTION
            ws.write(row_idx, 0, row[0], fmt_conv)
            # col 1 : NUMERO_POLICE
            ws.write(row_idx, 1, row[1], fmt_police)
            # col 2 : NOM SOUSCRIPTEUR
            ws.write(row_idx, 2, row[2] or "", fmt_t)
            # col 3 : NOM ASSURE
            ws.write(row_idx, 3, row[3] or "", fmt_t)
            # col 4 : DATE NAISSANCE
            val_date = row[4]
            if val_date and str(val_date).isdigit() and len(str(val_date)) == 8:
                s = str(val_date)
                ws.write(row_idx, 4, f"{s[6:8]}/{s[4:6]}/{s[0:4]}", fmt_t)
            else:
                ws.write(row_idx, 4, str(val_date) if val_date else "", fmt_date)
            # col 5 : CAPITAUX
            try:
                ws.write(row_idx, 5, float(row[5]) if row[5] else "", fmt_num)
            except (ValueError, TypeError):
                ws.write(row_idx, 5, row[5] or "", fmt_t)
            # col 6 : PERIODICITE
            ws.write(row_idx, 6, row[6] or "", fmt_t)
            # col 7 : FRACTIONNEMENT
            ws.write(row_idx, 7, row[7] or "", fmt_t)

        # Ligne TOTAL
        total_row = 4 + len(df)
        ws.merge_range(total_row, 0, total_row, 6, f"TOTAL — {len(df):,} lignes extraites", fmt_total_lbl)
        ws.write(total_row, 7, len(df), fmt_total_val)

        # Largeurs colonnes
        ws.set_column(0, 0, 20)   # NUMERO_CONVENTION
        ws.set_column(1, 1, 16)   # NUMERO_POLICE
        ws.set_column(2, 3, 32)   # NOM SOUSCRIPTEUR / ASSURE
        ws.set_column(4, 4, 18)   # DATE NAISSANCE
        ws.set_column(5, 5, 16)   # CAPITAUX
        ws.set_column(6, 6, 14)   # PERIODICITE
        ws.set_column(7, 7, 16)   # FRACTIONNEMENT
        ws.set_row(3, 32)         # Hauteur en-têtes

        # ── Feuille métadonnées ────────────────────────────────
        ws_meta = wb.add_worksheet("Conventions")
        fmt_m_hdr = wb.add_format({
            "bold": True, "bg_color": navy, "font_color": "#FFFFFF",
            "border": 1, "border_color": gold, "font_name": "Calibri",
        })
        fmt_m_row = wb.add_format({
            "bg_color": cream, "border": 1, "border_color": "#E0DCd0",
            "num_format": "0", "font_name": "Calibri",
        })
        ws_meta.write(0, 0, "NUMERO_CONVENTION", fmt_m_hdr)
        ws_meta.write(0, 1, "STATUT", fmt_m_hdr)
        ws_meta.set_column(0, 0, 22)
        ws_meta.set_column(1, 1, 18)
        found_convs = set(df["NUMERO_CONVENTION"].unique()) if "NUMERO_CONVENTION" in df.columns else set()
        for i, conv in enumerate(sheet_conventions, start=1):
            statut = "✓ Données trouvées" if conv in found_convs else "⚠ Aucune donnée"
            ws_meta.write(i, 0, conv, fmt_m_row)
            ws_meta.write(i, 1, statut, fmt_m_row)

    return output.getvalue()


# ─────────────────────────────────────────────────────────────────
# SIDEBAR — CONFIGURATION CONNEXION
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
        <div style='font-family: Playfair Display, serif; font-size:1.3rem; 
                    color:#C9A84C; font-weight:700; letter-spacing:0.05em;'>
            NSIA VIE
        </div>
        <div style='font-size:0.7rem; color:rgba(249,245,238,0.55); 
                    letter-spacing:0.12em; text-transform:uppercase; margin-top:2px;'>
            Outil Actuariel
        </div>
    </div>
    <hr style='border-color: rgba(201,168,76,0.3); margin: 8px 0 20px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("**🔌 Connexion SQL Server**")

    server   = st.text_input("Serveur",     value="10.8.3.9\\SUNCOTEDIVOIRE")
    database = st.text_input("Base",        value="SUN_COTEDIVOIRE")
    username = st.text_input("Identifiant", value="reportdata")
    password = st.text_input("Mot de passe", value="reportdata$2025", type="password")

    st.markdown("<hr style='border-color: rgba(201,168,76,0.2); margin: 16px 0;'>", unsafe_allow_html=True)

    # Test de connexion
    if st.button("🔗 Tester la connexion", use_container_width=True):
        if not all([server, database, username, password]):
            st.warning("Remplir tous les champs.")
        else:
            try:
                with st.spinner("Connexion..."):
                    conn = get_connection(server, database, username, password)
                    conn.close()
                st.success("✅ Connexion réussie !")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

    st.markdown("""
    <div style='margin-top:24px; padding:14px; background:rgba(255,255,255,0.05); 
                border-radius:8px; border:1px solid rgba(201,168,76,0.2);'>
        <div style='font-size:0.72rem; color:rgba(249,245,238,0.55); 
                    letter-spacing:0.06em; text-transform:uppercase; margin-bottom:8px;'>
            Format Excel attendu
        </div>
        <div style='font-size:0.8rem; color:rgba(249,245,238,0.8); line-height:1.6;'>
            Colonne <code style='background:rgba(201,168,76,0.2); 
            padding:1px 5px; border-radius:3px;'>NUMERO_CONVENTION</code><br>
            contenant les N° de convention<br>
            (un par ligne)
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top:16px; font-size:0.72rem; 
                color:rgba(249,245,238,0.35); text-align:center; line-height:1.8;'>
        10.8.3.9\\SUNCOTEDIVOIRE<br>
        SUN_COTEDIVOIRE · dbo<br>
        JPPOLIP · JAIDENP<br>
        v1.0 — 2026
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# BANNIÈRE PRINCIPALE
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nsia-header">
    <p class="nsia-subtitle">NSIA Vie Assurances · SUN_COTEDIVOIRE</p>
    <div class="gold-line"></div>
    <h1 class="nsia-title">Extraction Polices Groupes</h1>
    <p style="color:rgba(249,245,238,0.65); font-size:0.88rem; margin:10px 0 0 0; 
              font-family:'DM Sans',sans-serif; font-weight:300;">
        Importez votre liste de conventions → extraction automatique → export Excel stylisé
    </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ÉTAPE 1 — IMPORT DU FICHIER EXCEL
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="card">
    <p class="card-title">📁 Étape 1 — <span>Import de la liste des conventions</span></p>
    <hr class="card-divider">
</div>
""", unsafe_allow_html=True)

col_up, col_hint = st.columns([3, 2])

with col_up:
    uploaded_file = st.file_uploader(
        "Déposer le fichier Excel des numéros de convention",
        type=["xlsx", "xls"],
        help="Le fichier doit contenir une colonne nommée NUMERO_CONVENTION (ou similaire).",
        label_visibility="collapsed",
    )

with col_hint:
    st.markdown("""
    <div class="template-hint">
        <b>Format attendu :</b><br>
        Première ligne = en-tête<br>
        Colonne <code>NUMERO_CONVENTION</code><br>
        Valeurs numériques entières<br><br>
        <i>Si colonne absente, la 1ère colonne est utilisée.</i>
    </div>
    """, unsafe_allow_html=True)

    # Bouton téléchargement template
    template_df = pd.DataFrame({"NUMERO_CONVENTION": [6120368, 5100061, 6400047, 6120371]})
    template_bytes = io.BytesIO()
    template_df.to_excel(template_bytes, index=False)
    st.download_button(
        label="⬇ Télécharger le template Excel",
        data=template_bytes.getvalue(),
        file_name="template_conventions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

# ─────────────────────────────────────────────────────────────────
# TRAITEMENT FICHIER IMPORTÉ
# ─────────────────────────────────────────────────────────────────
conventions = []

if uploaded_file:
    try:
        conventions = read_conventions_from_excel(uploaded_file)

        if not conventions:
            st.error("⚠ Aucun numéro de convention valide trouvé dans le fichier.")
        else:
            # Métriques
            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-box">
                    <div class="metric-val">{len(conventions)}</div>
                    <div class="metric-lbl">Convention(s) chargée(s)</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">{min(conventions):,}</div>
                    <div class="metric-lbl">N° min</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">{max(conventions):,}</div>
                    <div class="metric-lbl">N° max</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Affichage liste
            with st.expander(f"📋 Voir les {len(conventions)} conventions chargées", expanded=False):
                conv_df = pd.DataFrame({"NUMERO_CONVENTION": conventions})
                st.dataframe(conv_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"❌ Erreur lecture du fichier : {e}")


# ─────────────────────────────────────────────────────────────────
# ÉTAPE 2 — APERÇU SQL GÉNÉRÉ
# ─────────────────────────────────────────────────────────────────
if conventions:
    with st.expander("🔍 Aperçu de la requête SQL générée", expanded=False):
        placeholders = ", ".join(str(c) for c in conventions)
        apercu_sql = SQL_TEMPLATE.format(placeholders=placeholders)
        st.code(apercu_sql, language="sql")


# ─────────────────────────────────────────────────────────────────
# ÉTAPE 3 — LANCEMENT DE L'EXTRACTION
# ─────────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <p class="card-title">⚙️ Étape 2 — <span>Lancement de l'extraction</span></p>
    <hr class="card-divider">
</div>
""", unsafe_allow_html=True)

col_btn, col_info = st.columns([2, 3])

with col_btn:
    can_run = bool(conventions and server and database and username and password)
    run_btn = st.button(
        "🚀  Lancer l'extraction SQL",
        disabled=not can_run,
        use_container_width=True,
        type="primary",
    )
    if not can_run and conventions:
        st.caption("⚠ Complétez la connexion SQL Server dans la barre latérale.")

with col_info:
    if can_run:
        st.markdown(f"""
        <div class="template-hint">
            <b>Prêt à extraire :</b><br>
            🏦 Serveur : <code>{server}</code><br>
            🗄️ Base : <code>SUN_COTEDIVOIRE.dbo</code><br>
            📋 {len(conventions)} convention(s) dans le filtre <code>IN(...)</code>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# EXÉCUTION & RÉSULTATS
# ─────────────────────────────────────────────────────────────────
if run_btn:
    progress_bar = st.progress(0, text="Initialisation de la connexion...")

    try:
        # Connexion
        progress_bar.progress(15, text="Connexion au serveur SQL...")
        conn = get_connection(server, database, username, password)

        # Exécution SQL
        progress_bar.progress(40, text="Exécution de la requête SQL (peut prendre plusieurs secondes)...")
        df_result = run_extraction(conn, conventions)
        conn.close()

        progress_bar.progress(75, text="Génération du fichier Excel...")

        # Export Excel
        excel_bytes = to_excel_bytes(df_result, conventions)
        progress_bar.progress(100, text="Extraction terminée !")

        # Sauvegarde dans session state
        st.session_state["df_result"]    = df_result
        st.session_state["excel_bytes"]  = excel_bytes
        st.session_state["conventions"]  = conventions
        st.session_state["run_done"]     = True

    except Exception as e:
        progress_bar.empty()
        st.error(f"❌ Erreur lors de l'extraction : {e}")
        st.session_state["run_done"] = False


# ─────────────────────────────────────────────────────────────────
# AFFICHAGE RÉSULTATS (persistant)
# ─────────────────────────────────────────────────────────────────
if st.session_state.get("run_done") and "df_result" in st.session_state:
    df_result   = st.session_state["df_result"]
    excel_bytes = st.session_state["excel_bytes"]
    convs_used  = st.session_state["conventions"]

    st.success(f"✅ Extraction réussie ! **{len(df_result):,} lignes** récupérées pour **{len(convs_used)} convention(s)**.")

    # ── Métriques résultats ──────────────────────────────────────
    n_polices = df_result["NUMERO_POLICE"].nunique() if "NUMERO_POLICE" in df_result.columns else 0
    n_convs_r = df_result["NUMERO_CONVENTION"].nunique() if "NUMERO_CONVENTION" in df_result.columns else 0

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box">
            <div class="metric-val">{len(df_result):,}</div>
            <div class="metric-lbl">Lignes extraites</div>
        </div>
        <div class="metric-box">
            <div class="metric-val">{n_polices:,}</div>
            <div class="metric-lbl">Polices distinctes</div>
        </div>
        <div class="metric-box">
            <div class="metric-val">{n_convs_r}</div>
            <div class="metric-lbl">Conventions avec données</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Aperçu du tableau ────────────────────────────────────────
    st.markdown("""
    <div class="card">
        <p class="card-title">📊 <span>Aperçu des données</span></p>
        <hr class="card-divider">
    </div>
    """, unsafe_allow_html=True)

    n_preview = st.slider("Nombre de lignes à afficher", 5, min(200, len(df_result)), 20)
    st.dataframe(df_result.head(n_preview), use_container_width=True, hide_index=True)

    # ── Téléchargement Excel ─────────────────────────────────────
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"NSIA_Extraction_Polices_Groupes_{ts}.xlsx"

    col_dl, col_sp = st.columns([2, 3])
    with col_dl:
        st.download_button(
            label=f"⬇ Télécharger le fichier Excel ({len(df_result):,} lignes)",
            data=excel_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col_sp:
        st.markdown(f"""
        <div class="template-hint">
            📄 Fichier : <code>{filename}</code><br>
            📋 2 onglets : <b>Extraction</b> (données) + <b>Conventions</b> (statut par convention)<br>
            🎨 Mise en page aux couleurs NSIA navy/or
        </div>
        """, unsafe_allow_html=True)
