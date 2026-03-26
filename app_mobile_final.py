"""
⚽ ASSISTANT COACH IA - MOBILE-FIRST
Interface optimisée pour téléphone et tablette
✅ Design responsive
✅ Touches larges et faciles
✅ Chargement rapide
✅ Navigation intuitive
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import logging
import warnings
import random
from datetime import datetime
from pathlib import Path

import shap
import plotly.graph_objects as go
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

warnings.filterwarnings('ignore')

# =========================
# 🎨 CONFIGURATION STREAMLIT MOBILE
# =========================

st.set_page_config(
    page_title="⚽ Coach IA",
    layout="wide",
    initial_sidebar_state="collapsed",  # Sidebar fermée par défaut
    menu_items=None  # Cache le menu hamburger Streamlit
)

# CSS MOBILE-FIRST CUSTOM
st.markdown("""
    <style>
    /* Mobile First - Responsive Design */
    * {
        margin: 0;
        padding: 0;
    }
    
    /* BODY & GENERAL */
    body {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #fff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
    }
    
    /* HEADER CUSTOM */
    .header-custom {
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 50%, #c92a2a 100%);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    .header-custom h1 {
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* CARDS */
    .metric-card {
        background: linear-gradient(135deg, #1f3c72 0%, #2a5298 100%);
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #ff6b6b;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        margin: 10px 0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:active {
        transform: scale(0.98);
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    
    .metric-card.danger {
        border-left-color: #ff3333;
    }
    
    .metric-card.warning {
        border-left-color: #ffd700;
    }
    
    .metric-card.success {
        border-left-color: #51cf66;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #ff6b6b;
    }
    
    .metric-label {
        font-size: 12px;
        color: #aaa;
        margin-top: 5px;
    }
    
    /* BUTTONS */
    .stButton > button {
        width: 100%;
        padding: 12px !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border: none !important;
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 100%) !important;
        color: white !important;
        box-shadow: 0 4px 10px rgba(255, 107, 107, 0.3) !important;
        transition: all 0.3s !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #ff5252 0%, #ee4a5c 100%) !important;
        box-shadow: 0 6px 15px rgba(255, 107, 107, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.95);
    }
    
    /* SLIDERS */
    .stSlider {
        padding: 10px 0;
    }
    
    .stSlider > div > div {
        background: #2a5298;
    }
    
    /* INPUTS */
    .stNumberInput input,
    .stSelectbox select,
    .stTextArea textarea {
        background: #1a1f2e !important;
        color: #fff !important;
        border: 2px solid #2a5298 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        font-size: 14px !important;
    }
    
    .stNumberInput input:focus,
    .stSelectbox select:focus,
    .stTextArea textarea:focus {
        border-color: #ff6b6b !important;
        box-shadow: 0 0 10px rgba(255, 107, 107, 0.3) !important;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        padding: 0 15px;
        background: #1a1f2e;
        border-radius: 8px;
        border: 2px solid #2a5298;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 100%);
        border-color: #ff6b6b;
    }
    
    /* INFO/SUCCESS/ERROR BOXES */
    .stAlert {
        border-radius: 8px !important;
        padding: 12px !important;
        border-left: 4px solid !important;
    }
    
    /* DIVIDER */
    .stDivider {
        background: #2a5298;
    }
    
    /* CHECKBOX */
    .stCheckbox {
        padding: 8px;
    }
    
    .stCheckbox > label {
        font-size: 14px;
    }
    
    /* SIDEBAR */
    .stSidebar {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%) !important;
    }
    
    /* RESPONSIVE GRID */
    @media (max-width: 768px) {
        [data-testid="column"] {
            max-width: 100% !important;
        }
        
        .stMetric {
            margin: 5px 0;
        }
        
        .header-custom h1 {
            font-size: 24px;
        }
        
        .metric-value {
            font-size: 20px;
        }
    }
    
    @media (max-width: 480px) {
        .header-custom {
            padding: 12px;
        }
        
        .header-custom h1 {
            font-size: 20px;
        }
        
        .metric-card {
            padding: 12px;
        }
        
        .metric-value {
            font-size: 18px;
        }
        
        .stButton > button {
            padding: 10px !important;
            font-size: 14px !important;
        }
    }
    
    /* PROGRESS BAR CUSTOM */
    .stProgress > div > div {
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 100%) !important;
    }
    
    /* METRIC DISPLAY */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1f3c72 0%, #2a5298 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff6b6b;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# ⚙️ CONFIGURATION LOGGING
