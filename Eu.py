import streamlit as st
from collections import Counter, defaultdict
import statistics

st.set_page_config(page_title="Football Studio AI Engine", layout="wide")

# ======================
# ESTADO
# ======================
if "history" not in st.session_state:
    st.session_state.history = []

if "pattern_perf" not in st.session_state:
    st.session_state.pattern_perf = defaultdict(lambda: {"win":0, "loss":0})

# ======================
# INPUT
# ======================
def add_result(r):
    st.session_state.history.append(r)
    if len(st.session_state.history) > 300:
        st.session_state.history.pop(0)

# ======================
# UTILIDADES
# ======================
def streak(hist):
    c = 1
    for i in range(len(hist)-1, 0, -1):
        if hist[i] == hist[i-1]:
            c += 1
        else:
            break
    return c

def zigzag(hist):
    c = 0
    for i in range(len(hist)-1, 1, -1):
        if hist[i] != hist[i-1]:
            c += 1
        else:
            break
    return c

def draw_gap(hist):
    for i in range(len(hist)-1, -1, -1):
        if hist[i] == "D":
            return len(hist)-1-i
    return len(hist)

def confidence(pattern):
    p = st.session_state.pattern_perf[pattern]
    total = p["win"] + p["loss"]
    if total < 5:
        return 50
    return round((p["win"] / total) * 100)

# ======================
# IA – MOTOR DE PADRÕES
# ======================
def analyze(hist):
    patterns = []
    if len(hist) < 20:
        return [{"pattern":"Observação","score":0,"action":"Não apostar"}]

    last20 = hist[-20:]
    last100 = hist[-100:] if len(hist)>=100 else hist

    c20 = Counter(last20)
    c100 = Counter(last100)

    # TREND
    for cor in ["R","B"]:
        pct = c20[cor]/len(last20)*100
        if pct >= 60:
            patterns.append({
                "pattern": f"Trend {cor}",
                "score": pct,
                "action": f"Seguir {'🔴' if cor=='R' else '🔵'}"
            })

    # STREAK
    s = streak(hist)
    if s >= 3:
        patterns.append({
            "pattern": "Streak",
            "score": min(30+s*8,70),
            "action": "Anti-streak" if s>=4 else "Continuar"
        })

    # ZIGZAG
    zz = zigzag(hist)
    if zz >= 3:
        patterns.append({
            "pattern": "ZigZag",
            "score": min(40+zz*6,70),
            "action": "Manter alternância"
        })

    # CLUSTER
    blocks=[]
    c=1
    for i in range(1,len(last20)):
        if last20[i]==last20[i-1]:
            c+=1
        else:
            blocks.append(c)
            c=1
    blocks.append(c)
    if len(blocks)>=4 and 3<=statistics.mean(blocks)<=4.5:
        patterns.append({
            "pattern":"Cluster",
            "score":60,
            "action":"Seguir blocos"
        })

    # DRAW
    gap = draw_gap(hist)
    if gap>=45:
        patterns.append({
            "pattern":"Draw Sniper",
            "score":min(50+gap,85),
            "action":"⚪ Draw (alto risco)"
        })

    # MEAN REVERSION
    diff = abs(c100["R"]-c100["B"])
    if len(last100)>=80 and diff>=20:
        weaker = "🔴" if c100["R"]<c100["B"] else "🔵"
        patterns.append({
            "pattern":"Reversão",
            "score":min(50+diff,80),
            "action":f"Apostar {weaker}"
        })

    if not patterns:
        patterns.append({
            "pattern":"Choppy",
            "score":10,
            "action":"NÃO APOSTAR"
        })

    # IA – AJUSTE PELO DESEMPENHO
    for p in patterns:
        conf = confidence(p["pattern"])
        p["score"] = round((p["score"] + conf) / 2)

    return sorted(patterns, key=lambda x: x["score"], reverse=True)

# ======================
# INTERFACE
# ======================
st.title("🤖 Football Studio – AI Decision Engine")

c1,c2 = st.columns([1,2])

with c1:
    st.subheader("Inserir Resultado")
    if st.button("🔴 Home"):
        add_result("R")
    if st.button("🔵 Away"):
        add_result("B")
    if st.button("⚪ Draw"):
        add_result("D")

    st.write(f"Rodadas: {len(st.session_state.history)}")

with c2:
    st.subheader("Histórico")
    st.write(" ".join(
        ["🔴" if x=="R" else "🔵" if x=="B" else "⚪" for x in st.session_state.history[-60:]]
    ))

    patterns = analyze(st.session_state.history)

    st.markdown("## 🧠 Decisão da IA")
    top = patterns[0]

    if top["score"] >= 55:
        st.success(f"""
Padrão: **{top['pattern']}**  
Score IA: **{top['score']}%**  
Ação: **{top['action']}**
""")
    else:
        st.error("EDGE INSUFICIENTE → NÃO APOSTAR")
