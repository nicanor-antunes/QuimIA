import base64
import os
from pathlib import Path

import streamlit as st
from groq import Groq


APP_DIR = Path(__file__).parent
LOGO_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".svg")
LOGO_CANDIDATES = (
    "logo-horizontal.png",
    "logo.png",
    "logo.jpg",
    "logo.jpeg",
    "logo.webp",
    "logo.svg",
    "quimia.png",
    "quimia.jpg",
    "quimia.jpeg",
    "quimia.webp",
    "quimia.svg",
)


st.set_page_config(
    page_title="QuimIA",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def get_client():
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(api_key=api_key)

if "resposta" not in st.session_state:
    st.session_state.resposta = ""

if "ultima_pergunta" not in st.session_state:
    st.session_state.ultima_pergunta = ""


def find_logo_path() -> Path | None:
    for filename in LOGO_CANDIDATES:
        logo_path = APP_DIR / filename
        if logo_path.exists():
            return logo_path

    logo_matches = sorted(
        path
        for path in APP_DIR.iterdir()
        if path.is_file()
        and "logo" in path.stem.lower()
        and path.suffix.lower() in LOGO_EXTENSIONS
    )
    return logo_matches[0] if logo_matches else None


@st.cache_data(show_spinner=False)
def image_data_uri(path: str) -> str:
    suffix = Path(path).suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }
    mime_type = mime_types.get(suffix, "image/png")
    encoded = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def logo_src() -> str | None:
    logo_path = find_logo_path()
    return image_data_uri(str(logo_path)) if logo_path else None


