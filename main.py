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
mod_type = st.sidebar.selectbox(
    "Modulation Type",
    ["ASK", "BPSK", "QPSK", "FSK", "DPSK"],
    index=0
)
bit_input = st.sidebar.text_input("Bit Stream", "10110011")
bit_rate = st.sidebar.slider("Bit Rate (bits/sec)", 1, 20, 5)
A = st.sidebar.slider("Amplitude", 1.0, 10.0, 3.0)
fc = st.sidebar.slider("Carrier Frequency (Hz)", 1.0, 50.0, 10.0)
fs = st.sidebar.slider("Samples per bit", 50, 1000, 300)
snr_db = st.sidebar.slider("SNR (dB)", -5, 40, 25)

f_delta = None
if mod_type == "FSK":
    f_delta = st.sidebar.slider("Frequency Separation (Hz)", 2.0, 20.0, 6.0)

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

# -------------------- TABS --------------------
tab1, tab2 = st.tabs(["📈 Waveform", "📘 Theory & Insights"])

# -------- TAB 1: Waveform --------
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

# -------- TAB 2: Theory --------
with tab2:
    st.subheader(f"📘 Understanding {mod_type}")
    theory_full = {
        "ASK": {
            "description": "Amplitude Shift Keying (ASK) represents binary data by switching the carrier amplitude between two levels.",
            "advantages": ["Simple to implement", "Low bandwidth requirement"],
            "disadvantages": ["Sensitive to noise", "Less power-efficient"],
            "applications": ["Optical fiber communication", "AM radio transmission"]
        },
        "BPSK": {
            "description": "Binary Phase Shift Keying (BPSK) represents bits '0' and '1' by phase shifts of 0° and 180°.",
            "advantages": ["Robust to noise", "Simple coherent demodulation"],
            "disadvantages": ["Low data rate", "Requires coherent receiver"],
            "applications": ["Satellite communication", "RFID systems"]
        },
        "QPSK": {
            "description": "Quadrature PSK (QPSK) encodes two bits per symbol, creating four phase states (45°, 135°, 225°, 315°).",
            "advantages": ["Higher data rate than BPSK", "Bandwidth efficient"],
            "disadvantages": ["More complex receiver design", "Phase ambiguity issues"],
            "applications": ["Wi-Fi (802.11)", "3G/4G LTE"]
        },
        "FSK": {
            "description": "Frequency Shift Keying (FSK) transmits binary data by shifting the carrier between two frequencies.",
            "advantages": ["Resistant to amplitude noise", "Simple demodulation techniques"],
            "disadvantages": ["Requires larger bandwidth", "Slower data rates"],
            "applications": ["Modems", "Low-frequency radio communication"]
        },
        "DPSK": {
            "description": "Differential PSK (DPSK) encodes bits using phase differences between successive symbols.",
            "advantages": ["No coherent reference required", "Simpler demodulation than PSK"],
            "disadvantages": ["Slightly higher error rate than BPSK", "Phase error propagation"],
            "applications": ["Wireless LANs", "Optical communication systems"]
        }
    }

    if mod_type in theory_full:
        tinfo = theory_full[mod_type]
        st.markdown(f"**Description:** {tinfo['description']}")
        st.markdown(f"**Advantages:**\n- " + "\n- ".join(tinfo['advantages']))
        st.markdown(f"**Disadvantages:**\n- " + "\n- ".join(tinfo['disadvantages']))
        st.markdown(f"**Applications:**\n- " + "\n- ".join(tinfo['applications']))
        st.info("💡 Tip: Lowering SNR increases noise and makes signal detection harder, demonstrating real-world challenges.")
    else:
        st.warning("⚠ Please select a valid modulation scheme.")

st.markdown("---")
st.caption("Digital Modulation Visualizer | Streamlit + Plotly")
st.write("DONE BY:""Harsha,","Neel,","Skanda,","Jayden")