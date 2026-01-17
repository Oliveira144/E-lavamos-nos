import streamlit as st
from collections import Counter

st.set_page_config(page_title="Football Studio Analyzer", layout="wide")

# ======================
# ESTADO GLOBAL
# ======================
if "history" not in st.session_state:
    st.session_state.history = []

# ======================
# FUNÇÕES
# ======================
def add_result(result):
    st.session_state.history.append(result)
    if len(st.session_state.history) > 200:
        st.session_state.history.pop(0)

def streak(history):
    if len(history) < 2:
        return 1
    count = 1
    for i in range(len(history)-1, 0, -1):
        if history[i] == history[i-1]:
            count += 1
        else:
            break
    return count

def zigzag_count(history):
    if len(history) < 3:
        return 0
    count = 0
    for i in range(len(history)-1, 1, -1):
        if history[i] != history[i-1]:
            count += 1
        else:
            break
    return count

def detect_pattern(history):
    if len(history) < 10:
        return "Observação"

    last20 = history[-20:]
    count = Counter(last20)

    red_pct = count["R"] / len(last20) * 100
    blue_pct = count["B"] / len(last20) * 100

    current_streak = streak(history)
    zigzag = zigzag_count(history)

    if red_pct >= 60:
        return "Trend Vermelho"
    if blue_pct >= 60:
        return "Trend Azul"
    if zigzag >= 3:
        return "ZigZag"
    if current_streak >= 4:
        return "Streak Forte"
    if current_streak >= 2:
        return "Streak Curto"

    return "Choppy / Sem padrão"

def suggestion(pattern, history):
    last = history[-1]
    if pattern == "Trend Vermelho":
        return "Seguir 🔴 (stake fixa)"
    if pattern == "Trend Azul":
        return "Seguir 🔵 (stake fixa)"
    if pattern == "ZigZag":
        return "Manter alternância"
    if pattern == "Streak Forte":
        return f"Anti-streak → Apostar {'🔵' if last == 'R' else '🔴'}"
    return "NÃO APOSTAR"

# ======================
# INTERFACE
# ======================
st.title("🎮 Football Studio – Analyzer Profissional")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎯 Inserir Resultado")
    if st.button("🔴 Home"):
        add_result("R")
    if st.button("🔵 Away"):
        add_result("B")
    if st.button("⚪ Draw"):
        add_result("D")

    st.markdown("---")
    st.subheader("📊 Estatísticas")
    total = len(st.session_state.history)
    if total > 0:
        c = Counter(st.session_state.history)
        st.write(f"🔴 Vermelho: {c['R']} ({c['R']/total:.1%})")
        st.write(f"🔵 Azul: {c['B']} ({c['B']/total:.1%})")
        st.write(f"⚪ Empate: {c['D']} ({c['D']/total:.1%})")

with col2:
    st.subheader("📈 Histórico")
    st.write(" ".join(
        ["🔴" if x=="R" else "🔵" if x=="B" else "⚪" for x in st.session_state.history[-50:]]
    ))

    if total >= 10:
        pattern = detect_pattern(st.session_state.history)
        advice = suggestion(pattern, st.session_state.history)

        st.markdown("### 🧠 Leitura da Mesa")
        st.success(f"Padrão Atual: **{pattern}**")
        st.warning(f"Sugestão Técnica: **{advice}**")

    else:
        st.info("Observe pelo menos 10 rodadas antes de qualquer decisão.")