st.markdown(
    """
    <style>
    :root {
        --bg: #f6f8fb;
        --surface: #ffffff;
        --surface-soft: #eef7f2;
        --text: #102033;
        --muted: #5b6b7d;
        --line: #dfe7ef;
        --brand: #159a57;
        --brand-dark: #0f7a46;
        --accent: #2563eb;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    section[data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--line);
        width: 18rem !important;
        min-width: 18rem !important;
    }

    section[data-testid="stSidebar"] > div {
        width: 18rem !important;
    }

    section[data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
    }

    .block-container {
        max-width: 1180px;
        padding: 1rem 1.8rem 3rem;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        margin-bottom: 1.2rem;
    }

    .brand-mark {
        display: grid;
        place-items: center;
        width: 56px;
        height: 56px;
        border-radius: 18px;
        background: linear-gradient(135deg, #dcfce7, #dbeafe);
        border: 1px solid #c7ead2;
        font-size: 1.8rem;
    }

    .logo-wrap {
        display: flex;
        justify-content: center;
        margin: 0 0 1rem;
    }

    .sidebar-logo {
        width: 168px;
        height: 68px;
        object-fit: contain;
        object-position: center;
        display: block;
    }

    .student-header {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.98), rgba(237,250,242,0.92)),
            radial-gradient(circle at 92% 20%, rgba(37, 99, 235, 0.15), transparent 28%);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);
        padding: 1.1rem 1.25rem;
        margin-bottom: 1rem;
    }

    .student-header-grid {
        display: grid;
        grid-template-columns: 190px minmax(0, 1fr);
        gap: 1.1rem;
        align-items: center;
    }

    .student-logo {
        width: 190px;
        height: 76px;
        object-fit: contain;
        object-position: center;
        display: block;
    }

    .student-header h1 {
        margin: 0.25rem 0 0.4rem;
        color: var(--text);
        font-size: 2rem;
        line-height: 1.12;
        letter-spacing: 0;
    }

    .student-header p {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.5;
        margin: 0;
        max-width: 760px;
    }

    .tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.8rem;
    }

    .tag-row span {
        border: 1px solid #ccefd8;
        border-radius: 999px;
        background: #f0fbf4;
        color: var(--brand-dark);
        font-size: 0.82rem;
        font-weight: 750;
        padding: 0.34rem 0.6rem;
    }

    .panel-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin: 0 0 0.6rem;
    }

    .panel-title h2 {
        margin: 0;
        color: var(--text);
        font-size: 1.22rem;
        letter-spacing: 0;
    }

    .panel-title span {
        color: var(--muted);
        font-size: 0.9rem;
    }

    .student-tip {
        background: #f8fbff;
        border: 1px solid var(--line);
        border-left: 4px solid var(--accent);
        border-radius: 8px;
        padding: 0.85rem 0.95rem;
        color: var(--muted);
        line-height: 1.5;
        font-size: 0.94rem;
        margin: 0.75rem 0 0;
    }

    .study-list {
        display: grid;
        gap: 0.55rem;
        margin: 0.4rem 0 0.9rem;
    }

    .study-list div {
        background: #fbfdff;
        border: 1px solid var(--line);
        border-radius: 8px;
        color: var(--muted);
        padding: 0.72rem 0.8rem;
        line-height: 1.45;
    }

    .study-list strong {
        color: var(--text);
    }

    .hero-brand {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1.1rem;
    }

    .hero-brand-logo {
        width: 260px;
        height: 92px;
        object-fit: contain;
        object-position: center;
        display: block;
        flex: 0 0 auto;
    }

    .hero-pill {
        color: var(--brand-dark);
        background: #e8f8ee;
        border: 1px solid #ccefd8;
        border-radius: 999px;
        padding: 0.45rem 0.75rem;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .brand-title {
        margin: 0;
        font-size: 1.9rem;
        line-height: 1;
        font-weight: 800;
        letter-spacing: 0;
    }

    .brand-subtitle {
        margin-top: 0.3rem;
        color: var(--muted);
        font-size: 0.98rem;
    }

    .hero {
        display: grid;
        grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.8fr);
        gap: 1.4rem;
        align-items: stretch;
        margin-bottom: 1.3rem;
    }

    .hero-main,
    .panel {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.06);
    }

    .hero-main {
        padding: 1.35rem 1.6rem 1.55rem;
        position: relative;
        overflow: hidden;
    }

    .hero-main::after {
        content: "";
        position: absolute;
        inset: auto -80px -95px auto;
        width: 260px;
        height: 260px;
        background: radial-gradient(circle, rgba(21,154,87,0.16), transparent 68%);
        pointer-events: none;
    }

    .eyebrow {
        color: var(--brand-dark);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .hero h1 {
        margin: 0;
        color: var(--text);
        font-size: 2.35rem;
        line-height: 1.08;
        letter-spacing: 0;
    }

    .hero p {
        color: var(--muted);
        font-size: 1.05rem;
        line-height: 1.65;
        max-width: 700px;
        margin: 1rem 0 0;
    }

    .hero-side {
        padding: 1rem;
        display: grid;
        gap: 0.8rem;
    }

    .stat {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.82rem;
        background: #fbfdff;
    }

    .stat strong {
        display: block;
        color: var(--text);
        font-size: 1rem;
        margin-bottom: 0.2rem;
    }

    .stat span {
        color: var(--muted);
        font-size: 0.9rem;
    }

    .section-title {
        margin: 1.5rem 0 0.75rem;
        font-size: 1.18rem;
        font-weight: 800;
        color: var(--text);
    }

    .quick-card {
        min-height: 154px;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    }

    .quick-icon {
        font-size: 1.6rem;
        margin-bottom: 0.55rem;
    }

    .quick-card h3 {
        margin: 0 0 0.35rem;
        font-size: 1.05rem;
        color: var(--text);
    }

    .quick-card p {
        margin: 0;
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.45;
    }

    .answer-box {
        background: var(--surface);
        border: 1px solid var(--line);
        border-left: 6px solid var(--brand);
        border-radius: 8px;
        padding: 1.2rem 1.35rem;
        margin-top: 1rem;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
        color: var(--text);
        line-height: 1.75;
        font-size: 1rem;
    }

    .answer-label {
        color: var(--brand-dark);
        font-weight: 800;
        margin-bottom: 0.55rem;
    }

    div[data-testid="stButton"] > button {
        min-height: 2.65rem;
        border-radius: 8px;
        border: 1px solid var(--line);
        font-weight: 700;
        transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: var(--brand);
        color: var(--brand-dark);
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(21, 154, 87, 0.13);
    }

    div[data-testid="stLinkButton"] > a {
        min-height: 2.65rem;
        border-radius: 8px;
        border: 1px solid var(--line);
        font-weight: 700;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius: 8px;
        border-color: var(--line);
    }

    .footer {
    text-align: center;
    margin-top: 50px;
    margin-bottom: 20px;
    color: #666;
    font-size: 14px;
}

.footer p {
    margin: 6px 0;
}

    @media (max-width: 820px) {
        .block-container {
            padding: 1.25rem 1rem 2.2rem;
        }

        .hero {
            grid-template-columns: 1fr;
        }

        .hero h1 {
            font-size: 2rem;
        }

        .hero-brand {
            align-items: flex-start;
            flex-direction: column;
        }

        .hero-brand-logo {
            width: 230px;
        }

        .student-header-grid {
            grid-template-columns: 1fr;
        }

        .student-logo {
            width: 175px;
        }

        .student-header h1 {
            font-size: 1.65rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_brand() -> None:
    src = logo_src()
    if src:
        st.markdown(
            f"""
            <div class="logo-wrap">
                <img class="sidebar-logo" src="{src}" alt="QuimIA">
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Assistente de química para estudo guiado")
        return

    st.markdown(
        """
        <div class="brand-lockup">
            <div class="brand-mark">⚗️</div>
            <div>
                <h2 class="brand-title">QuimIA</h2>
                <div class="brand-subtitle">Assistente de química para estudo guiado</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_answer(text: str) -> None:
    if not text:
        return

    st.markdown(
        '<div class="section-title">Resposta do QuimIA</div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown(text)


def generate_response(prompt: str, spinner_text: str) -> None:

    client = get_client()

    if client is None:
        st.error(
            "Configure a chave GROQ_API_KEY em st.secrets ou nas variáveis de ambiente."
        )
        return

    with st.spinner(spinner_text):

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=1500,
        )

        st.session_state.resposta = (
            completion.choices[0].message.content
        )


def quick_card(icon: str, title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="quick-card">
            <div class="quick-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_student_header() -> None:
    src = logo_src()
    logo_html = (
        f'<img class="student-logo" src="{src}" alt="QuimIA">'
        if src
        else '<div class="brand-mark">⚗️</div>'
    )

    st.markdown(
        f"""
        <section class="student-header">
            <div class="student-header-grid">
                <div>{logo_html}</div>
                <div>
                    <div class="eyebrow">Química para o Ensino Médio</div>
                    <h1>Resolva dúvidas, revise conteúdos e treine para provas.</h1>
                    <p>
                        O QuimIA explica passo a passo, cria exemplos do cotidiano e ajuda
                        você a praticar sem transformar química em decoreba.
                    </p>
                    <div class="tag-row">
                        <span>Explicação simples</span>
                        <span>Questões com gabarito</span>
                        <span>Revisão rápida</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    render_brand()

    pagina = st.radio(
        "Menu",
        [
            "Assistente",
            "Questões ENEM",
            "Recursos",
            "Sobre o Projeto",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Plataforma educacional com IA para estudar química com explicações simples.")

    if st.button("Nova conversa", use_container_width=True):
        st.session_state.resposta = ""
        st.session_state.ultima_pergunta = ""
        st.rerun()

    st.success("IA educacional ativa")


if pagina == "Assistente":
    render_student_header()

    left, right = st.columns([1.55, 0.95], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                """
                <div class="panel-title">
                    <h2>Pergunte ao QuimIA</h2>
                    <span>Resposta didática + passo a passo</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            pergunta = st.text_area(
                "Digite sua dúvida de química",
                value=st.session_state.ultima_pergunta,
                placeholder="Ex.: Por que o sal se dissolve na água? Como balancear H2 + O2 -> H2O?",
                height=132,
                label_visibility="collapsed",
            )

            col_ask, col_clear = st.columns([1, 0.25])
            with col_ask:
                enviar = st.button("Gerar resposta", type="primary", use_container_width=True)
            with col_clear:
                limpar = st.button("Limpar", use_container_width=True)

            st.markdown(
                """
                <div class="student-tip">
                    Dica: escreva o que você já tentou. Exemplo: “não entendi por que o oxigênio fica com 2 no balanceamento”.
                </div>
                """,
                unsafe_allow_html=True,
            )

        if limpar:
            st.session_state.resposta = ""
            st.session_state.ultima_pergunta = ""
            st.rerun()

        if enviar and pergunta.strip():
            st.session_state.ultima_pergunta = pergunta.strip()
            generate_response(
                f"""
                Você é o QuimIA, um tutor virtual especializado em Química para estudantes do Ensino Médio.

Objetivo:
Auxiliar estudantes a compreender conceitos de Química de forma clara,
didática e contextualizada.

Regras:
- Responda sempre em português.
- Utilize linguagem adequada ao Ensino Médio.
- Explique passo a passo.
- Use exemplos do cotidiano.
- Destaque fórmulas importantes.
- Relacione o conteúdo ao ENEM quando possível.
- Evite termos excessivamente técnicos sem explicação.
- Ao final, apresente um resumo em até 3 tópicos.

Formato:
1. Explicação
2. Exemplo prático
3. Resumo

                Responda para estudantes do ensino médio com:
                - linguagem simples;
                - explicação passo a passo;
                - analogias do cotidiano quando ajudarem;
                - fórmulas importantes bem destacadas;
                - um mini resumo final em até 3 tópicos.

                Pergunta:
                {pergunta.strip()}
                """,
                "QuimIA está analisando sua pergunta...",
            )
        elif enviar:
            st.warning("Digite uma pergunta antes de gerar a resposta.")

        render_answer(st.session_state.resposta)

        st.markdown('<div class="section-title">Perguntas prontas para começar</div>', unsafe_allow_html=True)
        exemplos = [
            "O que é ligação covalente?",
            "Explique o conceito de pH.",
            "Como balancear H2 + O2 -> H2O?",
            "O que é mol na química?",
        ]

        ex_cols = st.columns(2)
        for i, exemplo in enumerate(exemplos):
            with ex_cols[i % 2]:
                if st.button(exemplo, key=f"exemplo-{i}", use_container_width=True):
                    st.session_state.ultima_pergunta = exemplo
                    generate_response(
                        f"""
                        Explique de forma didática, simples e passo a passo:
                        {exemplo}
                        """,
                        "QuimIA está analisando...",
                    )

    with right:
        with st.container(border=True):
            st.markdown(
                """
                <div class="panel-title">
                    <h2>Modo estudo</h2>
                    <span>atalhos rápidos</span>
                </div>
                <div class="study-list">
                    <div><strong>Resumo:</strong> revise um tema em poucos minutos.</div>
                    <div><strong>Prática:</strong> treine com questão e gabarito.</div>
                    <div><strong>ENEM:</strong> veja contexto cotidiano e resolução.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Resumo de 5 minutos", key="aprenda", use_container_width=True):
                generate_response(
                    """
                    Gere um resumo curto e didático sobre um conteúdo importante de química do ensino médio.
                    Estruture em:
                    1. ideia principal;
                    2. exemplo do cotidiano;
                    3. fórmula ou regra importante;
                    4. três pontos para memorizar.
                    """,
                    "Gerando resumo...",
                )

            if st.button("Questão com gabarito", key="pratique", use_container_width=True):
                generate_response(
                    """
                    Gere uma questão de química para ensino médio com:
                    - enunciado contextualizado;
                    - 4 alternativas;
                    - resposta correta;
                    - explicação detalhada.
                    """,
                    "Gerando questão...",
                )

            if st.button("Treino estilo ENEM", key="enem-rapido", use_container_width=True):
                generate_response(
                    """
                    Crie uma questão de química no estilo ENEM.
                    Use contexto cotidiano, 5 alternativas, gabarito e resolução comentada.
                    """,
                    "Gerando questão ENEM...",
                )

        st.markdown('<div class="section-title">Explorar</div>', unsafe_allow_html=True)
        st.link_button(
            "Simulações PhET",
            "https://phet.colorado.edu/pt_BR/",
            use_container_width=True,
        )
        st.link_button(
            "Tabela periódica",
            "https://www.tabperiodic.com/pt-BR/",
            use_container_width=True,
        )


elif pagina == "Questões ENEM":
    st.markdown(
        """
        <section class="student-header">
            <div class="eyebrow">Treino contextualizado</div>
            <h1>Questões no estilo ENEM</h1>
            <p>
                Gere uma questão de química com situação-problema, cinco alternativas,
                gabarito e resolução comentada.
            </p>
            <div class="tag-row">
                <span>Contexto cotidiano</span>
                <span>5 alternativas</span>
                <span>Resolução comentada</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    enem_left, enem_right = st.columns([1.35, 0.85], gap="large")

    with enem_left:
        with st.container(border=True):
            st.markdown(
                """
                <div class="panel-title">
                    <h2>Escolha um tema</h2>
                    <span>opcional</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            tema = st.text_input(
                "Tema opcional",
                placeholder="Ex.: eletroquímica, soluções, termoquímica...",
                label_visibility="collapsed",
            )

            if st.button("Gerar questão ENEM", type="primary", use_container_width=True):
                recorte = f" sobre {tema.strip()}" if tema.strip() else ""
                generate_response(
                    f"""
                    Crie uma questão de química no estilo ENEM{recorte}.

                    Requisitos:
                    - contexto cotidiano;
                    - enunciado claro;
                    - 5 alternativas identificadas de A a E;
                    - indique a resposta correta;
                    - explique a resolução passo a passo.
                    """,
                    "Gerando questão...",
                )

    with enem_right:
        with st.container(border=True):
            st.markdown(
                """
                <div class="panel-title">
                    <h2>Como estudar</h2>
                </div>
                <div class="study-list">
                    <div><strong>1.</strong> Tente resolver antes de olhar o gabarito.</div>
                    <div><strong>2.</strong> Marque o trecho do enunciado que dá a pista.</div>
                    <div><strong>3.</strong> Refaça a conta ou conceito sem consultar.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    render_answer(st.session_state.resposta)

elif pagina == "Sobre o Projeto":

    st.markdown("""
    <section class="student-header">
        <div class="eyebrow">Inovação Educacional</div>
        <h1>Sobre o QuimIA</h1>
        <p>
            Plataforma desenvolvida para auxiliar estudantes do Ensino Médio
            no aprendizado de Química por meio de Inteligência Artificial.
        </p>
    </section>
    """, unsafe_allow_html=True)

    st.markdown("## Problema")

    st.write("""
    Muitos estudantes apresentam dificuldades na aprendizagem de Química
    devido à complexidade dos conceitos, linguagem técnica e necessidade
    de contextualização dos conteúdos.
    """)

    st.markdown("## Objetivo")

    st.write("""
    Desenvolver uma plataforma educacional baseada em Inteligência Artificial
    capaz de fornecer explicações didáticas, questões contextualizadas e
    apoio ao estudo de Química.
    """)

    st.markdown("## Tecnologias Utilizadas")

    st.markdown("""
    - Python
    - Streamlit
    - Inteligência Artificial (Groq + Llama)
    - HTML e CSS
    - Processamento de Linguagem Natural (PLN)
    """)

    st.markdown("## Público-Alvo")

    st.write("""
    Estudantes do Ensino Médio, candidatos ao ENEM e professores que
    desejam utilizar ferramentas digitais como apoio ao ensino de Química.
    """)

    st.markdown("## Equipe")

    st.write("""
    Felipe dos Santos Araújo

    Ana Caroline Araújo Duarte da Silva

    André Holanda Nascimento

    Nicanor Tiago Bueno Antunes
    """)

else:
    st.markdown(
        """
        <section class="student-header">
            <div class="eyebrow">Ferramentas externas</div>
            <h1>Recursos para estudar química</h1>
            <p>Links úteis para consultar, simular fenômenos e resolver exercícios com mais autonomia.</p>
            <div class="tag-row">
                <span>Consulta rápida</span>
                <span>Simulações</span>
                <span>Apoio para exercícios</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Consulta e prática</div>', unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)

    with r1:
        quick_card("⚛️", "Tabela periódica", "Consulte elementos, massas e propriedades.")
        st.link_button(
            "Abrir tabela",
            "https://www.tabperiodic.com/pt-BR/",
            use_container_width=True,
        )

    with r2:
        quick_card("🧮", "Calculadora", "Faça contas rápidas durante exercícios.")
        st.link_button(
            "Abrir calculadora",
            "https://www.calculadoraonline.com.br/basica",
            use_container_width=True,
        )

    with r3:
        quick_card("📖", "Materiais", "Acesse conteúdos de apoio e revisão.")
        st.link_button(
            "Abrir Só Química",
            "https://www.soquimica.com.br/",
            use_container_width=True,
        )


st.markdown(
    """
    <div class="footer">
        <strong>QuimIA © 2026</strong><br>
        Plataforma educacional com inteligência artificial.<br><br>

        Desenvolvido por:
        Felipe dos Santos Araújo • Ana Caroline Araújo Duarte da Silva •
        André Holanda Nascimento • Nicanor Tiago Bueno Antunes
    </div>
    """,
    unsafe_allow_html=True,
)
