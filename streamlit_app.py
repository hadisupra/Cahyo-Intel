"""
Streamlit App for LLM Agent
Connects to FastAPI backend (local or GCP Cloud Run)
"""

import os
import json
from datetime import datetime
# Inline token/cost utility (moved from Chat_token.py)
try:
    import tiktoken
except Exception:
    tiktoken = None

DEFAULT_USD_TO_IDR = float(os.getenv("USD_TO_IDR", "16000"))
INPUT_PRICE_PER_1K_USD = float(os.getenv("INPUT_PRICE_PER_1K_USD", "0.0005"))
OUTPUT_PRICE_PER_1K_USD = float(os.getenv("OUTPUT_PRICE_PER_1K_USD", "0.0015"))

def _count_tokens(text: str, model_hint: str = "gpt-4o-mini") -> int:
    if not text:
        return 0
    if tiktoken is None:
        # Fallback: rough estimate ~4 chars per token
        return max(1, len(text) // 4)
    try:
        enc = tiktoken.encoding_for_model(model_hint)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def run_chat_token(prompt: str, output_text: str = "", model: str = None, latency: float = 0.0):
    model_hint = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
    input_tokens = _count_tokens(prompt or "", model_hint)
    output_tokens = _count_tokens(output_text or "", model_hint)

    input_cost_usd = (input_tokens / 1000.0) * INPUT_PRICE_PER_1K_USD
    output_cost_usd = (output_tokens / 1000.0) * OUTPUT_PRICE_PER_1K_USD
    total_cost_usd = input_cost_usd + output_cost_usd
    total_cost_idr = total_cost_usd * DEFAULT_USD_TO_IDR

    return {
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "input_cost_usd": round(input_cost_usd, 6),
        "output_cost_usd": round(output_cost_usd, 6),
        "total_cost_usd": round(total_cost_usd, 6),
        "input_cost_idr": round(input_cost_usd * DEFAULT_USD_TO_IDR, 2),
        "output_cost_idr": round(output_cost_usd * DEFAULT_USD_TO_IDR, 2),
        "cost_idr": round(total_cost_idr, 2),
        "latency": round(latency or 0.0, 2),
    }


import requests
import streamlit as st

# Configuration - Set your API base URL (no trailing slash)
DEFAULT_API_URL = "https://llm-agent-api-793786022526.asia-southeast2.run.app"
API_URL = os.getenv("API_URL", DEFAULT_API_URL).rstrip("/")

# Page config
st.set_page_config(
    page_title="Olist LLM Agent Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
if "agent_mode" not in st.session_state:
    st.session_state.agent_mode = "auto"  # Default to auto mode
if "pending_message" not in st.session_state:             # <--- TAMBAHKAN INI
    st.session_state.pending_message = None   
if "page" not in st.session_state:
    st.session_state.page = None
if "quick_start_used" not in st.session_state:
    st.session_state.quick_start_used = False

    
# Sidebar

st.sidebar.image("sidebar_banner.png", use_container_width=True)

with st.sidebar:
    st.title("⚙️ Settings")

    api_url_input = st.text_input(
        "API URL",
        value=API_URL,
        help="Your FastAPI backend URL (e.g., http://localhost:8080 or Cloud Run URL)",
    )
    if api_url_input:
        API_URL = api_url_input.rstrip("/")

    # Agent mode selector
    st.session_state.agent_mode = st.selectbox(
        "Agent Mode",
        options=["auto", "sql", "qdrant"],
        index=0,
        help="Auto: Let AI choose | SQL: Structured data | Qdrant: Product reviews"
    )

    st.divider()

    if st.button("🔌 Test Connection", use_container_width=True):
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Connected to API!")
                data = response.json()
                st.json(data)
            else:
                st.error(f"❌ API returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection failed: {str(e)}")

    st.divider()

    st.subheader("📊 Session Info")
    st.text(f"Session ID: {st.session_state.session_id}")
    st.text(f"Messages: {len(st.session_state.messages)}")
    st.text(f"Current Mode: {st.session_state.agent_mode.upper()}")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.quick_start_used = False
        st.session_state.pending_message = None
        st.rerun()

    st.divider()
    st.sidebar.markdown("### About Us")

    if st.sidebar.button("Product", use_container_width=True):
        st.session_state.page = "Product"
    
    if st.sidebar.button("How to Use", use_container_width=True):
        st.session_state.page = "How to Use"

    if st.sidebar.button("Profile", use_container_width=True):
        st.session_state.page = "Profile"

    if st.sidebar.button("Career", use_container_width=True):
        st.session_state.page = "Career"
    
# ======================
# MAIN PAGE
# ======================
if st.session_state.page is None:

    st.image("main_banner.png", use_container_width=True)

    st.markdown(
        "### 💬 Chat with your data using AI\n"
        "Ask questions about products, orders, reviews."
    )

    # Chat history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Quick Start (only before chat starts)
    if not st.session_state.quick_start_used:
        st.subheader("🚀 Quick Start")
        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("📊 Product Statistics", use_container_width=True):
                st.session_state.pending_message = "Berapa total produk yang dijual?"
                st.session_state.quick_start_used = True
                st.rerun()

        with c2:
            if st.button("⭐ Review Analysis", use_container_width=True):
                st.session_state.pending_message = "Ringkasan review produk parfum"
                st.session_state.quick_start_used = True
                st.rerun()

        with c3:
            if st.button("💰 Price Analysis", use_container_width=True):
                st.session_state.pending_message = "What is the average price of products by category?"
                st.session_state.quick_start_used = True
                st.rerun()
                

# ======================
# GLOBAL CHAT INPUT (SATU KALI)
# ======================
chat_input = None

if st.session_state.page is None:
    chat_input = st.chat_input("💭 Ask me anything about products, orders, or reviews...")

# ======================
# Resolve prompt (Quick Start > Chat Input)
# ======================
prompt = None

if st.session_state.pending_message:
    prompt = st.session_state.pending_message
    st.session_state.pending_message = None
elif chat_input:
    prompt = chat_input

# ======================
# SINGLE API CALL (FINAL)
# ======================
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        payload = {
            "message": prompt,
            "agent": st.session_state.agent_mode,
            "session_id": st.session_state.session_id,
        }

        # 1. Placeholder untuk thinking + spinner
        thinking_placeholder = st.empty()

        with thinking_placeholder:
            st.markdown("🤔 **Thinking…**")
            with st.spinner(""):
                resp = requests.post(
                    f"{API_URL}/chat",
                    json=payload,
                    timeout=60,
                )

        # 2. Hapus thinking UI
        thinking_placeholder.empty()

        # 3. Baru render chat bubble FINAL
        if resp.status_code == 200:
            data = resp.json()
            answer = data.get("agent_response", "")
            # Compute tokens and cost for both input and output; include HTTP latency
            token_result = run_chat_token(prompt, answer, latency=(getattr(resp, "elapsed", None).total_seconds() if getattr(resp, "elapsed", None) else 0.0))
            agents_used = data.get("agents_used", [])
            agent_choice = data.get("agent_choice", None)

            with st.chat_message("assistant"):
                st.markdown(answer)
                st.caption(f"""
                📥 Input: {token_result['input_tokens']} | 📤 Output: {token_result['output_tokens']}
                💰 Cost: Input Rp{token_result['input_cost_idr']} | Output Rp{token_result['output_cost_idr']} | Total Rp{token_result['cost_idr']}
                ⏱️ Latency: {token_result['latency']}s
                """.strip())

                if agents_used:
                    st.caption(f"🤖 Agents: {', '.join(agents_used)}")

                if agent_choice and st.session_state.agent_mode == "auto":
                    st.caption(f"🎯 Auto-routed to: **{agent_choice.upper()}**")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "metadata": {
                    "agents": agents_used,
                    "agent_choice": agent_choice,
                    "mode": st.session_state.agent_mode,
                },
            })
        else:
            st.error("❌ API Error")

    except Exception as e:
        st.error(str(e))

