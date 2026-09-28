"""Local UI for the decomposition experiment.

    uv run streamlit run app.py

Sidebar picks the task (tweets / phishing), the model and the language.
Tabs: compare models and inspect one model's results, browse items where arms
disagree, and try Jev live. Reuses analyze.py so every number matches the
summary.md files.
"""

import json
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LogisticRegression
from typesafe_sdk import TypeSafeClient

from analyze import ARMS, METRICS, RESULTS, load, logit, predictions
from questions import TASKS, state_of
from run import MODEL, load_api_key

st.set_page_config(page_title="Ayrıştırma Paradoksu", layout="wide")

TASK_NAMES = {"offense": "Saldırgan tweet (Faz 1-3)", "phish": "Phishing e-postası (Faz 4)"}
BACKENDS = {"jev": "Jev", "laya": "Laya", "qwen": "Qwen3.5-9B", "openjev": "OpenJev"}
BACKEND_DESC = {
    "jev": "TypeSafe'in kapalı karar modeli (`jev-1.13.0`)",
    "laya": "Açık encoder, ModernBERT tabanlı, çok dilli",
    "qwen": "Açık decoder LLM, logprob hilesiyle karar modeline çevrildi",
    "openjev": "Açık encoder, DeBERTa-v3-large, sadece İngilizce",
}
LANG_NAMES = {
    "offense": {"tr": "Türkçe (OffensEval-TR)", "en": "İngilizce (OLID)"},
    "phish": {"en": "İngilizce (PhishNChips)"},
}
POSITIVE_TR = {"offense": "saldırgan", "phish": "phishing"}
ITEM_TR = {"offense": "tweet", "phish": "e-posta"}
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
    "sig_domain_mismatch": "Domain uyuşmazlığı",
    "sig_free_hosting": "Ücretsiz hosting / kısaltıcı",
    "sig_lure": "Giriş / doğrulama isteği",
    "sig_urgency": "Aciliyet / tehdit",
    "sig_generic_sender": "Genel webmail göndereni",
}
METRIC_NAMES = {
    "accuracy": "Doğruluk", "macro_f1": "Makro F1", "auc": "AUC (sıralama)",
    "ece": "ECE (kalibrasyon hatası, düşük iyi)", "brier": "Brier (düşük iyi)",
}
LOWER_IS_BETTER = {"ece", "brier"}


def results_dir(backend: str, task: str) -> Path:
    base = RESULTS if backend == "jev" else RESULTS / backend
    return base / TASKS[task]["subdir"]


def lines(path: Path) -> int:
    return sum(1 for _ in path.open()) if path.exists() else 0


def available(backend: str, task: str) -> bool:
    """Both raw files for every language exist, have rows and cover the same items."""
    d = results_dir(backend, task)
    for lang in TASKS[task]["langs"]:
        n_main, n_bare = lines(d / f"raw_{lang}.jsonl"), lines(d / f"raw_{lang}_bare.jsonl")
        if not n_main or n_main != n_bare:
            return False
    return (d / "metrics.csv").exists()


@st.cache_data
def item_data(backend: str, task: str, lang: str) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base = RESULTS if backend == "jev" else RESULTS / backend
    df = load(lang, base, task)
    texts = pd.read_csv(TASKS[task]["data"].format(lang=lang), dtype={"id": str})[["id", "text"]]
    df = df.merge(texts, on="id", how="left")
    return df, predictions(df, task)


@st.cache_data
def metrics_table(backend: str, task: str) -> pd.DataFrame:
    return pd.read_csv(results_dir(backend, task) / "metrics.csv")


@st.cache_resource
def fitted_models(task: str, lang: str) -> dict[str, LogisticRegression]:
    """Fit on all of Jev's items for this task and language, for scoring new inputs."""
    spec = TASKS[task]
    df, _ = item_data("jev", task, lang)
    y = df["label"].to_numpy()
    return {
        "M-fit": LogisticRegression().fit(logit(df[spec["mono"]].to_numpy())[:, None], y),
        "D-fit": LogisticRegression().fit(logit(df[spec["atomic"]].to_numpy()), y),
    }


@st.cache_resource
def client() -> TypeSafeClient:
    load_api_key()
    return TypeSafeClient(model=MODEL)