# =========================

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger("coach_ia")
    logger.setLevel(logging.DEBUG)
    
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_dir / "coach_ia.log",
        maxBytes=5*1024*1024,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

# =========================
# 🗄️ BASE DE DONNÉES SQLITE
# =========================

class MatchDatabase:
    def __init__(self, db_path="matchs.db"):
        self.db_path = db_path
        self.init_db()
        logger.info(f"Database initialized: {db_path}")
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS matchs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_match TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                possession INTEGER,
                tirs_equipe INTEGER,
                tirs_adverses INTEGER,
                score_equipe INTEGER,
                score_adverses INTEGER,
                xg_equipe REAL,
                xg_adverses REAL,
                diff_score INTEGER,
                score_ia REAL,
                style_jeu TEXT,
                systeme_adverse TEXT,
                attaque_gauche INTEGER,
                attaque_centre INTEGER,
                attaque_droite INTEGER,
                minute_match INTEGER,
                notes TEXT,
                contexte TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def ajouter_match(self, data):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT INTO matchs 
                (possession, tirs_equipe, tirs_adverses, score_equipe, score_adverses,
                 xg_equipe, xg_adverses, diff_score, score_ia, style_jeu, 
                 systeme_adverse, attaque_gauche, attaque_centre, attaque_droite,
                 minute_match, notes, contexte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('possession'), data.get('tirs_equipe'), data.get('tirs_adverses'),
                data.get('score_equipe'), data.get('score_adverses'), data.get('xg_equipe'),
                data.get('xg_adverses'), data.get('diff_score'), data.get('score_ia'),
                data.get('style_jeu', ''), data.get('systeme_adverse', ''),
                data.get('attaque_gauche', 0), data.get('attaque_centre', 0), 
                data.get('attaque_droite', 0), data.get('minute', 0),
                data.get('notes', ''), data.get('contexte', '')
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding match: {e}")
            return False
    
    def get_historique(self, limit=100):
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(
                "SELECT * FROM matchs ORDER BY date_match DESC LIMIT ?", 
                conn, params=(limit,)
            )
            conn.close()
            return df if len(df) > 0 else None
        except Exception as e:
            logger.error(f"Error getting historique: {e}")
            return None
    
    def get_stats_saison(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            stats = c.execute('''
                SELECT 
                    COUNT(*) as nb_matchs,
                    AVG(possession) as possession_moy,
                    AVG(tirs_equipe) as tirs_moy,
                    AVG(xg_equipe) as xg_moy,
                    AVG(score_ia) as score_ia_moy,
                    SUM(CASE WHEN score_ia > 15 THEN 1 ELSE 0 END) as victoires,
                    SUM(CASE WHEN score_ia >= -15 AND score_ia <= 15 THEN 1 ELSE 0 END) as nuls,
                    SUM(CASE WHEN score_ia < -15 THEN 1 ELSE 0 END) as defaites
                FROM matchs
            ''').fetchone()
            conn.close()
            return stats if stats and stats[0] > 0 else None
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return None

# =========================
# 🔧 UTILITAIRES CALCULS
# =========================

def contre_systeme(sys: str) -> str:
    table = {"4-3-3": "4-2-3-1", "4-4-2": "3-5-2", "3-5-2": "4-3-3", "4-2-3-1": "4-4-2", "5-3-2": "4-3-3"}
    return table.get(sys, "4-3-3")

def calcul_xg(tirs: int) -> float:
    return round(tirs * 0.12, 2)

def calcul_domination(tirs_eq, possession, tirs_adv) -> float:
    return (tirs_eq * 4 + possession * 0.4) - (tirs_adv * 4)

def calcul_danger(t_eq, t_adv, xg_eq, xg_adv, s_eq, s_adv, minute) -> int:
    danger = 0
    if t_adv > t_eq: danger += 1
    if xg_adv > xg_eq: danger += 1
    if s_eq <= s_adv: danger += 1
    if minute > 70: danger += 1
    return danger

def calcul_fatigue(minute, style_jeu) -> int:
    fatigue = 0
    if minute > 60: fatigue += 1
    if style_jeu == "Pressing": fatigue += 2
    return fatigue

def calcul_score_ia(domination, xg_eq, xg_adv, score_eq, score_adv, fatigue, danger, minute):
    score = (domination * 0.4 + (xg_eq - xg_adv) * 12 + (score_eq - score_adv) * 18 - fatigue * 12 - danger * 10)
    if minute > 75:
        score -= danger * 2 + fatigue * 2
    return score

def strategie_depuis_score(score_ia, danger, fatigue):
    if fatigue >= 3:
        return "🐢 Ralentir le rythme"
    if score_ia < -20:
        return "🛡️ Bloc bas défensif"
    elif score_ia < 0:
        return "⚡ Augmenter l'intensité"
    elif score_ia < 20:
        return "⚖️ Maintenir l'équilibre"
    else:
        return "⚔️ Exploiter l'avantage"

def valider_entrees(possession, tirs_equipe, tirs_adverses, score_equipe, score_adverses, minute) -> list:
    erreurs = []
    if possession == 0 and tirs_equipe == 0:
        erreurs.append("⚠️ Possession et tirs à 0")
    if minute < 1 or minute > 90:
        erreurs.append("⚠️ Minute invalide")
    return erreurs

# =========================
# 📊 PROFIL & FORME
# =========================

class ProfilEquipe:
    def __init__(self, db):
        self.db = db
    
    def calculer_profil(self):
        historique = self.db.get_historique(limit=30)
        
        if historique is None or len(historique) < 5:
            return {
                "possession_moy": 50, "tirs_moy": 6, "xg_moy": 0.72,
                "style_offensif": "Adaptatif", "evolution_possession": 0,
            }
        
        tirs_par_possession = historique['tirs_equipe'].sum() / (historique['possession'].mean() / 100 + 0.01)
        style = "Direct" if tirs_par_possession > 0.3 else ("Possession" if historique['possession'].mean() > 55 else "Transition")
        
        recent = historique.head(5)['possession'].mean()
        older = historique.tail(5)['possession'].mean()
        
        return {
            "possession_moy": round(historique["possession"].mean(), 1),
            "tirs_moy": round(historique["tirs_equipe"].mean(), 1),
            "xg_moy": round(historique["xg_equipe"].mean(), 2),
            "style_offensif": style,
            "evolution_possession": round(recent - older, 1),
        }
    
    def charger_profil(self):
        return self.calculer_profil()

def calcul_forme_recente(db, n: int = 5) -> dict:
    historique = db.get_historique(limit=n)
    
    if historique is None or len(historique) < 3:
        return {"label": "⚪ Pas de données", "emoji": "⚪"}
    
    try:
        victoires = int((historique["score_ia"] > 15).sum())
        nuls = int(((historique["score_ia"] >= -15) & (historique["score_ia"] <= 15)).sum())
        defaites = int((historique["score_ia"] < -15).sum())
        score_forme = round(historique["score_ia"].mean(), 1)
        
        if score_forme > 10:
            return {"label": "🔥 Excellente", "emoji": "🔥", "record": f"{victoires}V {nuls}N {defaites}D"}
        elif score_forme > 0:
            return {"label": "🟢 Bonne", "emoji": "🟢", "record": f"{victoires}V {nuls}N {defaites}D"}
        elif score_forme > -10:
            return {"label": "🟡 Moyenne", "emoji": "🟡", "record": f"{victoires}V {nuls}N {defaites}D"}
        else:
            return {"label": "🔴 Mauvaise", "emoji": "🔴", "record": f"{victoires}V {nuls}N {defaites}D"}
    except Exception as e:
        logger.error(f"Error calculating forme: {e}")
        return {"label": "⚪ Erreur", "emoji": "⚪"}

def calcul_momentum_persistant(db, score_ia_actuel: float) -> dict:
    historique = db.get_historique(limit=4)
    
    if historique is None or len(historique) < 2:
        return {"label": "➡️ Nouveau match", "emoji": "➡️"}
    
    try:
        scores = historique["score_ia"].tolist()
        scores.append(score_ia_actuel)
        delta = round(scores[-1] - scores[0], 1)
        
        if delta > 5:
            return {"label": f"📈 En hausse", "emoji": "📈", "delta": f"+{delta}"}
        elif delta < -5:
            return {"label": f"📉 En baisse", "emoji": "📉", "delta": f"{delta}"}
        else:
            return {"label": f"➡️ Stable", "emoji": "➡️", "delta": f"{delta:+.1f}"}
    except Exception:
        return {"label": "➡️ Erreur", "emoji": "➡️"}

def predire_fin_match(score_ia_actuel, minute_actuelle, historique_30):
    if minute_actuelle >= 90:
        return None
    
    evolution_minute = score_ia_actuel / max(minute_actuelle, 1)
    minutes_restantes = 90 - minute_actuelle
    score_projete = score_ia_actuel + (evolution_minute * minutes_restantes)
    
    confiance = 0.6
    if historique_30 is not None and len(historique_30) >= 3:
        variance = historique_30['score_ia'].std()
        confiance = max(0.5, min(0.95, 1 - (variance / 100)))
    
    if score_projete > 20:
        prediction = "🟢 Victoire"
    elif score_projete > 0:
        prediction = "🟡 Égalité"
    else:
        prediction = "🔴 Défaite"
    
    return {
        'score_final_projete': round(score_projete, 1),
        'prediction': prediction,
        'confiance': round(confiance * 100),
        'minutes_restantes': int(minutes_restantes),
    }

def parser_notes_contexte(notes_text):
    if not notes_text:
        return {'contexte': {}, 'resume': "Normal"}
    
    notes = notes_text.lower()
    contexte = {
        'blessures': any(m in notes for m in ['blessure', 'carton']),
        'rouge': 'rouge' in notes,
        'meteo': any(m in notes for m in ['pluie', 'froid']),
    }
    
    contextes_actifs = [k.replace('_', ' ').title() for k, v in contexte.items() if v]
    resume = ", ".join(contextes_actifs) if contextes_actifs else "Normal"
    return {'contexte': contexte, 'resume': resume}

# =========================
# 📊 DONNÉES & MODÈLE ML
# =========================

def generer_donnees_base(n=200, seed=42, profil: dict = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    
    if profil and isinstance(profil, dict) and "possession_moy" in profil:
        p_moy = profil.get("possession_moy", 50)
        t_moy = int(profil.get("tirs_moy", 6))
    else:
        p_moy = 50
        t_moy = 6
    
    possession = np.clip(rng.normal(p_moy, 10, n), 20, 80).astype(int)
    tirs_equipe = np.clip(rng.normal(t_moy, 3, n), 1, 20).astype(int)
    tirs_adverses = rng.integers(1, 15, n)
    xg_equipe = np.round(tirs_equipe * 0.12, 2)
    xg_adverses = np.round(tirs_adverses * 0.12, 2)
    diff_score = rng.integers(-3, 3, n)
    domination = (tirs_equipe * 4 + possession * 0.4) - (tirs_adverses * 4)
    score_ia = domination * 0.5 + (xg_equipe - xg_adverses) * 10 + diff_score * 15 + rng.normal(0, 3, n)
    
    return pd.DataFrame({
        "possession": possession, "tirs_equipe": tirs_equipe, "tirs_adverses": tirs_adverses,
        "xg_equipe": xg_equipe, "xg_adverses": xg_adverses, "diff_score": diff_score, 
        "score_ia": np.round(score_ia, 2),
    })

FEATURES = ["possession", "tirs_equipe", "tirs_adverses", "xg_equipe", "xg_adverses", "diff_score"]

@st.cache_resource
def charger_modele(_db, profil):
    try:
        df_base = generer_donnees_base(profil=profil)
        historique = _db.get_historique(limit=1000)
        
        if historique is not None and len(historique) > 0:
            df_reel_pondere = pd.concat([historique] * 3, ignore_index=True)
            df_total = pd.concat([df_base, df_reel_pondere], ignore_index=True)
            nb_vrais = len(historique)
        else:
            df_total = df_base
            nb_vrais = 0
        
        df_total["niveau"] = df_total["score_ia"].apply(
            lambda s: 2 if s > 15 else (1 if s > -15 else 0)
        )
        
        X = df_total[FEATURES]
        y = df_total["niveau"]
        
        modele = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
        modele.fit(X, y)
        
        scores_cv = cross_val_score(modele, X, y, cv=5)
        accuracy = round(scores_cv.mean(), 3)
        
        if nb_vrais == 0:
            confiance = "🟡 Débutant"
        elif nb_vrais < 5:
            confiance = f"🟠 Apprentissage"
        elif nb_vrais < 15:
            confiance = f"🟢 Opérationnel"
        else:
            confiance = f"🏆 Expert"
        
        importances = dict(zip(FEATURES, modele.feature_importances_))
        
        return modele, accuracy, nb_vrais, confiance, importances, X
    except Exception as e:
        logger.error(f"Model error: {e}")
        return None, 0, 0, "🔴 Erreur", {}, None

def invalider_cache_modele():
    charger_modele.clear()

# =========================
# 📈 GRAPHIQUES MOBILE
# =========================

def plot_radar_profil(profil_30):
    try:
        categories = ['Possession', 'Tirs', 'xG', 'Intensité']
        values_equipe = [
            profil_30['possession_moy'],
            min(profil_30['tirs_moy'] / 12 * 100, 100),
            min(profil_30['xg_moy'] / 2 * 100, 100),
            50 + profil_30.get('evolution_possession', 0) * 2
        ]
        values_ligue = [50, 100, 100, 50]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values_equipe, theta=categories, fill='toself', 
                                      name='Équipe', line=dict(color='#ff6b6b')))
        fig.add_trace(go.Scatterpolar(r=values_ligue, theta=categories, fill='toself', 
                                      name='Ligue', line=dict(color='#2a5298'), opacity=0.5))
        fig.update_layout(
            title="Profil vs Ligue",
            height=350,
            paper_bgcolor='rgba(15,20,25,0)',
            plot_bgcolor='rgba(15,20,25,0)',
            font=dict(color='#fff', size=10),
            showlegend=True
        )
        return fig
    except Exception as e:
        logger.error(f"Error plotting: {e}")
        return None

# =========================
# ⚙️ STREAMLIT CONFIG
# =========================

if "simulation" not in st.session_state:
    st.session_state.simulation = []
if "db" not in st.session_state:
    st.session_state.db = MatchDatabase()

db = st.session_state.db

# =========================
# HEADER CUSTOM
# =========================

st.markdown("""
    <div class="header-custom">
        <h1>⚽ COACH IA PRO</h1>
        <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.9;">Intelligence Tactique Football</p>
    </div>
""", unsafe_allow_html=True)

# =========================
# NAVIGATION MOBILE
# =========================

with st.sidebar:
    st.markdown("### 📋 MENU")
    mode = st.radio("", ["⚡ Rapide", "🧠 Analyse", "📊 Historique", "⚙️ Paramètres"])

# =========================
# ⚡ MODE RAPIDE
# =========================

if mode == "⚡ Rapide":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1f3c72 0%, #2a5298 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="margin: 0; font-size: 20px;">Décision Rapide</h2>
            <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.8;">Banc de Touche - Réponse immédiate</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Inputs en une colonne pour mobile
    st.markdown("**Score du match**")
    col1, col2 = st.columns(2)
    with col1:
        score = st.radio("", ["🟢 Gagne", "🟡 Égalité", "🔴 Perd"], label_visibility="collapsed")
    with col2:
        dynamique = st.radio("", ["💪 Domine", "⚖️ Équilibré", "😰 Subit"], label_visibility="collapsed")
    
    col3, col4 = st.columns(2)
    with col3:
        minute_r = st.slider("Minute", 0, 90, 60, step=5)
    with col4:
        systeme_adverse = st.selectbox("Système adverse", ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1"], label_visibility="collapsed")
    
    suggestion = contre_systeme(systeme_adverse)
    
    st.markdown("---")
    
    # Affichage réponse
    st.markdown("### 🎯 RECOMMANDATION")
    
    if score == "🔴 Perd" and dynamique == "😰 Subit":
        st.error(f"🚨 URGENCE TACTIQUE\n\n**Action:** Bloc bas défensif + **{suggestion}**\n\n⏱️ Serrer les rangs et jouer en transition rapide")
    elif score == "🔴 Perd":
        st.warning(f"⚠️ SITUATION CRITIQUE\n\n**Action:** Chercher le but + **{suggestion}**")
    elif score == "🟡 Égalité" and dynamique == "💪 Domine":
        st.info(f"🎯 À EXPLOITER\n\n**Action:** Augmenter le rythme et pressing haut")
    elif score == "🟢 Gagne":
        st.success(f"✅ PARFAIT\n\n**Action:** Maintenir intensité et contrôle")
    
    if minute_r > 75 and score != "🟢 Gagne":
        st.markdown("""
            <div style="background: linear-gradient(135deg, #ff3333 0%, #cc0000 100%); 
                        padding: 12px; border-radius: 8px; margin-top: 10px;">
                <p style="margin: 0; font-weight: 700;">⏱️ FIN DE MATCH IMMINENTE</p>
                <p style="margin: 5px 0 0 0; font-size: 12px;">Prenez les risques calculés maintenant!</p>
            </div>
        """, unsafe_allow_html=True)

# =========================
# 🧠 MODE ANALYSE
# =========================

elif mode == "🧠 Analyse":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1f3c72 0%, #2a5298 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="margin: 0; font-size: 20px;">Analyse Complète</h2>
            <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.8;">Tous les détails du match</p>
        </div>
    """, unsafe_allow_html=True)
    
    # ===== SECTION 1: SCORE & POSSESSION =====
    with st.expander("📊 Score & Possession", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            score_equipe = st.number_input("🔵 Score équipe", 0, 10, 1)
            possession = st.slider("🎯 Possession %", 0, 100, 50)
        with col2:
            score_adverses = st.number_input("🔴 Score adverse", 0, 10, 0)
            minute = st.slider("⏱️ Minute", 1, 90, 45)
    
    # ===== SECTION 2: TIRS & QUALITÉ =====
    with st.expander("⚽ Tirs & Qualité", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            tirs_equipe = st.number_input("🔵 Tirs équipe", 0, 50, 10)
        with col2:
            tirs_adverses = st.number_input("🔴 Tirs adverses", 0, 50, 8)
    
    # ===== SECTION 3: STYLE & SYSTÈME =====
    with st.expander("🎯 Style & Système", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            style_jeu = st.selectbox("Style de jeu", ["équilibré", "pressing", "défensif", "offensif"])
        with col2:
            systeme_adverse_analyse = st.selectbox("Système adverse", ["4-4-2", "4-3-3", "4-2-3-1", "3-5-2"])
    
    # ===== SECTION 4: ATTAQUES =====
    with st.expander("🔄 Répartition attaques"):
        attaque_gauche = st.slider("Gauche %", 0, 100, 33)
        attaque_centre = st.slider("Centre %", 0, 100, 34)
        attaque_droite = st.slider("Droite %", 0, 100, 33)
    
    st.markdown("---")
    
    # ===== VALIDATION & CALCULS =====
    for erreur in valider_entrees(possession, tirs_equipe, tirs_adverses, score_equipe, score_adverses, minute):
        st.warning(erreur)
    
    xg_equipe = calcul_xg(tirs_equipe)
    xg_adverses = calcul_xg(tirs_adverses)
    domination = calcul_domination(tirs_equipe, possession, tirs_adverses)
    danger = calcul_danger(tirs_equipe, tirs_adverses, xg_equipe, xg_adverses, score_equipe, score_adverses, minute)
    fatigue = calcul_fatigue(minute, style_jeu)
    diff_score = int(score_equipe - score_adverses)
    score_ia = calcul_score_ia(domination, xg_equipe, xg_adverses, score_equipe, score_adverses, fatigue, danger, minute)
    
    # Phase
    if domination > 10 and xg_equipe > xg_adverses:
        phase = "attaque_placee"
    elif domination < -10:
        phase = "defense_subie"
    else:
        phase = "transition"
    
    phases_labels = {
        "attaque_placee": "⚔️ Attaque placée — Vous dominez",
        "defense_subie": "🛡️ Défense subie — Consolidez",
        "transition": "⚖️ Phase transition — Organisés",
    }
    
    # Côté dominant
    cote_dominant = "Gauche" if attaque_gauche > max(attaque_centre, attaque_droite) else \
                   "Droite" if attaque_droite > max(attaque_gauche, attaque_centre) else "Centre"
    
    # Profil
    profil_equipe_obj = ProfilEquipe(db)
    profil = profil_equipe_obj.charger_profil()
    historique = db.get_historique(limit=100)
    historique_30 = db.get_historique(limit=30)
    
    forme = calcul_forme_recente(db)
    momentum = calcul_momentum_persistant(db, score_ia)
    stats = db.get_stats_saison()
    
    # ===== TABLEAU DE BORD =====
    st.markdown("### 📊 TABLEAU DE BORD")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{round(score_ia, 1)}</div>
                <div class="metric-label">Score IA</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        danger_color = "danger" if danger > 2 else ("warning" if danger > 1 else "success")
        st.markdown(f"""
            <div class="metric-card {danger_color}">
                <div class="metric-value">{danger}/4</div>
                <div class="metric-label">Danger</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{xg_equipe}</div>
                <div class="metric-label">xG Équipe</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{minute}'</div>
                <div class="metric-label">Minute</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== ANALYSE & STRATÉGIE =====
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧠 ANALYSE")
        st.info(phases_labels[phase])
        st.caption(f"Momentum: {momentum['emoji']} {momentum.get('delta', 'N/A')}")
        st.caption(f"Forme: {forme['emoji']} {forme.get('record', '')}")
    
    with col2:
        st.markdown("### 🎯 STRATÉGIE")
        strategie = strategie_depuis_score(score_ia, danger, fatigue)
        st.success(strategie)
        st.caption(f"Côté dominant: **{cote_dominant}**")
    
    st.markdown("---")
    
    # ===== PRÉDICTION =====
    st.markdown("### 🔮 PRÉDICTION FIN DE MATCH")
    
    if minute < 90:
        prediction = predire_fin_match(score_ia, minute, historique_30)
        
        if prediction:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Score projeté", prediction['score_final_projete'])
            with col2:
                st.metric("Confiance", f"{prediction['confiance']}%")
            
            if prediction['prediction'] == "🟢 Victoire":
                st.success(f"{prediction['prediction']} en {prediction['minutes_restantes']}'")
            elif prediction['prediction'] == "🟡 Égalité":
                st.info(f"{prediction['prediction']} en {prediction['minutes_restantes']}'")
            else:
                st.error(f"{prediction['prediction']} en {prediction['minutes_restantes']}'")
    
    st.markdown("---")
    
    # ===== GRAPHIQUES =====
    st.markdown("### 📈 GRAPHIQUES")
    fig_radar = plot_radar_profil(profil)
    if fig_radar:
        st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("---")
    
    # ===== SAUVEGARDE =====
    st.markdown("### 💾 ENREGISTRER LE MATCH")
    
    notes = st.text_area("📝 Notes optionnelles", placeholder="Blessures, conditions, etc.", height=60)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Enregistrer", use_container_width=True):
            contexte_data = parser_notes_contexte(notes)
            
            data = {
                "possession": possession, "tirs_equipe": tirs_equipe, "tirs_adverses": tirs_adverses,
                "score_equipe": score_equipe, "score_adverses": score_adverses, "xg_equipe": xg_equipe,
                "xg_adverses": xg_adverses, "diff_score": diff_score, "score_ia": score_ia,
                "style_jeu": style_jeu, "systeme_adverse": systeme_adverse_analyse,
                "attaque_gauche": attaque_gauche, "attaque_centre": attaque_centre,
                "attaque_droite": attaque_droite, "minute": minute,
                "notes": notes, "contexte": contexte_data['resume']
            }
            
            if db.ajouter_match(data):
                invalider_cache_modele()
                st.success("✅ Match enregistré!")
            else:
                st.error("❌ Erreur")
    
    with col2:
        rapport = f"⚽ MATCH {datetime.now().strftime('%d/%m')}\n{int(score_equipe)}-{int(score_adverses)} | Score IA: {round(score_ia, 1)}\nSystème: {systeme_adverse_analyse}"
        st.download_button(
            "📥 Télécharger",
            data=rapport,
            file_name=f"match_{datetime.now().strftime('%d%m%H%M')}.txt",
            use_container_width=True,
            mime="text/plain"
        )

# =========================
# 📊 MODE HISTORIQUE
# =========================

elif mode == "📊 Historique":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1f3c72 0%, #2a5298 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="margin: 0; font-size: 20px;">Historique</h2>
            <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.8;">Tous vos matchs</p>
        </div>
    """, unsafe_allow_html=True)
    
    historique_complet = db.get_historique(limit=20)
    stats = db.get_stats_saison()
    
    if stats and stats[0] > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Matchs", int(stats[0]))
        with col2:
            record = f"{int(stats[5])}V-{int(stats[6])}N-{int(stats[7])}D"
            st.metric("📈 Record", record)
        with col3:
            st.metric("🎯 Possession", f"{round(stats[1], 1)}%")
        with col4:
            st.metric("⚽ xG moy", round(stats[3], 2))
        
        st.markdown("---")
        
        if historique_complet is not None and len(historique_complet) > 0:
            st.markdown("### Derniers matchs")
            historique_display = historique_complet[['date_match', 'score_equipe', 'score_adverses', 'possession', 'score_ia']].copy()
            historique_display.columns = ['Date', '🔵 Score', '🔴 Adv', 'Poss %', 'Score IA']
            historique_display['Date'] = pd.to_datetime(historique_display['Date']).dt.strftime('%d/%m %H:%M')
            
            for idx, row in historique_display.iterrows():
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.caption(row['Date'])
                with col2:
                    st.caption(f"{int(row['🔵 Score'])}")
                with col3:
                    st.caption(f"{int(row['🔴 Adv'])}")
                with col4:
                    st.caption(f"{int(row['Poss %'])}%")
                with col5:
                    couleur = "🟢" if row['Score IA'] > 0 else "🔴"
                    st.caption(f"{couleur} {round(row['Score IA'], 1)}")

# =========================
# ⚙️ MODE PARAMÈTRES
# =========================

elif mode == "⚙️ Paramètres":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1f3c72 0%, #2a5298 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="margin: 0; font-size: 20px;">Paramètres</h2>
            <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.8;">Configuration & Info</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧪 Tests de Fonctionnement")
    
    if st.button("▶️ Lancer les tests", use_container_width=True):
        tests_passed = 0
        
        try:
            assert calcul_xg(10) == 1.2
            st.success("✅ calcul_xg")
            tests_passed += 1
        except:
            st.error("❌ calcul_xg")
        
        try:
            danger = calcul_danger(5, 5, 0.6, 0.6, 1, 0, 45)
            assert 0 <= danger <= 4
            st.success("✅ calcul_danger")
            tests_passed += 1
        except:
            st.error("❌ calcul_danger")
        
        st.metric("Tests réussis", f"{tests_passed}/2", delta="100%" if tests_passed == 2 else "")
    
    st.markdown("---")
    
    st.markdown("### 📊 Actions Base de Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Réinitialiser modèle", use_container_width=True):
            invalider_cache_modele()
            st.success("✅ Modèle réinitialisé")
    
    with col2:
        if st.button("📥 Exporter historique", use_container_width=True):
            h_complet = db.get_historique(limit=10000)
            if h_complet is not None:
                csv = h_complet.to_csv(index=False)
                st.download_button(
                    "Télécharger CSV",
                    csv,
                    file_name=f"historique_{datetime.now().strftime('%Y%m%d')}.csv",
                    use_container_width=True,
                    mime="text/csv"
                )
    
    st.markdown("---")
    
    st.markdown("### ℹ️ Informations Système")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("📱 Version: 2.0 Pro Mobile")
        st.caption("📊 Base: SQLite")
        st.caption("⏱️ Heure serveur:", datetime.now().strftime("%H:%M:%S"))
    
    with col2:
        st.caption("🎯 Mode: Mobile-First")
        st.caption("📁 Logs: Active")
        st.caption("🔒 Data: Local Safe")

# =========================
# FOOTER
# =========================

st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 15px 0; color: #aaa; font-size: 12px;">
        <p>⚽ <strong>Coach IA Pro v2.0</strong> — Intelligence Tactique Football</p>
        <p style="margin-top: 5px; opacity: 0.6;">Mobile-First | Offline-Ready | Privacy-First</p>
    </div>
""", unsafe_allow_html=True)

logger.info("App session ended")
