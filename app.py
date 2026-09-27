"""Local UI for the decomposition experiment.

    uv run streamlit run app.py

Tabs: try a sentence live, browse the results, inspect posts where arms disagree.
Reuses analyze.py so every number matches results/summary.md.
"""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LogisticRegression
from typesafe_sdk import TypeSafeClient

from analyze import ARMS, COMPARISONS, LANGS, METRICS, load, logit, predictions
from questions import ATOMIC_KEYS, QUESTION_SETS
from run import MODEL, load_api_key

st.set_page_config(page_title="Ayrıştırma Paradoksu", layout="wide")

LANG_NAMES = {"tr": "Türkçe (OffensEval-TR)", "en": "İngilizce (OLID)"}
ARM_DESC = {
    "B-raw": "Tanımsız tek soru",
    "B-fit": "Tanımsız tek soru, ayarlı",
    "M-raw": "Tanımlı tek soru",
    "M-fit": "Tanımlı tek soru, ayarlı",
    "D-noisyor": "5 atomik soru, basit birleştirme (etiketsiz)",
    "D-fit": "5 atomik soru, ayarlı ağırlıklar",
    "MD-fit": "Tanım + 5 atomik, ayarlı",
}
ATOMIC_TR = {
    "profanity": "Küfür",
    "insult": "Hakaret",
    "threat": "Tehdit",
    "identity_attack": "Kimlik saldırısı",
    "veiled": "Örtük saldırı",
}


@st.cache_data
def lang_data(lang: str) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    df = load(lang)
    texts = pd.read_csv(f"data/sample_{lang}.csv", dtype={"id": str})[["id", "text"]]
    df = df.merge(texts, on="id", how="left")
    return df, predictions(df)


@st.cache_data
def metrics_table() -> pd.DataFrame:
    return pd.read_csv("results/metrics.csv")


@st.cache_resource
def fitted_models(lang: str) -> dict[str, LogisticRegression]:
    """Fit on all 1,000 posts of a language, for scoring new sentences."""
    df, _ = lang_data(lang)
    y = df["label"].to_numpy()
    return {
        "M-fit": LogisticRegression().fit(logit(df["offensive"].to_numpy())[:, None], y),
        "D-fit": LogisticRegression().fit(logit(df[ATOMIC_KEYS].to_numpy()), y),
    }


@st.cache_resource
def client() -> TypeSafeClient:
    load_api_key()
    return TypeSafeClient(model=MODEL)


# ---------------------------------------------------------------------------

st.title("Ayrıştırma Paradoksu")
st.caption(
    "Jev'de bir soruyu 5 atomik soruya bölmek işe yarıyor mu? "
    "İngilizce ve Türkçe, dil başına 1.000 tweet, `jev-1.13.0`."
)

tab_try, tab_results, tab_examples = st.tabs(["🧪 Dene", "📊 Sonuçlar", "🔍 Örnekler"])

