"""
BTN Baleares – Rayas del Mediterráneo
Aplicación Streamlit de visualización
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Rayas en el Mediterráneo · BTN Baleares",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta ────────────────────────────────────────────────────────────────────
SPECIES_COLORS = {
    "Dasyatis pastinaca":  "#4A5568", #"#4a6d8c", # gris
    "Myliobatis aquila":   "#6699CC", #"#2e7d6b", # azul
    "Torpedo marmorata":   "#3B82F6", #"#c07c3a", # azul claro
    "Raja radula":         "#2563EB", #"#6b5b8c", # azul claro
    "Gymnura altavela":    "#C4C7CC", #"#7d1a2a", # azul intenso NO gris
    "Raja brachyura":      "#397D82", #"#3a7a50", 
    "Raja polystigma":     "#BCE8E8", #"#8a7a3a",
}
SEX_COLORS = {"M": "#40e0d0", "F": "#CC7722"}
SEX_COLORS_MUTED = {"M": "#a8d8d4", "F": "#ddc4a0"}

MONTH_ES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
            7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

PLOT_LAYOUT = dict(
    font_family="Source Sans 3, sans-serif",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=True, gridcolor="#dde4ec", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#dde4ec", zeroline=False),
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Source+Sans+3:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
h1, h2, h3 { font-family: 'Lora', serif; }

/* Sidebar: widgets en azul marino */
[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child,
[data-testid="stSidebar"] [data-baseweb="tag"] {
    border-color: #1a3a5c !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #1a3a5c !important;
    color: white !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: #1a3a5c !important;
    border-color: #1a3a5c !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[data-testid="stThumbValue"] {
    color: #1a3a5c !important;
}
[data-testid="stSidebar"] .stSlider > div > div > div > div {
    background: #1a3a5c !important;
}

.kpi-box {
    background: #dde4ec;
    border-radius: 4px;
    padding: 18px 14px;
    text-align: center;
    border: 1px solid #c8d2de;
}
.kpi-value {
    font-family: 'Lora', serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
    margin: 0;
    color: #1a1a1a;
}
.kpi-label {
    font-size: 0.78rem;
    color: #444;
    margin-top: 5px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.section-intro {
    background: #f2f5f9;
    border-left: 3px solid #4a6d8c;
    border-radius: 0 4px 4px 0;
    padding: 12px 16px;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #333;
    margin-bottom: 1.2rem;
}
.note-box {
    background: #f5f5f2;
    border-left: 3px solid #8a8a7a;
    border-radius: 0 4px 4px 0;
    padding: 9px 14px;
    font-size: 0.86rem;
    color: #555;
    margin-top: 0.7rem;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# DESCARGA DE DATOS DESDE GOOGLE DRIVE 
# ════════════════════════════════════════════════════════════════════════════

DRIVE_IDS = {
    "presence_day.csv":          "1awWlwxX6TH0eTb5jdn3XkUheblrdtgZN",
    "fish_metadata.csv":         "1cWZrwJjV2c7ld9d1UDMFjeopgl1nH53F",
    "deployment_metadata.csv":   "1H5XkGJMvJtj-LI1wCTCBkEcd-HR85Gqh" 
#    "sensor_data.csv":   	     "13onKpGwDarA-WUX91hWYrlLJgh9YVi49"
}

def ensure_data_files():
    
    try:
        import gdown
    except ImportError:
        return  # en local sin gdown, usa los ficheros locales

    base = Path(__file__).parent
    for filename, file_id in DRIVE_IDS.items():
        dest = base / filename
        if not dest.exists() and not file_id.startswith("XXX"):
            url = f"https://drive.google.com/uc?id={file_id}"
            with st.spinner(f"Descargando {filename}…"):
                gdown.download(url, str(dest), quiet=True)

ensure_data_files()


# ════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    base = Path(__file__).parent

    presence_path = base / "presence_day.csv"
    if not presence_path.exists():
        st.error("No se encuentra presence_day.csv.")
        st.stop()

    pres = pd.read_csv(presence_path, parse_dates=["interval"])
    pres["month"]   = pres["interval"].dt.month
    pres["month_s"] = pres["month"].map(MONTH_ES)
    pres["year"]    = pres["interval"].dt.year

    fish_path = base / "fish_metadata.csv"
    fish = None
    if fish_path.exists():
        raw = fish_path.read_text(encoding="utf-8", errors="replace")[:2000]
        sep = "\t" if raw.count("\t") > raw.count(",") else ","
        fish = pd.read_csv(fish_path, sep=sep)
        fish["fish_id"] = fish["fish_id"].astype(str)
        pres["fish_id"] = pres["fish_id"].astype(str)
        cols = ["fish_id"] + [c for c in ["sex","length_cm","weight_g"]
                               if c in fish.columns]
        pres = pres.merge(fish[cols].drop_duplicates("fish_id"),
                          on="fish_id", how="left")

    if "species" not in pres.columns:
        if fish is not None and "species" in fish.columns:
            sp_map = fish.set_index("fish_id")["species"].to_dict()
            pres["species"] = pres["fish_id"].map(sp_map).fillna("Desconocida")
        else:
            pres["species"] = "Desconocida"

    deploy_path = base / "deployment_metadata.csv"
    stations = None
    if deploy_path.exists():
        raw2 = deploy_path.read_text(encoding="utf-8", errors="replace")[:2000]
        sep2 = "\t" if raw2.count("\t") > raw2.count(",") else ","
        dep  = pd.read_csv(deploy_path, sep=sep2)
        lat_col   = next((c for c in dep.columns if "lat" in c.lower()), None)
        lon_col   = next((c for c in dep.columns if "lon" in c.lower()), None)
        st_col    = next((c for c in dep.columns if c.lower() in
                         ("station","station_id")), None)
        zone_col  = next((c for c in dep.columns if "zone" in c.lower()), None)
        depth_col = next((c for c in dep.columns if c.lower() == "depth"), None)
        btype_col = next((c for c in dep.columns if "bottom" in c.lower()), None)
        if lat_col and lon_col and st_col:
            keep = ([st_col, lat_col, lon_col] +
                    ([zone_col]  if zone_col  else []) +
                    ([depth_col] if depth_col else []) +
                    ([btype_col] if btype_col else []))
            stations = (dep[keep].dropna(subset=[lat_col, lon_col])
                                 .drop_duplicates(subset=[st_col])
                                 .rename(columns={st_col:"station",
                                                   lat_col:"lat",
                                                   lon_col:"lon"}))
            if zone_col:  stations = stations.rename(columns={zone_col:"zone"})
            if depth_col: stations = stations.rename(columns={depth_col:"depth"})
            if btype_col: stations = stations.rename(columns={btype_col:"bottom_type"})

    return pres, stations, fish


pres, stations, fish = load_data()
all_species  = sorted(pres["species"].dropna().unique())
all_years    = sorted(pres["year"].dropna().unique().tolist())
all_months   = list(range(1, 13))


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## Rayas del Mediterráneo")
    st.markdown("**BTN · Balearic Tracking Network**")
    st.markdown("---")
    st.markdown("### Filtros")

    sel_species = st.multiselect("Especie", options=all_species, default=all_species)

    sel_years = st.multiselect("Año", options=all_years, default=all_years)

    month_range = st.slider("Meses", 1, 12, (1, 12),
                            format="%d",
                            help="1 = Enero · 12 = Diciembre")

    if "sex" in pres.columns and pres["sex"].notna().any():
        sex_opts = sorted(pres["sex"].dropna().unique().tolist())
        sel_sex  = st.multiselect("Sexo", options=sex_opts, default=sex_opts,
                                  help="M = macho · F = hembra")
    else:
        sel_sex = None

    st.markdown("---")
    year_label = "·".join(str(y) for y in sorted(sel_years)) if sel_years else "todos los años"
    st.markdown(f"<small>Datos: IMEDEA (UIB-CSIC) · BTN · {year_label}</small>",
                unsafe_allow_html=True)

# ── Filtros ───────────────────────────────────────────────────────────────────
df = pres.copy()
if sel_species:
    df = df[df["species"].isin(sel_species)]
if sel_years:
    df = df[df["year"].isin(sel_years)]
df = df[df["month"].between(*month_range)]
if sel_sex and "sex" in df.columns:
    df = df[df["sex"].isin(sel_sex)]

month_order = [MONTH_ES[i] for i in range(1, 13) if i in df["month"].values]


# ════════════════════════════════════════════════════════════════════════════
# PORTADA Y KPIs
# ════════════════════════════════════════════════════════════════════════════
st.markdown("# 🐟 Rayas en el Mediterráneo Balear")
st.markdown("### Balearic Tracking Network - IMEDEA")

st.markdown(
    '<div class="section-intro">'
    'Las rayas (Batoidea) son depredadores bentónicos clave en el ecosistema '
    'mediterráneo, muy vulnerables a la pesca incidental de arrastre. '
    'Este proyecto visualiza los patrones de distribución y movimiento de '
    '7 especies de raya registradas por la red de telemetría acústica '
    'BTN-IMEDEA en las costas de las Islas Baleares.'
    '</div>', unsafe_allow_html=True)

n_events   = len(df)
n_ind      = df["fish_id"].nunique() if "fish_id" in df.columns else "—"
n_sp       = df["species"].nunique()
n_stations = df["station_dominant"].nunique()
peak_month = (df.groupby("month_s")["n_detections"].sum().idxmax()
              if len(df) else "—")

k1, k2, k3, k4, k5 = st.columns(5)
for col, val, label in [
    (k1, f"{n_events:,}",  "Eventos de presencia"),
    (k2, str(n_ind),       "Individuos detectados"),
    (k3, str(n_sp),        "Especies"),
    (k4, str(n_stations),  "Estaciones activas"),
    (k5, peak_month,       "Mes más activo"),
]:
    col.markdown(
        f'<div class="kpi-box">'
        f'<p class="kpi-value">{val}</p>'
        f'<p class="kpi-label">{label}</p>'
        f'</div>', unsafe_allow_html=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — DISTRIBUCIÓN GEOGRÁFICA
# ════════════════════════════════════════════════════════════════════════════
st.markdown("## Distribución geográfica")
st.markdown(
    '<div class="section-intro">'
    'Cada burbuja representa una estación de la red BTN. Su tamaño indica '
    'el número total de eventos de presencia; el color, la especie dominante.'
    '</div>', unsafe_allow_html=True)

col_map, col_bar = st.columns([3, 2])  # kept for fallback only

st_agg = (df.groupby("station_dominant")
            .agg(
                n_events=("n_detections","sum"),
                n_individuals=("fish_id","nunique"),
                **({ "dominant_species": (
                        "species",
                        lambda x: x.value_counts().index[0] if len(x) else "—"
                    )} if "species" in df.columns else {})
            ).reset_index())
if "dominant_species" not in st_agg.columns:
    st_agg["dominant_species"] = "Sin especie"

if stations is not None:
    st_agg = st_agg.merge(
        stations[["station","lat","lon"] +
                 (["zone"] if "zone" in stations.columns else [])],
        left_on="station_dominant", right_on="station", how="left")
    map_df = st_agg.dropna(subset=["lat","lon"])

    max_ev = map_df["n_events"].max() if len(map_df) else 1
    import numpy as np
    log_sizes  = np.log1p(map_df["n_events"])
    norm_sizes = (log_sizes / log_sizes.max() * 52 + 14).clip(14, 66)
    fig_map = go.Figure(go.Scattermap(
        lat=map_df["lat"], lon=map_df["lon"],
        mode="markers",
        marker=dict(
            size=norm_sizes,
            color=map_df["dominant_species"].map(SPECIES_COLORS).fillna("#888"),
            opacity=0.82,
        ),
        text=map_df["station_dominant"],
        customdata=map_df[["n_events","n_individuals","dominant_species"]].values,
        hovertemplate=(
            "<b>Estación %{text}</b><br>"
            "Eventos: %{customdata[0]:,}<br>"
            "Individuos: %{customdata[1]}<br>"
            "Especie dominante: %{customdata[2]}<extra></extra>"
        ),
    ))
    fig_map.update_layout(
        **PLOT_LAYOUT, height=500,
        margin=dict(l=0, r=0, t=10, b=0),
        map=dict(
            style="white-bg",
            layers=[{"below":"traces","sourcetype":"raster",
                     "source":["https://server.arcgisonline.com/ArcGIS/rest/services/"
                               "World_Imagery/MapServer/tile/{z}/{y}/{x}"]}],
            zoom=8, center={"lat":39.6,"lon":2.9},
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    bar1, bar2 = st.columns(2)
    sp_agg = (df.groupby("species")
                .agg(n_events=("n_detections","sum"), n_ind=("fish_id","nunique"))
                .reset_index().sort_values("n_events", ascending=True))
    with bar1:
        fig_sp = px.bar(sp_agg, x="n_events", y="species", orientation="h",
                        color="species", color_discrete_map=SPECIES_COLORS,
                        labels={"n_events":"Eventos","species":""},
                        title="Eventos por especie")
        fig_sp.update_layout(**PLOT_LAYOUT, showlegend=False, height=240,
                             margin=dict(l=0,r=10,t=40,b=0))
        st.plotly_chart(fig_sp, use_container_width=True)
    with bar2:
        fig_ind2 = px.bar(sp_agg.sort_values("n_ind", ascending=True),
                          x="n_ind", y="species", orientation="h",
                          color="species", color_discrete_map=SPECIES_COLORS,
                          labels={"n_ind":"Individuos únicos","species":""},
                          title="Individuos por especie")
        fig_ind2.update_layout(**PLOT_LAYOUT, showlegend=False, height=240,
                               margin=dict(l=0,r=10,t=40,b=0))
        st.plotly_chart(fig_ind2, use_container_width=True)
else:
    top_st = st_agg.sort_values("n_events", ascending=True).tail(15)
    fig_st = px.bar(top_st, x="n_events", y="station_dominant",
                    orientation="h", color="dominant_species",
                    color_discrete_map=SPECIES_COLORS,
                    labels={"station_dominant":"","n_events":"Eventos"},
                    title="Estaciones más activas")
    fig_st.update_layout(**PLOT_LAYOUT, height=440, showlegend=False)
    st.plotly_chart(fig_st, use_container_width=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN  — TRAYECTORIAS: TOP 5 INDIVIDUOS MÁS MÓVILES
# ════════════════════════════════════════════════════════════════════════════
st.markdown("## Trayectorias individuales")
st.markdown(
    '<div class="section-intro">'
    'Los 5 individuos que visitaron más estaciones distintas a lo largo del año. '
    'Las líneas unen cronológicamente '
    'las estaciones de detección, '
    'no el recorrido real entre puntos.'
    '</div>', unsafe_allow_html=True)

if stations is not None and "fish_id" in df.columns:

    # ── Calcular movilidad ────────────────────────────────────────────────
    mobility = (df.groupby(["fish_id"] +
                            (["species"] if "species" in df.columns else []))
                  ["station_dominant"].nunique()
                  .reset_index()
                  .rename(columns={"station_dominant": "n_stations"}))
    top5 = mobility.nlargest(5, "n_stations").reset_index(drop=True)

    IND_PALETTE = ["#4a6d8c","#7d1a2a","#2e7d6b","#6b5b8c","#c07c3a"]

    traj_all = (df[df["fish_id"].isin(top5["fish_id"])]
                .merge(stations[["station","lat","lon"]],
                       left_on="station_dominant", right_on="station", how="left")
                .dropna(subset=["lat","lon"])
                .sort_values(["fish_id","interval"]))

    # ── Bézier cuadrática (traducción del código R) ───────────────────────
    import numpy as np

    def bezier_curve(lon1, lat1, lon2, lat2, curvature=0.25, n_points=40):
        """Curva Bézier cuadrática entre dos puntos geográficos."""
        from_pt = np.array([lon1, lat1])
        to_pt   = np.array([lon2, lat2])
        midpoint   = (from_pt + to_pt) / 2
        diff       = to_pt - from_pt
        orthogonal = np.array([-diff[1], diff[0]])  # rotar 90°
        control    = midpoint + curvature * orthogonal
        t = np.linspace(0, 1, n_points)
        curve = np.outer((1-t)**2, from_pt) + \
                np.outer(2*(1-t)*t, control) + \
                np.outer(t**2, to_pt)
        return curve[:, 0], curve[:, 1]  # lons, lats

    if len(traj_all) == 0:
        st.markdown('<div class="note-box">Sin coordenadas para mostrar trayectorias.</div>',
                    unsafe_allow_html=True)
    else:
        fig_traj = go.Figure()

        for i, row in top5.iterrows():
            fid  = row["fish_id"]
            color = IND_PALETTE[i % len(IND_PALETTE)]
            sp    = row.get("species",fid) if "species" in row.index else fid
            label = f"{fid} · {sp.split()[-1]} ({int(row['n_stations'])} est.)"
            ind   = (traj_all[traj_all["fish_id"] == fid]
                     .drop_duplicates(subset=["station_dominant"])  # una visita por estación
                     .copy())

            
            for j in range(len(ind) - 1):
                r0, r1 = ind.iloc[j], ind.iloc[j+1]
                dist = ((r1["lon"]-r0["lon"])**2 + (r1["lat"]-r0["lat"])**2)**0.5
                curv = 0.18 if dist > 0.3 else 0.12
                lons, lats = bezier_curve(r0["lon"], r0["lat"],
                                          r1["lon"], r1["lat"],
                                          curvature=curv)
                fig_traj.add_trace(go.Scattermap(
                    lon=lons, lat=lats,
                    mode="lines",
                    line=dict(width=2, color=color),
                    opacity=0.75,
                    legendgroup = fid,
                    showlegend=(j == 0),
                    name=label if j == 0 else None,
                    hoverinfo="skip",
                ))

            
            fig_traj.add_trace(go.Scattermap(
                lat=ind["lat"], lon=ind["lon"],
                mode="markers",
                marker=dict(size=8, color=color, opacity=0.9),
                legendgroup=fid,
                showlegend=False,
                text=ind["station_dominant"],
                hovertemplate=f"<b>{fid}</b><br>%{{text}}<extra></extra>",
            ))

        fig_traj.update_layout(
            **PLOT_LAYOUT, height=520,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="v", x=1.01, y=1.0,
                        xanchor="left", yanchor="top", font=dict(size=10),
                        title=dict(text="Individuo")),
            map=dict(
                style="white-bg",
                layers=[{"below":"traces","sourcetype":"raster",
                         "source":["https://server.arcgisonline.com/ArcGIS/rest/services/"
                                   "World_Imagery/MapServer/tile/{z}/{y}/{x}"]}],
                zoom=8, center={"lat":39.6,"lon":2.9},
            ),
        )
        st.plotly_chart(fig_traj, use_container_width=True)
#        st.markdown(
#            '<div class="note-box">Top 5 individuos por número de estaciones visitadas. '
#            'Las curvas siguen una trayectoria Bézier y no representan el recorrido real.</div>',
#            unsafe_allow_html=True)
else:
    st.markdown('<div class="note-box">Necesita deployment_metadata.csv con lat/lon.</div>',
                unsafe_allow_html=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — ÁBACO: PRESENCIA INDIVIDUAL POR ZONA Y TIEMPO
# ════════════════════════════════════════════════════════════════════════════
st.markdown("## Presencia individual por zona")
st.markdown(
    '<div class="section-intro">'
    'Cada fila es un individuo. Las barras de color muestran en qué zona marina '
    'fue detectado cada día; el gris claro indica períodos sin detección. '
    'El punto amarillo marca la fecha de liberación del animal.'
    '</div>', unsafe_allow_html=True)

# Paleta de zonas
ZONE_COLORS = {
    "RM Migjorn":              "#1e5f5a",
    "RM el Toro i Malgrats":   "#CC7722",
    "RM Llevant":              "#c0392b",
    "RM sa Dragonona":         "#1a3a5c",
    "RM Badia de Palma":       "#8a8a1a",
    "PNMT Cabrera":            "#6b1a1a",
    "Outside MPA":             "#8a8a8a",
    "Non-detected":            "#e8e8e8",
}

@st.cache_data
def build_abacus(_pres, _stations, _fish, species_key):
    if _stations is None or "zone" not in _stations.columns:
        return None, None

    df_z = _pres.merge(_stations[["station","zone"]],
                       left_on="station_dominant", right_on="station", how="left")
    df_z["zone"] = df_z["zone"].fillna("Outside MPA")
    df_z["date"] = pd.to_datetime(df_z["interval"]).dt.tz_localize(None).dt.normalize()

    sp_map = (_pres[["fish_id","species"]].drop_duplicates()
                .set_index("fish_id")["species"].to_dict()
              if "species" in _pres.columns else {})

    daily = (df_z.groupby(["fish_id","date"])["zone"]
                  .agg(lambda x: x.value_counts().index[0])
                  .reset_index())

    segments = []
    for fish_id, grp in daily.groupby("fish_id"):
        grp = grp.sort_values("date").reset_index(drop=True)
        sp  = sp_map.get(fish_id, "")
        cur_zone  = grp.loc[0, "zone"]
        cur_start = grp.loc[0, "date"]

        for j in range(1, len(grp)):
            zone = grp.loc[j, "zone"]
            date = grp.loc[j, "date"]
            prev = grp.loc[j-1, "date"]
            gap  = (date - prev).days

            if gap > 1:
                segments.append(dict(fish_id=fish_id, species=sp, zone=cur_zone,
                                     Start=cur_start,
                                     Finish=prev + pd.Timedelta(days=1)))
                segments.append(dict(fish_id=fish_id, species=sp, zone="Non-detected",
                                     Start=prev + pd.Timedelta(days=1),
                                     Finish=date))
                cur_zone, cur_start = zone, date
            elif zone != cur_zone:
                segments.append(dict(fish_id=fish_id, species=sp, zone=cur_zone,
                                     Start=cur_start, Finish=date))
                cur_zone, cur_start = zone, date

        segments.append(dict(fish_id=fish_id, species=sp, zone=cur_zone,
                             Start=cur_start,
                             Finish=grp.loc[len(grp)-1,"date"] + pd.Timedelta(days=1)))

    if not segments:
        return None, None

    segs = pd.DataFrame(segments)
    segs["Start"]  = pd.to_datetime(segs["Start"])
    segs["Finish"] = pd.to_datetime(segs["Finish"])

    release = None
    if _fish is not None and "release_time_utc" in _fish.columns:
        release = _fish[["fish_id","release_time_utc"]].copy()
        release["release_time_utc"] = (pd.to_datetime(release["release_time_utc"], utc=True)
                                         .dt.tz_localize(None))
    return segs, release

if stations is not None and "zone" in stations.columns and "fish_id" in df.columns:

    # Selector de especie
    ab_species = st.selectbox("Especie", options=sorted(df["species"].dropna().unique()),
                              key="abacus_sp")
    df_ab = df[df["species"] == ab_species].copy()

    # Pasar como JSON para cache 
#    df_ab_s      = df_ab[["fish_id","station_dominant","interval","species"]].to_json(orient="split")
#    stations_s   = stations.to_json(orient="split")
#    fish_s       = fish.to_json(orient="split") if fish is not None else None

    segs, release = build_abacus(df_ab, stations, fish, ab_species)

    if segs is None or len(segs) == 0:
        st.markdown('<div class="note-box">Sin datos de zona para construir el ábaco.</div>',
                    unsafe_allow_html=True)
    else:
        # Ordenar individuos por primera detección
        first_det   = segs.groupby("fish_id")["Start"].min().sort_values()
        ordered_fish = first_det.index.tolist()

        # Colores de zona con fallback
        import hashlib
        all_zones = segs["zone"].unique()
        def zone_color(z):
            if z in ZONE_COLORS: return ZONE_COLORS[z]
            h = int(hashlib.md5(z.encode()).hexdigest()[:6], 16)
            return f"#{h:06x}"
        color_map = {z: zone_color(z) for z in all_zones}

        fig_ab = px.timeline(
            segs,
            x_start="Start",
            x_end="Finish",
            y="fish_id",
            color="zone",
            color_discrete_map=color_map,
            category_orders={"fish_id": ordered_fish},
            title=f"Presencia por zona — {ab_species}",
        )
        fig_ab.update_yaxes(autorange="reversed", tickfont=dict(size=9))
        fig_ab.update_layout(
            height=max(350, len(ordered_fish) * 22 + 100),
            margin=dict(l=100, r=20, t=50, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Source Sans 3, sans-serif",
            legend=dict(orientation="v", x=1.01, y=1.0,
                        xanchor="left", font=dict(size=9)),
            xaxis=dict(showgrid=True, gridcolor="#dde4ec"),
            yaxis=dict(showgrid=False),
        )

        # Punto amarillo = liberación
        if release is not None:
            rel_f = release[release["fish_id"].isin(ordered_fish)]
            fig_ab.add_trace(go.Scatter(
                x=rel_f["release_time_utc"],
                y=rel_f["fish_id"],
                mode="markers",
                marker=dict(symbol="circle", size=9,
                            color="#f0c040",
                            line=dict(width=1, color="#888")),
                name="Liberación",
                hovertemplate="<b>%{y}</b><br>Liberación: %{x|%Y-%m-%d}<extra></extra>",
            ))

        st.plotly_chart(fig_ab, use_container_width=True)
else:
    st.markdown(
        '<div class="note-box">Para el ábaco se necesita la columna <b>zone</b> '
        'en deployment_metadata.csv.</div>', unsafe_allow_html=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — BATIMETRÍA
# ════════════════════════════════════════════════════════════════════════════
st.markdown("## Batimetría y tipo de fondo")
st.markdown(
    '<div class="section-intro">'
    'Las rayas son especies bénticas que frecuentan fondos someros. '
    'Estos gráficos muestran en qué rangos de profundidad y tipos de fondo '
    'se concentran las detecciones, permitiendo caracterizar las preferencias '
    'de hábitat de cada especie.'
    '</div>', unsafe_allow_html=True)

if stations is not None and "depth" in stations.columns:
    # Unir profundidad y tipo de fondo a las detecciones
    depth_cols = ["station","depth"] + \
                 (["bottom_type"] if "bottom_type" in stations.columns else [])
    df_depth = df.merge(stations[depth_cols],
                        left_on="station_dominant", right_on="station", how="left")
    df_depth = df_depth.dropna(subset=["depth"])

    # Rangos de profundidad
    bins   = [0, 15, 25, 35, 50, 200]
    labels = ["0–15 m","15–25 m","25–35 m","35–50 m",">50 m"]
    df_depth["depth_range"] = pd.cut(df_depth["depth"], bins=bins,
                                      labels=labels, right=True)

    col_b1, col_b2 = st.columns(2)

    with col_b1:
        # Detecciones por rango de profundidad y especie
        depth_sp = (df_depth.groupby(["depth_range","species"],
                                      observed=True)["n_detections"]
                             .sum().reset_index())
        fig_depth = px.bar(
            depth_sp,
            x="depth_range", y="n_detections",
            color="species", color_discrete_map=SPECIES_COLORS,
            labels={"depth_range":"Profundidad","n_detections":"Detecciones",
                    "species":"Especie"},
            title="Detecciones por rango de profundidad",
            category_orders={"depth_range": labels},
        )
        fig_depth.update_layout(**PLOT_LAYOUT, height=340,
                                margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="v", x=1.01))
        st.plotly_chart(fig_depth, use_container_width=True)

    with col_b2:
        if "bottom_type" in df_depth.columns and df_depth["bottom_type"].notna().any():
            
            def simplify_bottom(bt):
                if pd.isna(bt): return "Desconocido"
                bt = bt.lower()
                if "posidonia" in bt: return "Posidonia"
                if "rock" in bt or "roca" in bt: return "Roca"
                if "sand" in bt or "arena" in bt: return "Arena"
                return "Otro"

            df_depth["bottom_simple"] = df_depth["bottom_type"].apply(simplify_bottom)

            BOTTOM_COLORS = {
                "Posidonia": "#2e7d6b",
                "Roca":      "#6b5b8c",
                "Arena":     "#c07c3a",
                "Otro":      "#8a8a7a",
                "Desconocido":"#cccccc",
            }
            btype_sp = (df_depth.groupby(["bottom_simple","species"],
                                          observed=True)["n_detections"]
                                 .sum().reset_index())
            fig_btype = px.bar(
                btype_sp,
                x="bottom_simple", y="n_detections",
                color="species", color_discrete_map=SPECIES_COLORS,
                labels={"bottom_simple":"Tipo de fondo",
                        "n_detections":"Detecciones","species":"Especie"},
                title="Detecciones por tipo de fondo",
            )
            fig_btype.update_layout(**PLOT_LAYOUT, height=340,
                                    margin=dict(l=0, r=0, t=40, b=0),
                                    legend=dict(orientation="v", x=1.01))
            st.plotly_chart(fig_btype, use_container_width=True)
        else:
            # Sin bottom_type: scatter profundidad vs detecciones por estación
            st_depth = (df_depth.groupby(["station_dominant","depth"])["n_detections"]
                                 .sum().reset_index())
            fig_sc_d = px.scatter(
                st_depth, x="depth", y="n_detections",
                size="n_detections", color="n_detections",
                color_continuous_scale=[[0,"#d6e8f7"],[1,"#1a3a5c"]],
                labels={"depth":"Profundidad (m)","n_detections":"Detecciones",
                        "station_dominant":"Estación"},
                title="Profundidad de estación vs detecciones",
                hover_name="station_dominant",
            )
            fig_sc_d.update_layout(**PLOT_LAYOUT, height=340,
                                   margin=dict(l=0, r=0, t=40, b=0),
                                   showlegend=False)
            st.plotly_chart(fig_sc_d, use_container_width=True)

    # Profundidad media por especie
    depth_mean = (df_depth.groupby("species")["depth"]
                           .mean().reset_index()
                           .rename(columns={"depth":"prof_media"})
                           .sort_values("prof_media"))
    fig_dm = px.bar(
        depth_mean, x="prof_media", y="species",
        orientation="h", color="species",
        color_discrete_map=SPECIES_COLORS,
        labels={"prof_media":"Profundidad media (m)","species":""},
        title="Profundidad media de detección por especie",
        text=depth_mean["prof_media"].round(1),
    )
    fig_dm.update_traces(textposition="outside")
    fig_dm.update_layout(**PLOT_LAYOUT, showlegend=False, height=260,
                         margin=dict(l=0, r=60, t=40, b=0))
    st.plotly_chart(fig_dm, use_container_width=True)
#    st.markdown(
#        '<div class="note-box">La profundidad media de detección es un indicador '
#        'de las preferencias de hábitat de cada especie, condicionada por la '
#        'distribución de los receptores en la red BTN.</div>',
#        unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="note-box">Para el análisis de batimetría, '
        'deployment_metadata.csv necesita una columna <b>depth</b>.</div>',
        unsafe_allow_html=True)
st.markdown("## Comportamiento individual")
st.markdown(
    '<div class="section-intro">'
    'Algunos individuos son residentes (permanecen semanas en las mismas '
    'estaciones) y otros transeúntes (pocas detecciones antes de desaparecer). '
    'Las rayas marcadas tienen el sexo registrado, lo que permite '
    'explorar si machos y hembras muestran patrones distintos.'
    '</div>', unsafe_allow_html=True)

has_sex = "sex" in df.columns and df["sex"].notna().any()

if "fish_id" in df.columns:
    group_cols = ["fish_id"]
    if "species" in df.columns: group_cols.append("species")
    if has_sex:                  group_cols.append("sex")

    ind_agg = (df.groupby(group_cols)
                 .agg(n_days=("interval","nunique"),
                      n_events=("n_detections","sum"),
                      n_stations=("station_dominant","nunique"),
                      first_det=("interval","min"),
                      last_det=("interval","max"))
                 .reset_index())
    ind_agg["active_days"] = (ind_agg["last_det"] - ind_agg["first_det"]).dt.days + 1

    col_sc, col_sex = st.columns(2)

    with col_sc:
        scatter_color = "sex" if has_sex else ("species" if "species" in ind_agg.columns else None)
        color_map     = SEX_COLORS if scatter_color == "sex" else SPECIES_COLORS

        fig_sc = px.scatter(
            ind_agg,
            x="active_days", y="n_events",
            color=scatter_color,
            color_discrete_map=color_map,
            symbol="species" if (has_sex and "species" in ind_agg.columns) else None,
            size="n_stations",
            hover_name="fish_id",
            hover_data={c: True for c in ["n_days","n_stations","species","sex"]
                        if c in ind_agg.columns},
            labels={"active_days":"Días de seguimiento",
                    "n_events":"Total detecciones",
                    "n_stations":"Estaciones visitadas",
                    "sex":"Sexo","species":"Especie"},
            title="Residentes/Transeúntes",
            opacity=0.82
        )
        fig_sc.update_layout(**PLOT_LAYOUT, height=380)
        st.plotly_chart(fig_sc, use_container_width=True)
#        st.markdown(
#            '<div class="note-box">Cada punto es un individuo. '
#            'Tamaño = estaciones visitadas. '
#            'Azul = macho · Granate = hembra.</div>',
#            unsafe_allow_html=True)

    with col_sex:
        if has_sex and "species" in ind_agg.columns:
            sex_sp = (ind_agg.groupby(["species","sex"])["fish_id"]
                             .count().reset_index()
                             .rename(columns={"fish_id":"n"}))
            fig_sexsp = px.bar(
                sex_sp, x="species", y="n", color="sex",
                color_discrete_map=SEX_COLORS,
                barmode="group",
                labels={"species":"Especie","n":"Individuos","sex":"Sexo"},
                title="Individuos por especie y sexo"
            )
            fig_sexsp.update_layout(**PLOT_LAYOUT, height=380,
                                    xaxis_tickangle=-90,
                                    margin=dict(l=0, r=80, t=40, b=120),
                                    legend=dict(orientation="v", x=1.02, y=1.0,
                                                xanchor="left", yanchor="top"))
            st.plotly_chart(fig_sexsp, use_container_width=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — RESERVAS MARINAS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("## Reservas marinas")
st.markdown(
    '<div class="section-intro">'
    'Las Islas Baleares cuentan con 12 reservas marinas de interés pesquero. '
    '¿Utilizan las rayas estas zonas protegidas? ¿Varía el uso a lo largo del año?'
    '</div>', unsafe_allow_html=True)

if stations is not None and "zone" in stations.columns:
    has_sex  = "sex" in df.columns and df["sex"].notna().any()
    df_zone  = df.merge(stations[["station","zone"]],
                       left_on="station_dominant", right_on="station", how="left")
    df_zone  = df_zone.copy()
    df_zone["is_rm"] = df_zone["zone"].str.contains(
        "reserva|RM|reserve|integral|parcial", case=False, na=False)

    col_d, col_z = st.columns(2)

    with col_d:
        if has_sex and "sex" in df_zone.columns:
            # 4 segmentos: sexo × dentro/fuera de RM
            sex_rm = (df_zone.groupby(["sex","is_rm"])["n_detections"]
                             .sum().reset_index())
            sex_rm["label"] = sex_rm.apply(
                lambda r: f"{'♀' if r['sex']=='F' else '♂'} "
                          f"{'dentro' if r['is_rm'] else 'fuera'}",
                axis=1)
            color_map_rm = {
                "♀ dentro": SEX_COLORS["F"],
                "♂ dentro": SEX_COLORS["M"],
                "♀ fuera":  SEX_COLORS_MUTED["F"],
                "♂ fuera":  SEX_COLORS_MUTED["M"],
            }
            fig_donut = px.pie(
                sex_rm, values="n_detections", names="label",
                color="label", color_discrete_map=color_map_rm,
                title="Uso de reservas marinas por sexo",
                hole=0.5
            )
        else:
            rm_counts = (df_zone.groupby("is_rm")["n_detections"]
                                .sum().reset_index())
            rm_counts["Zona"] = rm_counts["is_rm"].map(
                {True:"Dentro de reserva", False:"Fuera de reserva"})
            fig_donut = px.pie(
                rm_counts, values="n_detections", names="Zona",
                color="Zona",
                color_discrete_map={"Dentro de reserva":"#4a6d8c",
                                    "Fuera de reserva":"#a0b0c0"},
                title="Detecciones dentro y fuera de reservas",
                hole=0.5
            )
        fig_donut.update_layout(**PLOT_LAYOUT, height=380,
                                margin=dict(l=0, r=140, t=40, b=0),
                                legend=dict(orientation="v", x=1.02, y=0.5,
                                            xanchor="left", yanchor="middle",
                                            font=dict(size=11)))
        st.plotly_chart(fig_donut, use_container_width=True)
#        if has_sex:
#            st.markdown(
#                '<div class="note-box">Colores vivos = dentro de reserva · '
#                'Colores apagados = fuera. '
#                '♀ ocre · ♂ turquesa</div>', unsafe_allow_html=True)

    with col_z:
        zone_month = (df_zone.groupby(["zone","month"])["n_detections"]
                             .sum().reset_index().sort_values("month"))
        zone_month["month_s"] = zone_month["month"].map(MONTH_ES)
        fig_zm = px.line(
            zone_month, x="month_s", y="n_detections",
            color="zone", markers=True,
            labels={"month_s":"Mes","n_detections":"Detecciones","zone":"Zona"},
            title="Estacionalidad por zona",
            category_orders={"month_s": list(MONTH_ES.values())}
        )
        fig_zm.update_layout(**PLOT_LAYOUT, height=360,
                             margin=dict(l=0, r=160, t=40, b=0),
                             legend=dict(orientation="v", x=1.02, y=1.0,
                                         xanchor="left", yanchor="top",
                                         font=dict(size=10)))
        st.plotly_chart(fig_zm, use_container_width=True)
else:
    st.markdown(
        '<div class="note-box">Para el análisis por reservas marinas, '
        'deployment_metadata.csv necesita una columna de zona.</div>',
        unsafe_allow_html=True)

st.markdown("---")

st.markdown(
    '<div style="text-align:center;color:#999;font-size:0.82rem;padding:16px 0;">'
    'Balearic Tracking Network (BTN) · IMEDEA (UIB-CSIC)'
    '</div>', unsafe_allow_html=True)