if "page" not in st.session_state:
    st.session_state.page = None

page = st.session_state.page
# ======================
# 4. PRODUCT
# ======================
if page == "Product":
    st.title("What is SmartStack?")

    st.markdown("""
SmartStack Commerce Intelligence AI is an LLM-powered analytics assistant developed in partnership between **Cahyo Intelligence x Olist**. Designed to interact through natural language, it enables users to analyze e-commerce data without dashboards or SQL queries.

Rather than functioning as a consumer-facing shopping bot, SmartStack operates as a **decision intelligence layer** — helping teams interrogate data, surface trends, and validate hypotheses in real time.

SmartStack combines:
- **RAG (Retrieval-Augmented Generation)** for understanding and summarizing customer review data  
- **SQL Agent** for querying structured data (pricing, logistics, payments, seller performance)  
- **Orchestrator Agent** to detect intent and route each request to the correct analytical workflow  

Our mission is to remove technical complexity and allow both technical and non-technical users to extract value from Olist’s dataset through simple, conversational inputs.
    """)

    st.title("What problem does SmartStack solve?")

    st.markdown("""
Today’s e-commerce data environments produce large volumes of fragmented information across multiple systems. While rich in potential value, data is often underutilized due to:

- Siloed tables and inconsistent data accessibility  
- High volumes of unstructured review text  
- The need for specialized technical skills (SQL, BI tools)

**SmartStack addresses a core question:**

> How can e-commerce transaction and review data be transformed into business intelligence, accessible through natural language?

By enabling rapid exploration and insight-generation, SmartStack reduces dependency on analysts for basic queries and shortens the path between question → answer → action.
    """)

    st.title("Who is SmartStack for?")

    st.markdown("""
SmartStack is designed for teams who need actionable intelligence without technical overhead. Key users include:

**Primary users**
- E-commerce and business analysts looking for rapid category, seller, pricing, and review insights  
- Product and operations managers diagnosing performance bottlenecks (e.g., slow delivery regions, problematic sellers)  
- Merchants seeking category benchmarking or internal performance simulations  

**Secondary users**
- Data science and AI learners using the platform for experimentation or education  
- Internal stakeholders conducting AI-driven analytics demonstrations  

SmartStack is **not** intended for end consumers seeking product recommendations, nor for brand-level or SKU-level comparison as a replacement for commercial intelligence suites.
    """)

    if st.button("← Back to Home", key="back_home", help="Back to Home"):
        st.session_state.page = None
        st.rerun()

    st.stop()