# --- Try --------------------------------------------------------------------
with tab_try:
    left, right = st.columns([3, 2])
    with left:
        text = st.text_area(
            "Bir cümle yazın (Türkçe veya İngilizce)",
            "Bu maçı kaybettiren hakemi kimse ciddiye almıyor zaten, yazık.",
            height=110,
        )
    with right:
        weights_lang = st.radio(
            "Ayarlı kollar hangi dilin verisiyle ayarlansın?",
            LANGS,
            format_func=LANG_NAMES.get,
            index=LANGS.index("tr"),
            horizontal=True,
        )
        st.caption("Her deneme 2 istek gönderir, maliyeti yaklaşık 0,00004 $.")
        go = st.button("Jev'e sor", type="primary", use_container_width=True)

    if go and text.strip():
        with st.spinner("Jev yanıtlıyor..."):
            state = {"post": text.strip()}
            main = client().system_one(state, QUESTION_SETS["main"])
            bare = client().system_one(state, QUESTION_SETS["bare"])
        n = {**{k: v.noul for k, v in main.nouls.items()},
             **{k: v.noul for k, v in bare.nouls.items()}}
        A = np.array([[n[k] for k in ATOMIC_KEYS]])
        models = fitted_models(weights_lang)
        arms = {
            "B-raw": n["offensive_bare"],
            "M-raw": n["offensive"],
            "M-fit": models["M-fit"].predict_proba(logit(np.array([[n["offensive"]]])))[0, 1],
            "D-noisyor": 1 - np.prod(1 - A),
            "D-fit": models["D-fit"].predict_proba(logit(A))[0, 1],
        }

        st.subheader("Kollar: P(saldırgan)")
        arm_df = pd.DataFrame(
            {"kol": list(arms), "açıklama": [ARM_DESC[a] for a in arms], "olasılık": list(arms.values())}
        )
        base = alt.Chart(arm_df).encode(
            x=alt.X("olasılık:Q", scale=alt.Scale(domain=[0, 1]), title="P(saldırgan)"),
            y=alt.Y("açıklama:N", sort=list(arm_df["açıklama"]), title=None,
                    axis=alt.Axis(labelLimit=400)),
        )
        bars = base.mark_bar().encode(
            color=alt.condition("datum.olasılık >= 0.5", alt.value("#d1495b"), alt.value("#66a182")),
            tooltip=["kol", alt.Tooltip("olasılık:Q", format=".2f")],
        )
        labels = base.mark_text(align="left", dx=4, color="#ddd").encode(
            text=alt.Text("olasılık:Q", format=".2f")
        )
        rule = alt.Chart(pd.DataFrame({"x": [0.5]})).mark_rule(
            strokeDash=[4, 4], color="#999").encode(x="x:Q")
        st.altair_chart(bars + labels + rule, use_container_width=True)

        st.subheader("Atomik sorular")
        atom_df = pd.DataFrame(
            {"soru": [ATOMIC_TR[k] for k in ATOMIC_KEYS], "olasılık": A[0]}
        )
        st.altair_chart(
            alt.Chart(atom_df).mark_bar(color="#8d6cab").encode(
                x=alt.X("olasılık:Q", scale=alt.Scale(domain=[0, 1]), title="P(evet)"),
                y=alt.Y("soru:N", sort=None, title=None, axis=alt.Axis(labelLimit=400)),
                tooltip=[alt.Tooltip("olasılık:Q", format=".2f")],
            ),
            use_container_width=True,
        )
        if arms["D-noisyor"] - arms["D-fit"] > 0.25:
            st.info(
                "Basit birleştirme ayarlı kolun çok üstünde. Bu deneydeki ana "
                "bulgu: atomik cevaplar birbiriyle ilişkili olduğu için noisy-OR "
                "aynı kanıtı birden çok sayıp aşırı özgüvenli oluyor."
            )

