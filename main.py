import streamlit as st
import numpy as np
import plotly.graph_objects as go
from numpy import pi
from pathlib import Path

# --------- CONFIG (ONLY ONCE) ----------
st.set_page_config(
    page_title="Digital Modulation Visualizer | BMSCE",
    layout="wide",
    page_icon="📡"
)

# Path to logo next to this script
LOGO_PATH = Path(__file__).parent / "bmsce_logo.jpg"

# --------- STAGE MANAGEMENT ----------
# stage = 0 -> welcome
# stage = 1 -> constraints
# stage = 2 -> main visualizer
if "stage" not in st.session_state:
    st.session_state.stage = 0


# --------- PAGE 0: WELCOME ----------
def page_welcome():
    st.markdown(
        """
        <style>
            .welcome-title {
                font-size: 48px;
                font-weight: 800;
                color: #00c0ff;
                text-align: center;
                text-shadow: 0px 0px 15px rgba(0, 192, 255, 0.7);
                margin-top: 10px;
            }
            .welcome-sub {
                font-size: 24px;
                color: #f1f3f6;
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Centered logo
    st.write("")  # spacing
    logo_cols = st.columns([1, 2, 1])
    with logo_cols[1]:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=230)
        else:
            st.error("Logo file not found. Make sure 'bmsce_logo.jpg' is next to this script.")

    st.markdown("<h1 class='welcome-title'>BMS College of Engineering</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='welcome-sub'>Department of Electronics and Communication Engineering</h3>",
                unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Centered start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start = st.button(
            "🚀 Start Digital Modulation Visualizer",
            use_container_width=True
        )
    if start:
        st.session_state.stage = 1
        st.rerun()   # ✅ updated


# --------- PAGE 1: CONSTRAINTS & CREDITS ----------
def page_constraints():
    st.markdown("## ⚙️ Simulation Constraints & Settings")
    st.markdown(
        """
        Below are the parameter ranges and assumptions used in this digital modulation visualizer.
        These values are chosen to keep the waveforms **easy to view** and **computationally light**.
        """
    )

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Signal Parameters")
        st.markdown(
            """
            - **Bit Stream**: Binary sequence (e.g. `10110011`)  
            - **Bit Rate**: `1` to `20` bits/sec  
            - **Amplitude (A)**: `1.0` to `10.0` units  
            - **Carrier Frequency (fc)**: `1` Hz to `50` Hz  
            - **Samples per Bit (fs)**: `50` to `1000` samples/bit  
            - **SNR**: `-5 dB` (very noisy) to `40` dB (almost clean)  
            """
        )

        st.markdown("### Modulation-Specific")
        st.markdown(
            """
            - **ASK**:  
              - Bit `1` → carrier of amplitude `A`  
              - Bit `0` → amplitude `0` (no carrier)  
            
            - **BPSK**:  
              - Bit `0` → phase `0°`  
              - Bit `1` → phase `180°`  
            
            - **QPSK**:  
              - 2 bits are grouped per symbol  
              - 4 phases used for mapping (00, 01, 11, 10)  
            """
        )

    with col_right:
        st.markdown("### FSK & DPSK")
        st.markdown(
            """
            - **FSK**:
              - Two frequencies:  
                - `f₁ = fc − Δf/2` for bit `0`  
                - `f₂ = fc + Δf/2` for bit `1`  
              - Frequency separation Δf: `2` Hz to `20` Hz (set using slider)
            
            - **DPSK**:
              - Phase is changed **relative** to previous symbol  
              - Bit `1` → phase toggles by `π`  
              - Bit `0` → phase stays unchanged  
            """
        )

        st.markdown("### Notes")
        st.markdown(
            """
            - Time axis is scaled using **bit duration** `T_b = 1 / bit_rate`.  
            - Total simulation time = `len(bits) × T_b`.  
            - Noise is **additive white Gaussian noise (AWGN)**.  
            - Visualization is intended for **educational use**,
              not for strict standard-compliant physical layer design.
            """
        )

    st.markdown("---")
    st.markdown("### 👨‍💻 Developed By")
    st.markdown(
        """
        - **Harsha**  
        - **Neel**  
        - **Skanda**  
        - **Jayden**  
        """
    )

    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        proceed = st.button("➡️ Proceed to Visualizer", use_container_width=True)
    if proceed:
        st.session_state.stage = 2
        st.rerun()   # ✅ updated


# --------- PAGE 2: MAIN VISUALIZER ----------
def page_visualizer():
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #0b0f19;
                color: #f1f3f6;
            }
            h1, h2, h3 {
                color: #00c0ff !important;
                text-shadow: 0px 0px 8px rgba(0,192,255,0.4);
            }
            .stSidebar {
                background: linear-gradient(180deg, #1a1f2b, #10131a);
                color: white;
                border-right: 2px solid #00c0ff30;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📡 Digital Modulation Visualizer — Interactive Learning Tool")
    st.markdown(
        """
        This tool demonstrates **ASK, BPSK, QPSK, FSK, and DPSK**.  
        Adjust parameters in the sidebar to see how digital bits map into analog waveforms.
        """
    )

    # ---- SIDEBAR ----
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

    # ---- DATA PREP ----
    bits = [b for b in bit_input if b in ("0", "1")]
    if len(bits) == 0:
        st.error("❌ Please enter a valid binary bit stream (e.g. 101010).")
        return

    Tb = 1 / bit_rate
    T = Tb * len(bits)
    t = np.linspace(0, T, int(fs * len(bits)))
    signal = np.zeros_like(t)

    # ---- MODULATION ----
    if mod_type == "ASK":
        for i, b in enumerate(bits):
            idx = (t >= i * Tb) & (t < (i + 1) * Tb)
            carrier = np.sin(2 * pi * fc * t[idx])
            signal[idx] = A * carrier if b == "1" else 0

    elif mod_type == "BPSK":
        for i, b in enumerate(bits):
            idx = (t >= i * Tb) & (t < (i + 1) * Tb)
            phase = 0 if b == "0" else pi
            signal[idx] = A * np.sin(2 * pi * fc * t[idx] + phase)

    elif mod_type == "QPSK":
        if len(bits) % 2 != 0:
            bits.append("0")
        mapping = {"00": pi / 4, "01": 3 * pi / 4, "11": 5 * pi / 4, "10": 7 * pi / 4}
        for i in range(0, len(bits), 2):
            idx = (t >= (i / 2) * Tb) & (t < ((i / 2) + 1) * Tb)
            phase = mapping["".join(bits[i:i + 2])]
            signal[idx] = A * np.sin(2 * pi * fc * t[idx] + phase)

    elif mod_type == "FSK":
        f1, f2 = fc - f_delta / 2, fc + f_delta / 2
        for i, b in enumerate(bits):
            idx = (t >= i * Tb) & (t < (i + 1) * Tb)
            signal[idx] = A * np.sin(2 * pi * (f1 if b == "0" else f2) * t[idx])

    elif mod_type == "DPSK":
        prev_phase = 0
        for i, b in enumerate(bits):
            idx = (t >= i * Tb) & (t < (i + 1) * Tb)
            if b == "1":
                prev_phase = (prev_phase + pi) % (2 * pi)
            signal[idx] = A * np.sin(2 * pi * fc * t[idx] + prev_phase)

    # ---- NOISE ----
    sig_power = np.mean(signal ** 2)
    noise_power = sig_power / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_power) * np.random.randn(len(signal))
    rx = signal + noise

    # ---- TABS ----
    tab1, tab2 = st.tabs(["📈 Waveform", "📘 Theory"])

    with tab1:
        st.subheader(f"🧩 {mod_type} Waveform Visualization")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=signal, mode="lines", name="Transmitted"))
        fig.add_trace(go.Scatter(x=t, y=rx, mode="lines", name="Received (Noisy)"))
        fig.update_layout(template="plotly_dark", xaxis_title="Time (s)", yaxis_title="Amplitude")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader(f"📘 Understanding {mod_type}")
        st.write("You can fill detailed theory content here if needed.")

    st.markdown("---")
    st.caption("Digital Modulation Visualizer | BMSCE ECE — Harsha, Neel, Skanda, Jayden")


# --------- ROUTER ----------
if st.session_state.stage == 0:
    page_welcome()
elif st.session_state.stage == 1:
    page_constraints()
else:
    page_visualizer()
