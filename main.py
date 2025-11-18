import streamlit as st
import numpy as np
import plotly.graph_objects as go
from numpy import pi

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Digital Modulation Visualizer", layout="wide", page_icon="📡")

st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #f1f3f6;
    }
    h1, h2, h3 {
        color: #00c0ff !important;
        text-shadow: 0px 0px 8px rgba(0,192,255,0.4);
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stSidebar {
        background: linear-gradient(180deg, #1a1f2b, #10131a);
        color: white;
        border-right: 2px solid #00c0ff30;
    }
    .sidebar-content {
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.title("📡 Digital Modulation Visualizer — Interactive Learning Tool")
st.markdown("""
This visualizer helps you **understand ASK, BPSK, QPSK, FSK, and DPSK** modulation schemes.  
Adjust parameters in the sidebar and explore how digital bits become analog waveforms 🎛️  
""")

# -------------------- SIDEBAR --------------------
st.sidebar.header("⚙️ Simulation Controls")
mod_type = st.sidebar.selectbox("Modulation Type", ["ASK", "BPSK", "QPSK", "FSK", "DPSK"])
bit_input = st.sidebar.text_input("Bit Stream", "10110011")
bit_rate = st.sidebar.slider("Bit Rate (bits/sec)", 1, 20, 5)
A = st.sidebar.slider("Amplitude", 1.0, 10.0, 3.0)
fc = st.sidebar.slider("Carrier Frequency (Hz)", 1.0, 50.0, 10.0)
fs = st.sidebar.slider("Samples per bit", 50, 1000, 300)
snr_db = st.sidebar.slider("SNR (dB)", -5, 40, 25)

if mod_type == "FSK":
    f_delta = st.sidebar.slider("Frequency Separation (Hz)", 2.0, 20.0, 6.0)
else:
    f_delta = None

# -------------------- DATA PREP --------------------
bits = [b for b in bit_input if b in ('0', '1')]
if len(bits) == 0:
    st.error("❌ Please enter a valid binary bit stream (e.g. 101010).")
    st.stop()

Tb = 1 / bit_rate
T = Tb * len(bits)
t = np.linspace(0, T, int(fs * len(bits)))
signal = np.zeros_like(t)

# -------------------- MODULATION LOGIC --------------------
if mod_type == "ASK":
    for i, b in enumerate(bits):
        idx = (t >= i*Tb) & (t < (i+1)*Tb)
        carrier = np.sin(2*pi*fc*t[idx])
        signal[idx] = (A * carrier) if b == '1' else 0

elif mod_type == "BPSK":
    for i, b in enumerate(bits):
        idx = (t >= i*Tb) & (t < (i+1)*Tb)
        phase = 0 if b == '0' else pi
        signal[idx] = A * np.sin(2*pi*fc*t[idx] + phase)

elif mod_type == "QPSK":
    if len(bits) % 2 != 0:
        bits.append('0')
    bit_pairs = [bits[i:i+2] for i in range(0, len(bits), 2)]
    mapping = {'00': pi/4, '01': 3*pi/4, '11': 5*pi/4, '10': 7*pi/4}
    for i, pair in enumerate(bit_pairs):
        idx = (t >= i*Tb) & (t < (i+1)*Tb)
        phase = mapping[''.join(pair)]
        signal[idx] = A * np.sin(2*pi*fc*t[idx] + phase)

elif mod_type == "FSK":
    f1, f2 = fc - f_delta/2, fc + f_delta/2
    for i, b in enumerate(bits):
        idx = (t >= i*Tb) & (t < (i+1)*Tb)
        f = f1 if b == '0' else f2
        signal[idx] = A * np.sin(2*pi*f*t[idx])

elif mod_type == "DPSK":
    prev_phase = 0
    for i, b in enumerate(bits):
        idx = (t >= i*Tb) & (t < (i+1)*Tb)
        if b == '1':
            prev_phase = (prev_phase + pi) % (2*pi)
        signal[idx] = A * np.sin(2*pi*fc*t[idx] + prev_phase)

# -------------------- ADD NOISE --------------------
sig_power = np.mean(signal**2)
noise_power = sig_power / (10**(snr_db/10))
noise = np.sqrt(noise_power) * np.random.randn(len(signal))
rx = signal + noise

# -------------------- TABS FOR UI --------------------
tab1, tab2, tab3 = st.tabs(["📈 Waveform", "🌌 Constellation", "📘 Theory"])

# -------- TAB 1: Waveform Visualization --------
with tab1:
    st.subheader(f"🧩 {mod_type} Waveform Visualization")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=signal, mode="lines", name="Transmitted Signal", line=dict(color="#00C0FF", width=2)))
    fig.add_trace(go.Scatter(x=t, y=rx, mode="lines", name="Received (Noisy)", line=dict(color="#FF4081", width=1)))
    fig.update_layout(
        template="plotly_dark",
        title=f"{mod_type} Modulated Signal",
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        height=450,
        legend=dict(bgcolor="#111", bordercolor="#333")
    )
    st.plotly_chart(fig, use_container_width=True)

# -------- TAB 2: Constellation Diagram --------
with tab2:
    st.subheader("🌌 Constellation Representation")
    if mod_type == "ASK":
        I, Q = [0, A], [0, 0]
    elif mod_type == "BPSK":
        I, Q = [A, -A], [0, 0]
    elif mod_type == "QPSK":
        I = [np.cos(pi/4), np.cos(3*pi/4), np.cos(5*pi/4), np.cos(7*pi/4)]
        Q = [np.sin(pi/4), np.sin(3*pi/4), np.sin(5*pi/4), np.sin(7*pi/4)]
    elif mod_type == "FSK":
        I, Q = [f1, f2], [0, 0]
    elif mod_type == "DPSK":
        I, Q = [np.cos(0), np.cos(pi)], [np.sin(0), np.sin(pi)]

    const_fig = go.Figure(data=go.Scatter(x=I, y=Q, mode='markers+text',
                                          text=[f"Symbol {i+1}" for i in range(len(I))],
                                          textposition="top center",
                                          marker=dict(size=14, color="#00FFAA", line=dict(width=1, color="black"))))
    const_fig.update_layout(template="plotly_dark",
                            xaxis_title="In-phase (I)",
                            yaxis_title="Quadrature (Q)",
                            height=450,
                            title=f"{mod_type} Constellation Diagram")
    st.plotly_chart(const_fig, use_container_width=True)

# -------- TAB 3: Theory Section --------
with tab3:
    st.subheader(f"📘 Understanding {mod_type}")
    theory_text = {
        "ASK": "In Amplitude Shift Keying (ASK), binary data is represented by switching the carrier amplitude between two levels.",
        "BPSK": "In Binary Phase Shift Keying (BPSK), bits '0' and '1' are represented by phase shifts of 0° and 180° respectively.",
        "QPSK": "In Quadrature PSK, two bits are grouped per symbol, resulting in four phase shifts (45°, 135°, 225°, 315°).",
        "FSK": "In Frequency Shift Keying (FSK), bits are represented by varying the carrier frequency (f₁ and f₂).",
        "DPSK": "In Differential PSK, data is encoded as phase changes relative to the previous symbol."
    }
    st.write(theory_text[mod_type])
    st.info("💡 Tip: Try changing SNR to see how noise affects constellation clarity!")

st.markdown("---")
st.caption("🚀 Built by Skanda | Streamlit + Plotly | Designed for learning digital modulation visually")
