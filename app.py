import streamlit as st
import pandas as pd
import os
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# =========================
# ⚙️ CONFIG
# =========================
st.set_page_config(page_title="Assistant Coach IA", layout="centered")
st.title("⚽ Assistant Coach IA")

DATA_FILE = "data_matchs.csv"

# =========================
# 🔧 UTILITAIRES
# =========================

def contre_systeme(sys: str) -> str:
    table = {
        "4-3-3":   "4-2-3-1",
        "4-4-2":   "3-5-2",
        "3-5-2":   "4-3-3",
        "4-2-3-1": "4-4-2",
        "5-3-2":   "4-3-3",
    }
    return table.get(sys, "4-3-3")


def calcul_xg(tirs: int) -> float:
    return round(tirs * 0.12, 2)


def calcul_domination(tirs_eq: int, possession: int, tirs_adv: int) -> float:
    return (tirs_eq * 4 + possession * 0.4) - (tirs_adv * 4)


def calcul_danger(tirs_eq, tirs_adv, xg_eq, xg_adv, score_eq, score_adv, minute) -> int:
    danger = 0
    if tirs_adv > tirs_eq:    danger += 1
    if xg_adv > xg_eq:        danger += 1
    if score_eq <= score_adv: danger += 1
    if minute > 70:            danger += 1
    return danger


def calcul_fatigue(minute: int, style_jeu: str) -> int:
    fatigue = 0
    if minute > 60:             fatigue += 1
    if style_jeu == "Pressing": fatigue += 2
    return fatigue


def calcul_score_ia(domination, xg_eq, xg_adv, score_eq, score_adv, fatigue, danger) -> float:
    return (
        domination * 0.5
        + (xg_eq - xg_adv) * 10
        + (score_eq - score_adv) * 15
        - fatigue * 10
        - danger * 8
    )


def strategie_depuis_score(score_ia: float) -> str:
    if score_ia < -25:  return "🛡️ Bloc bas"
    elif score_ia < 0:  return "🔒 Défensif"
    elif score_ia < 25: return "⚖️ Équilibre"
    else:               return "⚔️ Offensif"


# =========================
# 🧠 CHARGEMENT DU MODÈLE ML
# =========================

@st.cache_resource
def charger_modele(chemin: str):
    if not os.path.exists(chemin):
        return None, None

    historique = pd.read_csv(chemin)
    if len(historique) < 30:
        return None, None

    historique["resultat"] = (historique["score_ia"] > 0).astype(int)
    features = ["possession", "tirs_equipe", "tirs_adverses", "xg_equipe", "xg_adverses"]
    X = historique[features]
    y = historique["resultat"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modele = RandomForestClassifier(n_estimators=100, random_state=42)
    modele.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, modele.predict(X_test))
    return modele, accuracy


def invalider_cache_modele():
    charger_modele.clear()


# =========================
# 🎮 MODE
# =========================
mode = st.radio("Mode d'utilisation", ["⚡ Mode rapide", "🧠 Mode analyse"])

# =========================
# ⚡ MODE RAPIDE
# =========================
if mode == "⚡ Mode rapide":

    st.subheader("⚡ Assistant banc de touche")

    col1, col2 = st.columns(2)
    with col1:
        score     = st.selectbox("Score",     ["Gagne", "Égalité", "Perd"])
        dynamique = st.selectbox("Dynamique", ["On domine", "Équilibré", "On subit"])
    with col2:
        minute          = st.slider("Minute", 0, 90, 60)
        systeme_adverse = st.selectbox(
            "Système adverse",
            ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "5-3-2"]
        )

    suggestion = contre_systeme(systeme_adverse)
    st.divider()

    if score == "Perd" and dynamique == "On subit":
        st.error(f"🔴 URGENCE : bloc bas + passer en **{suggestion}**")
    elif score == "Perd" and dynamique == "On domine":
        st.warning(f"🟠 Domination stérile → passer en **{suggestion}**")
    elif score == "Perd" and dynamique == "Équilibré":
        st.warning(f"🟠 Chercher le but → hausser le pressing, envisager **{suggestion}**")
    elif score == "Égalité" and dynamique == "On domine":
        st.info("🟡 Augmenter le rythme + pressing haut")
    elif score == "Égalité" and dynamique == "On subit":
        st.warning(f"🟠 Sécuriser : reculer le bloc, tenter **{suggestion}**")
    elif score == "Gagne" and dynamique == "On subit":
        st.warning("🟠 Renforcer le milieu + gérer le ballon")
    elif score == "Gagne" and dynamique == "On domine":
        st.success("🟢 Parfait — maintenir l'intensité")
    else:
        st.success("🟢 Match sous contrôle")

    if minute > 75 and score != "Gagne":
        st.error("⏱️ Fin de match imminente → prendre des risques calculés !")