# --- Results ----------------------------------------------------------------
with tab_results:
    m = metrics_table()
    metric = st.selectbox(
        "Metrik",
        list(METRICS),
        format_func={
            "accuracy": "Doğruluk", "macro_f1": "Makro F1", "auc": "AUC (sıralama)",
            "ece": "ECE (kalibrasyon hatası, düşük iyi)", "brier": "Brier (düşük iyi)",
        }.get,
    )
    sub = m[m.metric == metric].copy()
    sub["kol"] = sub["arm"].map(ARM_DESC)
    sub["dil"] = sub["lang"].map({"tr": "Türkçe", "en": "İngilizce"})
    chart = alt.Chart(sub).encode(
        y=alt.Y("kol:N", sort=[ARM_DESC[a] for a in ARMS], title=None,
                axis=alt.Axis(labelLimit=400)),
        yOffset="dil:N",
        color=alt.Color("dil:N", scale=alt.Scale(range=["#3a6ea5", "#e07a5f"])),
    )
    st.altair_chart(
        chart.mark_rule().encode(x=alt.X("lo:Q", title=metric, scale=alt.Scale(zero=False)), x2="hi:Q")
        + chart.mark_point(filled=True, size=70).encode(
            x="value:Q", tooltip=["dil", "kol", alt.Tooltip("value:Q", format=".3f")]
        ),
        use_container_width=True,
    )
    st.caption("Çizgiler %95 bootstrap güven aralığı.")

    st.subheader("Kalibrasyon")
    rel_lang = st.radio("Dil", LANGS, format_func=LANG_NAMES.get, index=LANGS.index("tr"), horizontal=True, key="rel")
    df, preds = lang_data(rel_lang)
    y = df["label"].to_numpy()
    shown = st.multiselect(
        "Kollar", ARMS, default=["B-raw", "M-raw", "D-noisyor", "D-fit"], format_func=ARM_DESC.get
    )
    edges = np.linspace(0, 1, 11)
    rows = []
    for arm in shown:
        p = preds[arm]
        idx = np.minimum(np.digitize(p, edges) - 1, 9)
        for b in range(10):
            mask = idx == b
            if mask.sum() >= 10:
                rows.append(dict(kol=ARM_DESC[arm], tahmin=p[mask].mean(),
                                 gerçek=y[mask].mean(), n=int(mask.sum())))
    diag = alt.Chart(pd.DataFrame({"a": [0, 1]})).mark_line(
        strokeDash=[4, 4], color="#999").encode(x="a:Q", y="a:Q")
    rel = alt.Chart(pd.DataFrame(rows)).mark_line(point=True).encode(
        x=alt.X("tahmin:Q", title="Tahmin edilen P(saldırgan)", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("gerçek:Q", title="Gerçekte saldırgan oranı", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("kol:N", title=None, legend=alt.Legend(labelLimit=400, orient="bottom", columns=2)),
        tooltip=["kol", alt.Tooltip("tahmin:Q", format=".2f"),
                 alt.Tooltip("gerçek:Q", format=".2f"), "n"],
    )
    st.altair_chart((diag + rel).properties(height=420), use_container_width=True)
    st.caption("Köşegenin altı = aşırı özgüven, üstü = eksik özgüven.")

    st.subheader("Etkiler")
    st.markdown(open("results/summary.md").read().split("## Effects")[1].split("\n", 1)[1])

# --- Examples ---------------------------------------------------------------
with tab_examples:
    ex_lang = st.radio("Dil", LANGS, format_func=LANG_NAMES.get, index=LANGS.index("tr"), horizontal=True, key="ex")
    df, preds = lang_data(ex_lang)
    y = df["label"].to_numpy()
    right = {arm: (preds[arm] >= 0.5) == y for arm in ARMS}
    filters = {
        "Tanım işe yaradı: tanımsız yanlış, tanımlı doğru": ~right["B-raw"] & right["M-raw"],
        "Bölmek işe yaradı: tanımlı yanlış, bölünmüş+ayarlı doğru": ~right["M-fit"] & right["D-fit"],
        "Bölmek zarar verdi: tanımlı doğru, bölünmüş+ayarlı yanlış": right["M-fit"] & ~right["D-fit"],
        "Basit birleştirme yanlış alarm verdi": (preds["D-noisyor"] >= 0.5) & (y == 0),
        "Hepsi yanlış (etiket hatası olabilir)": np.all([~right[a] for a in ARMS], axis=0),
    }
    choice = st.selectbox("Filtre", list(filters))
    mask = filters[choice]
    st.caption(f"{mask.sum()} tweet · toplam {len(df)}")

    view = pd.DataFrame({
        "tweet": df["text"],
        "etiket": np.where(y == 1, "OFF", "NOT"),
        **{a: preds[a].round(2) for a in ["B-raw", "M-raw", "D-noisyor", "D-fit"]},
        **{ATOMIC_TR[k]: df[k] for k in ATOMIC_KEYS},
    })[mask]
    view = view.reindex((view["M-raw"] - view["D-fit"]).abs().sort_values(ascending=False).index)
    st.dataframe(
        view,
        hide_index=True,
        use_container_width=True,
        column_config={
            c: st.column_config.ProgressColumn(c, min_value=0, max_value=1, format="%.2f")
            for c in ["B-raw", "M-raw", "D-noisyor", "D-fit"]
        } | {"tweet": st.column_config.TextColumn(width=520)},
    )