# ======================
# 4. PRODUCT
# ======================
if page == "How to Use":
    st.title("How to Use")

    st.markdown("""SmartStack is currently in its Beta phase.
During this period, features and analytical outputs are still being actively developed and refined. As a result, users may encounter functional limitations, incomplete results, or system behavior that is not yet fully consistent. We greatly value user feedback, as it is essential to the continuous improvement of the platform.

To support a more effective user experience and ensure more accurate query results, we recommend reviewing the usage guidelines and best practices provided below.

For Indonesian and English-speaking users, we have prepared a dedicated guide containing tailored tips and usage recommendations to help improve search precision and overall experience.""")

    st.title("Panduan Penggunaan (Bahasa Indonesia)")

    st.markdown("""
1. **Gunakan kata kunci yang tepat**: Pemilihan kata kunci membantu sistem menentukan metode analisis yang sesuai. Gunakan istilah seperti jumlah, rata-rata, atau statistik untuk analisis data, dan kata seperti review, ulasan, atau pengalaman untuk analisis opini pelanggan.

2. **Perhatikan bahasa data**: Sebagian data tersedia dalam bahasa Portugis. Jika diperlukan, tambahkan instruksi seperti “terjemahkan nama kategori ke bahasa Indonesia” agar hasil lebih mudah dipahami.

3. **Sampaikan masukan dan keluhan**: Masukan, kendala, atau saran pengembangan dapat dikirimkan ke customer@cahyoai.com
.  """)

    st.title("Usage Guide (English)")

    st.markdown("""
1. **Use clear and relevant keywords**: Choosing the right keywords helps the system select the most appropriate analysis method. Use terms such as total, average, or statistics for data-based queries, and words like review, feedback, or experience for opinion and customer sentiment analysis.

2. **Be mindful of the data language**: Some data is available in Portuguese. When needed, add instructions such as “please translate category name to English” to make the results easier to understand.

3. **Share feedback and report issues**: Feedback, issues, or feature suggestions can be sent to customer@cahyoai.com
.""")

    if st.button("← Back to Home", key="back_home", help="Back to Home"):
        st.session_state.page = None
        st.rerun()

    st.stop()

# ======================
# 5. Profile
# ======================
elif page == "Profile":
    st.title("Who Are We?")

    st.markdown("""
**Cahyo Intelligence** takes its name from the Indonesian word *cahaya*, meaning *light* — a reflection of our philosophy: bringing clarity to the complexity of data and artificial intelligence.

We are a team focused on building applied AI and data solutions, with expertise spanning data analytics, product management, artificial intelligence, and engineering. Our work centers on turning real-world business problems into practical, scalable systems.

Guided by principles of precision, transparency, and measurable impact, our mission is to transform complex datasets into insights that are accessible, relevant, and actionable for better decision-making.
    """)

    st.image(
        "team.png",
        use_container_width=True
    )

    if st.button("← Back to Home", key="back_home", help="Back to Home"):
        st.session_state.page = None
        st.rerun()

    st.stop()

# ======================
# 6. KARIR
# ======================

elif page == "Career":
    st.title("Join Our Team")

    st.markdown("""
We are always open to meeting talented individuals passionate about shaping the future of AI and data.

We welcome interest from professionals with experience in:
- Data Analytics  
- AI / Machine Learning Engineering  
- Product Management  
- Software Engineering  

If you’d like to explore opportunities with us, please reach out to our internal team at career@cahyoai.com or share your details for future openings.
    """)

    if st.button("← Back to Home", key="back_home", help="Back to Home"):
        st.session_state.page = None
        st.rerun()

    st.stop()


# Footer
st.divider()
st.image("footer.png", use_container_width=True)
st.markdown(
    """
<div style='text-align: center; color: gray;'>
    <small>Powered by FastAPI + SQLite + Qdrant + OpenAI | Deployed on GCP Cloud Run</small>
</div>
""",
    unsafe_allow_html=True,
)