# =========================
# 🧠 MODE ANALYSE
# =========================
else:

    st.subheader("🧠 Analyse complète")

    col1, col2 = st.columns(2)
    with col1:
        possession     = st.slider("Possession (%)", 0, 100, 50)
        tirs_equipe    = st.number_input("Tirs équipe",   0, 30, 5)
        tirs_adverses  = st.number_input("Tirs adverses", 0, 30, 5)
        score_equipe   = st.number_input("Score équipe",  0, 10, 0)
        score_adverses = st.number_input("Score adverse", 0, 10, 0)
    with col2:
        minute         = st.slider("Minute", 0, 90, 45)
        attaque_gauche = st.slider("Attaques côté gauche (%)", 0, 100, 33)
        attaque_centre = st.slider("Attaques centre (%)",      0, 100, 34)
        attaque_droite = st.slider("Attaques côté droit (%)",  0, 100, 33)
        style_jeu      = st.selectbox(
            "Style de jeu",
            ["Adaptatif (IA)", "Possession", "Pressing", "Défensif", "Transition rapide"]
        )

    total_attaques = attaque_gauche + attaque_centre + attaque_droite
    if total_attaques != 100:
        st.warning(f"⚠️ La répartition des attaques totalise {total_attaques}% (doit être 100%)")

    # --- CALCULS ---
    xg_equipe   = calcul_xg(tirs_equipe)
    xg_adverses = calcul_xg(tirs_adverses)
    domination  = calcul_domination(tirs_equipe, possession, tirs_adverses)
    danger      = calcul_danger(tirs_equipe, tirs_adverses, xg_equipe, xg_adverses,
                                score_equipe, score_adverses, minute)
    fatigue     = calcul_fatigue(minute, style_jeu)
    score_ia    = calcul_score_ia(domination, xg_equipe, xg_adverses,
                                  score_equipe, score_adverses, fatigue, danger)

    # --- PHASE DE JEU ---
    if domination > 10 and xg_equipe > xg_adverses:
        phase = "attaque_placee"
    elif domination < -10:
        phase = "defense_subie"
    else:
        phase = "transition"

    # --- CÔTÉ DOMINANT ---
    cote_dominant = (
        "Gauche" if attaque_gauche > attaque_droite and attaque_gauche > attaque_centre
        else "Droite" if attaque_droite > attaque_gauche and attaque_droite > attaque_centre
        else "Centre"
    )

    # --- MODÈLE ML ---
    modele, accuracy = charger_modele(DATA_FILE)
    prediction, proba_prediction = None, None

    if modele is not None:
        X_pred           = [[possession, tirs_equipe, tirs_adverses, xg_equipe, xg_adverses]]
        prediction       = modele.predict(X_pred)[0]
        proba_prediction = modele.predict_proba(X_pred)[0][prediction]

    # --- STRATÉGIE ---
    if prediction is not None:
        strategie = "⚔️ Exploiter l'avantage" if prediction == 1 else "🛡️ Sécuriser le jeu"
    else:
        strategie = strategie_depuis_score(score_ia)

    # --- PROBABILITÉ DE BUT ---
    if prediction is not None:
        proba_but = round(proba_prediction * 100) if prediction == 1 else round((1 - proba_prediction) * 100)
    else:
        proba_but = max(0, min(100, int(xg_equipe * 50 + domination * 0.5)))

    # --- AFFICHAGE ---
    st.divider()

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Score IA",  round(score_ia, 1))
    col_b.metric("Danger",    f"{danger} / 4")
    col_c.metric("xG équipe vs adverse", f"{xg_equipe} / {xg_adverses}")

    st.subheader("🧠 Phase de jeu détectée")
    phases_labels = {
        "attaque_placee": "⚔️ Attaque placée — vous dominez, continuez à presser",
        "defense_subie":  "🛡️ Défense subie — consolidez le bloc",
        "transition":     "⚖️ Phase de transition — restez organisés",
    }
    st.info(phases_labels[phase])

    # =========================
    # 🎮 SIMULATION RÉALISTE
    # =========================
    simulation = []
    for i in range(3):
        if phase == "attaque_placee":
            chance = proba_but + 10
        elif phase == "defense_subie":
            chance = proba_but - 15
        else:
            chance = proba_but
        if random.randint(0, 100) < chance:
            simulation.append("⚽ Occasion dangereuse")
        else:
            simulation.append("➡️ Phase neutre")

    st.subheader("🎮 Simulation des prochaines actions")
    for action in simulation:
        st.write(action)

    st.subheader("🎯 Stratégie recommandée")
    st.success(strategie)

    st.subheader("📍 Côté dominant de vos attaques")
    st.info(f"Vous attaquez principalement par le **{cote_dominant}** — pensez à varier !")

    if modele is not None:
        st.subheader("🧠 IA avancée (Random Forest)")
        if prediction == 1:
            st.success(f"Situation favorable — confiance : **{round(proba_prediction*100)}%**")
        else:
            st.error(f"Situation défavorable — confiance : **{round(proba_prediction*100)}%**")
        st.caption(f"Précision du modèle sur données de test : {round(accuracy*100, 1)}%")
    else:
        nb_matchs = len(pd.read_csv(DATA_FILE)) if os.path.exists(DATA_FILE) else 0
        st.info(f"🧠 IA avancée disponible après 30 matchs enregistrés ({nb_matchs}/30 actuellement)")

    st.subheader("🔮 Probabilité de but")
    st.progress(proba_but)
    st.write(f"{proba_but}%")

    st.subheader("📈 Domination globale")
    domination_progress = max(0, min(100, int((score_ia + 50))))
    st.progress(domination_progress)

    # --- SAUVEGARDE ---
    st.divider()
    if st.button("💾 Enregistrer ce match"):
        data = {
            "possession":     possession,
            "tirs_equipe":    tirs_equipe,
            "tirs_adverses":  tirs_adverses,
            "score_equipe":   score_equipe,
            "score_adverses": score_adverses,
            "xg_equipe":      xg_equipe,
            "xg_adverses":    xg_adverses,
            "score_ia":       score_ia,
        }
        df = pd.DataFrame([data])

        if os.path.exists(DATA_FILE):
            df.to_csv(DATA_FILE, mode="a", header=False, index=False)
        else:
            df.to_csv(DATA_FILE, index=False)

        invalider_cache_modele()
        st.success("✅ Match enregistré — modèle IA mis à jour au prochain chargement.")
