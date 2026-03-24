import streamlit as st
import pandas as pd
import pyodbc
import io
from datetime import datetime

st.set_page_config(page_title="NSIA · Extraction Polices Groupes", page_icon="🏦", layout="centered")

st.title("🏦 Extraction Polices Groupes")
st.markdown("Connexion NSIACIF → Exécution SQL → Export Excel")
st.divider()

with st.expander("⚙️ Paramètres de connexion", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        server   = st.text_input("Serveur",      value="10.8.3.9")
        database = st.text_input("Base",         value="SUN_COTEDIVOIRE")
    with col2:
        username = st.text_input("Utilisateur",  value="reportdata")
        password = st.text_input("Mot de passe", value="reportdata$2025", type="password")

st.subheader("📋 Numéros de convention")
uploaded = st.file_uploader("Importer un fichier Excel avec les conventions", type=["xlsx", "xls"])

conventions = []
if uploaded:
    df_conv = pd.read_excel(uploaded, dtype=str)
    col = df_conv.columns[0]
    conventions = [int(x) for x in df_conv[col].dropna() if str(x).strip().isdigit()]
    st.success(f"✅ {len(conventions)} convention(s) : {conventions}")
else:
    raw = st.text_area(
        "Ou saisir les numéros manuellement (un par ligne)",
        value="6120368\n5100061\n6400047\n6120371",
        height=120,
    )
    conventions = [int(x.strip()) for x in raw.splitlines() if x.strip().isdigit()]
    st.info(f"ℹ️ {len(conventions)} convention(s) saisie(s)")

st.divider()
if st.button("🚀 Lancer l'extraction", type="primary", use_container_width=True, disabled=not conventions):
    placeholders = ", ".join(str(c) for c in conventions)
    SQL = f"""
    SELECT DISTINCT
        P.JPPOLIP_WNPLAN AS NUMERO_CONVENTION,
        P.JPPOLIP_WNUPO  AS NUMERO_POLICE,
        ISNULL(SOUSCRIPTEUR.JAIDENP_NOMTOT,
               RTRIM(LTRIM(COALESCE(SOUSCRIPTEUR.JAIDENP_PREAD,'') + ' ' +
                           COALESCE(SOUSCRIPTEUR.JAIDENP_NOMAD,'')))
        ) AS NOM_SOUSCRIPTEUR,
        ISNULL(ASSURE.JAIDENP_NOMTOT,
               RTRIM(LTRIM(COALESCE(ASSURE.JAIDENP_PREAD,'') + ' ' +
                           COALESCE(ASSURE.JAIDENP_NOMAD,'')))
        ) AS NOM_ASSURE,
        ASSURE.JAIDENP_DNAAD  AS DATE_NAISSANCE_ASSURE,
        S.X.value('(MTKBGC)[1]','nvarchar(50)') AS CAPITAUX,
        X.X.value('(DSERE)[1]', 'nvarchar(50)') AS PERIODICITE,
        dbo.periodicite_police(P.JPPOLIP_WNUPO,'G') AS FRACTIONNEMENT
    FROM SUN_COTEDIVOIRE.dbo.JPPOLIP P
    LEFT JOIN SUN_COTEDIVOIRE.dbo.JAIDENP SOUSCRIPTEUR
        ON P.JPPOLIP_WUCLI = SOUSCRIPTEUR.JAIDENP_WNUAD
    LEFT JOIN SUN_COTEDIVOIRE.dbo.JAIDENP ASSURE
        ON P.JPPOLIP_JAASSUP_WNUAD = ASSURE.JAIDENP_WNUAD
    LEFT OUTER JOIN (
        SELECT JPPOLIP_WNUPO, CONVERT(XML, FICXML) AS FICXML
        FROM SUN_COTEDIVOIRE.dbo.JPPOLIP WHERE JPPOLIP_WNUPO > 0
    ) Z ON P.JPPOLIP_WNUPO = Z.JPPOLIP_WNUPO
    OUTER APPLY Z.FICXML.nodes('//JPPOLIP') X(X)
    OUTER APPLY Z.FICXML.nodes('//JPPOLIP/JAASSUP/JAGAADP') S(X)
    WHERE P.JPPOLIP_WNPLAN IN ({placeholders})
    ORDER BY P.JPPOLIP_WNPLAN, P.JPPOLIP_WNUPO, NOM_ASSURE
    """
    try:
        with st.spinner("Connexion à SQL Server via FreeTDS..."):
            conn_str = (
                "DRIVER={FreeTDS};"
                f"SERVER={server};"
                "PORT=1433;"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                "TDS_Version=7.4;"
            )
            conn = pyodbc.connect(conn_str, timeout=30)

        with st.spinner("Exécution de la requête SQL..."):
            df = pd.read_sql(SQL, conn)
            conn.close()

        if df.empty:
            st.warning("⚠️ Aucune donnée trouvée pour ces conventions.")
        else:
            st.success(f"✅ **{len(df):,} lignes** extraites — {df['NUMERO_CONVENTION'].nunique()} convention(s)")
            st.dataframe(df.head(50), use_container_width=True)

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Extraction")
                ws = writer.sheets["Extraction"]
                wb = writer.book
                hdr = wb.add_format({"bold": True, "bg_color": "#0D2B55", "font_color": "#FFFFFF", "border": 1})
                for i, c in enumerate(df.columns):
                    ws.write(0, i, c, hdr)
                    ws.set_column(i, i, max(len(c) + 4, 16))

            fname = f"NSIA_Polices_Groupes_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            st.download_button(
                label=f"⬇️ Télécharger Excel ({len(df):,} lignes)",
                data=buf.getvalue(),
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
