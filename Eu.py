import streamlit as st
from collections import Counter
import statistics

st.set_page_config("Football Studio AI PRO", layout="wide")

# ===============================
# ESTADO GLOBAL
# ===============================
if "history" not in st.session_state:
    st.session_state.history = []

if "bankroll" not in st.session_state:
    st.session_state.bankroll = 1000.0

if "profit" not in st.session_state:
    st.session_state.profit = 0.0

# ===============================
# INPUT
# ===============================
def add_result(r):
    st.session_state.history.append(r)
    if len(st.session_state.history) > 500:
        st.session_state.history.pop(0)

# ===============================
# FUNÇÕES DE PADRÃO
# ===============================
def streak(hist):
    c = 1
    for i in range(len(hist)-1,0,-1):
        if hist[i]==hist[i-1]: c+=1
        else: break
    return c

def zigzag(hist):
    z=0
    for i in range(len(hist)-1,1,-1):
        if hist[i]!=hist[i-1]: z+=1
        else: break
    return z

def draw_gap(hist):
    for i in range(len(hist)-1,-1,-1):
        if hist[i]=="D":
            return len(hist)-1-i
    return len(hist)

def cluster(hist):
    blocks=[]
    c=1
    for i in range(1,len(hist)):
        if hist[i]==hist[i-1]: c+=1
        else:
            blocks.append(c)
            c=1
    blocks.append(c)
    return statistics.mean(blocks[-6:]) if len(blocks)>=6 else 0

# ===============================
# IA CENTRAL
# ===============================
def analyze(hist):
    if len(hist)<30:
        return {"action":"NÃO APOSTAR","score":0}

    last20=hist[-20:]
    last100=hist[-100:] if len(hist)>=100 else hist

    c20=Counter(last20)
    c100=Counter(last100)

    signals=[]

    # 1 TREND
    for cor in ["R","B"]:
        p=c20[cor]/20*100
        if p>=60:
            signals.append((cor,p,"TREND"))

    # 2 ANTI STREAK
    s=streak(hist)
    if s>=4:
        signals.append(("B" if hist[-1]=="R" else "R",65+s*3,"ANTI-STREAK"))

    # 3 ZIGZAG
    zz=zigzag(hist)
    if zz>=3:
        signals.append((hist[-2],55+zz*4,"ZIG-ZAG"))

    # 4 CLUSTER
    cl=cluster(last20)
    if 3<=cl<=4.5:
        signals.append((hist[-1],60,"CLUSTER"))

    # 5 DRAW GAP
    dg=draw_gap(hist)
    if dg>=50:
        signals.append(("D",70+dg//2,"DRAW GAP"))

    # 6 MEAN REVERSION
    diff=abs(c100["R"]-c100["B"])
    if diff>=20:
        weaker="R" if c100["R"]<c100["B"] else "B"
        signals.append((weaker,60+diff,"REVERSION"))

    # 7 COLAPSO
    if len(signals)>=3:
        best=max(signals,key=lambda x:x[1])
        return {
            "action":"NÃO APOSTAR",
            "score":best[1],
            "reason":"COLAPSO / ARMADILHA"
        }

    if not signals:
        return {"action":"NÃO APOSTAR","score":0,"reason":"MESA CHOPPY"}

    best=max(signals,key=lambda x:x[1])

    return {
        "action":"APOSTAR",
        "color":best[0],
        "score":round(best[1]),
        "reason":best[2]
    }

# ===============================
# GESTÃO DE BANCA
# ===============================
def stake(score):
    if score>=80: return st.session_state.bankroll*0.05
    if score>=70: return st.session_state.bankroll*0.03
    if score>=60: return st.session_state.bankroll*0.02
    return 0

# ===============================
# INTERFACE
# ===============================
st.title("🤖 Football Studio – AI ENGINE PRO")

c1,c2=st.columns([1,2])

with c1:
    st.subheader("🎮 Entrada")
    if st.button("🔴 Home"): add_result("R")
    if st.button("🔵 Away"): add_result("B")
    if st.button("⚪ Draw"): add_result("D")

    st.metric("Banca",f"R$ {st.session_state.bankroll:.2f}")
    st.metric("Lucro",f"R$ {st.session_state.profit:.2f}")

with c2:
    st.subheader("📊 Histórico (Recente → Antigo)")
    st.write(" ".join(
        ["🔴" if x=="R" else "🔵" if x=="B" else "⚪"
         for x in reversed(st.session_state.history[-60:])]
    ))

    r=analyze(st.session_state.history)

    st.markdown("## 🎯 DECISÃO DA IA")

    if r["action"]=="NÃO APOSTAR":
        st.error(f"NÃO APOSTAR | {r.get('reason','')}")
    else:
        s=stake(r["score"])
        cor="🔴" if r["color"]=="R" else "🔵" if r["color"]=="B" else "⚪"
        st.success(
            f"APOSTAR {cor} | "
            f"Score: {r['score']} | "
            f"Stake: R$ {s:.2f} | "
            f"Padrão: {r['reason']}"
        )