def show_text(task: str, text: str) -> str:
    if task == "offense":
        return text
    e = json.loads(text)
    return f"{e['from']} → {e['link_url']} · {e['subject']}"


# --- Sidebar ------------------------------------------------------------------

with st.sidebar:
    st.header("Ayarlar")
    task = st.radio("Görev", list(TASK_NAMES), format_func=TASK_NAMES.get, key="task")
    ready = [b for b in BACKENDS if available(b, task)]
    if st.session_state.get("backend") not in ready:
        st.session_state["backend"] = ready[0]
    backend = st.radio(
        "Model", ready, format_func=BACKENDS.get,
        captions=[BACKEND_DESC[b] for b in ready], key="backend",
    )
    langs = TASKS[task]["langs"]
    if st.session_state.get("lang") not in langs:
        st.session_state["lang"] = "tr" if "tr" in langs else langs[0]
    lang = st.radio("Dil", langs, format_func=LANG_NAMES[task].get, key="lang")
    missing = [BACKENDS[b] for b in BACKENDS if b not in ready]
    if missing:
        st.caption("Bu görevde sonucu olmayan: " + ", ".join(missing))
    if task == "phish" and "qwen" in ready:
        st.caption("Qwen phishing'de 500 e-postalık dengeli alt kümede çalıştı, diğerleri 2.000'de.")

pos = POSITIVE_TR[task]
st.title("Ayrıştırma Paradoksu")
st.caption(
    "Bir karar modeline soruyu tek seferde mi, 5 atomik soruya bölerek mi sormak daha iyi? "
    f"Görev: **{TASK_NAMES[task]}** · Model: **{BACKENDS[backend]}**"
)

tab_results, tab_examples, tab_try = st.tabs(["📊 Sonuçlar", "🔍 Örnekler", "🧪 Dene (Jev)"])

