import streamlit as st

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="Football Studio PRO IA", layout="wide")

# ===============================
# SESSION STATE
# ===============================
if "history" not in st.session_state:
    st.session_state.history = []

if "cycle_memory" not in st.session_state:
    st.session_state.cycle_memory = []

# ===============================
# UTILS
# ===============================
def extract_blocks(hist):
    if not hist:
        return []
    blocks=[]
    c=1
    for i in range(1,len(hist)):
        if hist[i]==hist[i-1]:
            c+=1
        else:
            blocks.append((hist[i-1],c))
            c=1
    blocks.append((hist[-1],c))
    return blocks

# ===============================
# CICLOS
# ===============================
def detect_cycle(blocks):
    if not blocks:
        return None

    size = blocks[-1][1]

    if size >= 4:
        return "STREAK"

    if len(blocks) >= 4:
        sizes = [b[1] for b in blocks[-4:]]
        if sizes == [1,1,1,1]:
            return "ALTERNÂNCIA"

    if len(blocks) >= 4:
        if [b[1] for b in blocks[-4:]] == [4,4,3,2]:
            return "DECAIMENTO"

    if len(blocks) >= 6:
        if [b[1] for b in blocks[-6:]] == [4,4,3,2,3,2]:
            return "ESTRUTURAL"

    return "CHOPPY"

def update_cycle_memory(blocks):
    cycle = detect_cycle(blocks)
    if not cycle:
        return

    if not st.session_state.cycle_memory or st.session_state.cycle_memory[-1] != cycle:
        st.session_state.cycle_memory.append(cycle)

    if len(st.session_state.cycle_memory) > 3:
        st.session_state.cycle_memory.pop(0)

# ===============================
# PADRÕES
# ===============================
def detect_patterns(hist):
    signals=[]
    blocks=extract_blocks(hist)
    if len(hist) < 6:
        return signals

    sizes=[b[1] for b in blocks]

    # STREAK
    if blocks[-1][1] >= 3:
        signals.append((blocks[-1][0], 54, "STREAK"))

    # DUPLO CURTO
    if len(sizes)>=2 and sizes[-1]==2 and sizes[-2]==2:
        signals.append((blocks[-1][0], 55, "DUPLO CURTO"))

    # 1x1x1
    if sizes[-3:] == [1,1,1]:
        signals.append((blocks[-1][0], 56, "1x1x1"))

    # DECAIMENTO
    if len(sizes)>=4 and sizes[-4:] == [4,4,3,2]:
        signals.append((blocks[-1][0], 56, "DECAIMENTO"))

    # PADRÃO AVANÇADO
    if len(sizes)>=8 and sizes[-8:] == [4,4,3,2,3,2,1,2]:
        signals.append((blocks[-2][0], 59, "ESTRUTURAL AVANÇADO"))

    return signals

# ===============================
# IA FINAL COM MEMÓRIA
# ===============================
def ia_decision(hist):
    blocks = extract_blocks(hist)
    update_cycle_memory(blocks)

    signals = detect_patterns(hist)

    if not signals:
        return "AGUARDAR", 0, "SEM PADRÃO"

    best = max(signals, key=lambda x: x[1])
    score = best[1]

    # 🔴 MEMÓRIA DE 3 CICLOS
    memory = st.session_state.cycle_memory

    if memory.count("CHOPPY") >= 2:
        score -= 10

    if len(memory) == 3 and memory[0] == memory[2]:
        score += 5  # repetição estrutural

    if score >= 55:
        return f"APOSTAR {'🔴' if best[0]=='R' else '🔵'}", score, f"{best[2]} | CICLOS {memory}"
    else:
        return "AGUARDAR", score, f"{best[2]} | CICLOS {memory}"

# ===============================
# UI
# ===============================
st.title("🎮 Football Studio PRO IA – Memória de Ciclos")

col1,col2,col3 = st.columns(3)

with col1:
    if st.button("🔴 Vermelho"):
        st.session_state.history.insert(0,"R")
    if st.button("🔵 Azul"):
        st.session_state.history.insert(0,"B")
    if st.button("⚪ Empate"):
        st.session_state.history.insert(0,"D")

with col2:
    st.subheader("🧠 Memória de 3 Ciclos")
    st.write(st.session_state.cycle_memory)

with col3:
    st.subheader("📊 Histórico (Recente → Antigo)")
    st.write(" ".join("🔴" if h=="R" else "🔵" if h=="B" else "⚪" for h in st.session_state.history[:30]))

# ===============================
# DECISÃO
# ===============================
decision, score, info = ia_decision(st.session_state.history)

st.divider()
st.subheader("🎯 DECISÃO DA IA")

if "APOSTAR" in decision:
    st.success(f"{decision} | Score {score} | {info}")
else:
    st.warning(f"{decision} | Score {score} | {info}")