# --- Results ------------------------------------------------------------------
with tab_results:
    metric = st.selectbox("Metrik", list(METRICS), format_func=METRIC_NAMES.get, key="metric")

    st.subheader("Modelleri karşılaştır")
    rows = []
    for b in ready:
        m = metrics_table(b, task)
        m = m[(m.metric == metric) & (m.lang == lang)]
        for r in m.itertuples():
            rows.append(dict(model=BACKENDS[b], kol=ARM_DESC[r.arm], değer=r.value, n=r.n))
    grid = pd.DataFrame(rows)
    order = [ARM_DESC[a] for a in ARMS]
    heat = alt.Chart(grid).encode(
        x=alt.X("model:N", sort=[BACKENDS[b] for b in ready], title=None, axis=alt.Axis(labelAngle=0, orient="top")),
        y=alt.Y("kol:N", sort=order, title=None, axis=alt.Axis(labelLimit=400)),
    )
    st.altair_chart(
        (heat.mark_rect().encode(
            color=alt.Color("değer:Q", scale=alt.Scale(scheme="redyellowgreen", reverse=metric in LOWER_IS_BETTER),
                            legend=None),
            tooltip=["model", "kol", alt.Tooltip("değer:Q", format=".3f"), "n"],
        ) + heat.mark_text(fontSize=13).encode(
            text=alt.Text("değer:Q", format=".3f"),
            color=alt.value("black"),
        )).properties(height=300),
        width="stretch",
    )
    notes = [f"{LANG_NAMES[task][lang]}, {METRIC_NAMES[metric].lower()}."]
    if grid["n"].nunique() > 1:
        notes.append("Modeller farklı sayıda örnekte ölçüldü (sütun başına n, fareyle üzerine gelince görünür).")
    st.caption(" ".join(notes))

    st.subheader(f"{BACKENDS[backend]}: güven aralıkları")
    m = metrics_table(backend, task)
    sub = m[m.metric == metric].copy()
    sub["kol"] = sub["arm"].map(ARM_DESC)
    sub["dil"] = sub["lang"].map({"tr": "Türkçe", "en": "İngilizce"})
    chart = alt.Chart(sub).encode(
        y=alt.Y("kol:N", sort=order, title=None, axis=alt.Axis(labelLimit=400)),
        yOffset="dil:N",
        color=alt.Color("dil:N", scale=alt.Scale(range=["#3a6ea5", "#e07a5f"])),
    )
    st.altair_chart(
        chart.mark_rule().encode(x=alt.X("lo:Q", title=METRIC_NAMES[metric], scale=alt.Scale(zero=False)), x2="hi:Q")
        + chart.mark_point(filled=True, size=70).encode(
            x="value:Q", tooltip=["dil", "kol", alt.Tooltip("value:Q", format=".3f")]
        ),
        width="stretch",
    )
    st.caption("Çizgiler %95 bootstrap güven aralığı.")

    st.subheader(f"{BACKENDS[backend]}: kalibrasyon")
    df, preds = item_data(backend, task, lang)
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
    if rows:
        diag = alt.Chart(pd.DataFrame({"a": [0, 1]})).mark_line(
            strokeDash=[4, 4], color="#999").encode(x="a:Q", y="a:Q")
        rel = alt.Chart(pd.DataFrame(rows)).mark_line(point=True).encode(
            x=alt.X("tahmin:Q", title=f"Tahmin edilen P({pos})", scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("gerçek:Q", title=f"Gerçekte {pos} oranı", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("kol:N", title=None, legend=alt.Legend(labelLimit=400, orient="bottom", columns=2)),
            tooltip=["kol", alt.Tooltip("tahmin:Q", format=".2f"),
                     alt.Tooltip("gerçek:Q", format=".2f"), "n"],
        )
        st.altair_chart((diag + rel).properties(height=420), width="stretch")
    st.caption("Köşegenin altı = aşırı özgüven, üstü = eksik özgüven. En az 10 örnek içeren aralıklar gösteriliyor.")

    st.subheader(f"{BACKENDS[backend]}: etkiler")
    summary = (results_dir(backend, task) / "summary.md").read_text()
    st.markdown(summary.split("## Effects")[1].split("\n", 1)[1])

# --- Examples -----------------------------------------------------------------
with tab_examples:
    spec = TASKS[task]
    df, preds = item_data(backend, task, lang)
    y = df["label"].to_numpy()
    right = {arm: (preds[arm] >= 0.5) == y for arm in ARMS}
    filters = {
        "Tanım işe yaradı: tanımsız yanlış, tanımlı doğru": ~right["B-raw"] & right["M-raw"],
        "Bölmek işe yaradı: tanımlı yanlış, bölünmüş+ayarlı doğru": ~right["M-fit"] & right["D-fit"],
        "Bölmek zarar verdi: tanımlı doğru, bölünmüş+ayarlı yanlış": right["M-fit"] & ~right["D-fit"],
        "Basit birleştirme yanlış alarm verdi": (preds["D-noisyor"] >= 0.5) & (y == 0),
        "Hepsi yanlış (etiket hatası olabilir)": np.all([~right[a] for a in ARMS], axis=0),
    }
    choice = st.selectbox("Filtre", list(filters), key="filter")
    mask = filters[choice]
    st.caption(f"{BACKENDS[backend]} · {mask.sum()} {ITEM_TR[task]} · toplam {len(df)}")

    labels = ("OFF", "NOT") if task == "offense" else ("phishing", "meşru")
    view = pd.DataFrame({
        ITEM_TR[task]: df["text"].map(lambda t: show_text(task, t)),
        "etiket": np.where(y == 1, *labels),
        **{a: preds[a].round(2) for a in ["B-raw", "M-raw", "D-noisyor", "D-fit"]},
        **{ATOMIC_TR[k]: df[k] for k in spec["atomic"]},
    })[mask]
    view = view.reindex((view["M-raw"] - view["D-fit"]).abs().sort_values(ascending=False).index)
    st.dataframe(
        view,
        hide_index=True,
        width="stretch",
        column_config={
            c: st.column_config.ProgressColumn(c, min_value=0, max_value=1, format="%.2f")
            for c in ["B-raw", "M-raw", "D-noisyor", "D-fit"]
        } | {ITEM_TR[task]: st.column_config.TextColumn(width=520)},
    )

# --- Try ----------------------------------------------------------------------
with tab_try:
    st.caption(
        "Canlı deneme sadece Jev ile yapılabiliyor: Laya, Qwen ve OpenJev ağır yerel "
        "kütüphaneler istiyor. Ayarlı kollar Jev'in bu görevdeki verisiyle ayarlanır. "
        "Her deneme 2 istek gönderir."
    )
    spec = TASKS[task]
    if task == "offense":
        text = st.text_area("Bir cümle yazın (Türkçe veya İngilizce)",
                            "Bu maçı kaybettiren hakemi kimse ciddiye almıyor zaten, yazık.", height=110)
        state = {"post": text.strip()} if text.strip() else None
    else:
        c1, c2 = st.columns(2)
        email = {
            "from": c1.text_input("from", "security@paypa1-support.com"),
            "sender": c2.text_input("sender", "PayPal Security Team"),
            "link_url": c1.text_input("link_url", "https://bit.ly/3xVerify"),
            "link_display_text": c2.text_input("link_display_text", "Verify your account"),
            "subject": st.text_input("subject", "Action required: unusual sign-in detected"),
            "body": st.text_area("body", "We noticed an unusual sign-in to your account. Verify your "
                                 "identity within 24 hours or your account will be suspended.", height=110),
        }
        state = state_of(task, json.dumps(email))
    go = st.button("Jev'e sor", type="primary")

    if go and state:
        with st.spinner("Jev yanıtlıyor..."):
            main = client().system_one(state, spec["sets"]["main"])
            bare = client().system_one(state, spec["sets"]["bare"])
        n = {**{k: v.noul for k, v in main.nouls.items()},
             **{k: v.noul for k, v in bare.nouls.items()}}
        A = np.array([[n[k] for k in spec["atomic"]]])
        models = fitted_models(task, lang)
        arms = {
            "B-raw": n[spec["bare"]],
            "M-raw": n[spec["mono"]],
            "M-fit": models["M-fit"].predict_proba(logit(np.array([[n[spec["mono"]]]])))[0, 1],
            "D-noisyor": 1 - np.prod(1 - A),
            "D-fit": models["D-fit"].predict_proba(logit(A))[0, 1],
        }

        st.subheader(f"Kollar: P({pos})")
        arm_df = pd.DataFrame(
            {"kol": list(arms), "açıklama": [ARM_DESC[a] for a in arms], "olasılık": list(arms.values())}
        )
        base = alt.Chart(arm_df).encode(
            x=alt.X("olasılık:Q", scale=alt.Scale(domain=[0, 1]), title=f"P({pos})"),
            y=alt.Y("açıklama:N", sort=list(arm_df["açıklama"]), title=None, axis=alt.Axis(labelLimit=400)),
        )
        bars = base.mark_bar().encode(
            color=alt.condition("datum.olasılık >= 0.5", alt.value("#d1495b"), alt.value("#66a182")),
            tooltip=["kol", alt.Tooltip("olasılık:Q", format=".2f")],
        )
        text_labels = base.mark_text(align="left", dx=4).encode(text=alt.Text("olasılık:Q", format=".2f"))
        rule = alt.Chart(pd.DataFrame({"x": [0.5]})).mark_rule(strokeDash=[4, 4], color="#999").encode(x="x:Q")
        st.altair_chart(bars + text_labels + rule, width="stretch")

        st.subheader("Atomik sorular")
        atom_df = pd.DataFrame({"soru": [ATOMIC_TR[k] for k in spec["atomic"]], "olasılık": A[0]})
        st.altair_chart(
            alt.Chart(atom_df).mark_bar(color="#8d6cab").encode(
                x=alt.X("olasılık:Q", scale=alt.Scale(domain=[0, 1]), title="P(evet)"),
                y=alt.Y("soru:N", sort=None, title=None, axis=alt.Axis(labelLimit=400)),
                tooltip=[alt.Tooltip("olasılık:Q", format=".2f")],
            ),
            width="stretch",
        )
        if arms["D-noisyor"] - arms["D-fit"] > 0.25:
            st.info(
                "Basit birleştirme ayarlı kolun çok üstünde. Atomik cevaplar birbiriyle "
                "ilişkili olduğu için noisy-OR aynı kanıtı birden çok sayıp aşırı özgüvenli oluyor."
            )
