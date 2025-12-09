import streamlit as st
import os
import tempfile
import io
from datetime import datetime
import zipfile
from PIL import Image
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter
import time

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA COISA!)
# ============================================================================
st.set_page_config(
    page_title="Conversor de Arquivos - Francisco Matos",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# POPUP MODAL PERSONALIZADO
# ============================================================================
def mostrar_popup_simples():
    """Versão mais simples e confiável"""
    
    if 'popup_visto' not in st.session_state:
        st.session_state.popup_visto = True
        
        # CSS para o modal e overlay
        st.markdown("""
        <style>
            .popup-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                z-index: 9998;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .popup-content {
                background: white;
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                border: 2px solid #e0e0e0;
                text-align: center;
                position: relative;
                z-index: 9999;
                max-width: 500px;
                width: 90%;
                margin: 2rem;
                animation: popupFadeIn 0.4s ease;
            }
            
            @keyframes popupFadeIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # HTML do popup
        st.markdown("""
        <div class="popup-overlay" id="popupOverlay">
            <div class="popup-content">
                <h2 style='color: #1a237e; margin-bottom: 1rem;'>
                    Olá, Francisco Matos
                </h2>
                
                <p style='color: #444; line-height: 1.6; margin-bottom: 1.5rem;'>
                    Desenvolvi esta ferramenta pensando em facilitar seu trabalho.<br>
                    Espero que seja muito útil para você!
                </p>
                
                <p style='color: #666; font-style: italic; margin-top: 1.5rem;'>
                    — Com Amor, Adrielly
                </p>
                
                <div style='margin-top: 1.5rem;'>
                    <button onclick="document.getElementById('popupOverlay').style.display='none'" 
                    style='
                        background: #1a237e;
                        color: white;
                        border: none;
                        padding: 10px 30px;
                        border-radius: 25px;
                        cursor: pointer;
                        font-weight: 500;
                        font-size: 1rem;
                    '>
                        Começar a usar
                    </button>
                </div>
            </div>
        </div>
        
        <script>
            // Fecha o popup ao clicar fora
            document.getElementById('popupOverlay').addEventListener('click', function(e) {
                if (e.target === this) {
                    this.style.display = 'none';
                }
            });
            
            // Fecha com ESC
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    document.getElementById('popupOverlay').style.display = 'none';
                }
            });
        </script>
        """, unsafe_allow_html=True)

# ============================================================================
# MOSTRAR POPUP (chamada imediatamente após a configuração)
# ============================================================================
mostrar_popup_simples()

# ============================================================================
# CSS PERSONALIZADO - ESTILO ELEGANTE
# ============================================================================
st.markdown("""
<style>
    /* Fonte principal */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Cabeçalho personalizado */
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 2.5rem;
        border-radius: 0 0 20px 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(26, 35, 126, 0.15);
    }
    
    .welcome-text {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    /* Cards de funcionalidades */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .feature-title {
        color: #1a237e;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        border-left: 4px solid #3949ab;
        padding-left: 12px;
    }
    
    .feature-description {
        color: #555;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 1.2rem;
    }
    
    /* Botões elegantes */
    .stButton > button {
        background: linear-gradient(135deg, #3949ab 0%, #1a237e 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 8px;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(57, 73, 171, 0.3);
        background: linear-gradient(135deg, #303f9f 0%, #151b5c 100%);
    }
    
    /* Sidebar estilizada */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-right: 1px solid #eaeaea;
    }
    
    .sidebar-title {
        color: #1a237e;
        font-weight: 600;
        font-size: 1.3rem;
        margin-bottom: 1.5rem;
        padding-bottom: 10px;
        border-bottom: 2px solid #e0e0e0;
    }
    
    /* Área de upload */
    .upload-area {
        border: 2px dashed #3949ab;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        background: #f0f2ff;
        border-color: #1a237e;
    }
    
    /* Cards de arquivo */
    .file-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #3949ab;
    }
    
    .file-name {
        font-weight: 500;
        color: #333;
    }
    
    .file-size {
        font-size: 0.85rem;
        color: #666;
    }
    
    /* Rodapé personalizado */
    .footer {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 20px 20px 0 0;
        margin-top: 3rem;
        text-align: center;
    }
    
    .footer-text {
        font-size: 1rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    .heart {
        color: #ff4081;
        display: inline-block;
        animation: heartbeat 1.5s infinite;
    }
    
    @keyframes heartbeat {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    /* Estilos para métricas */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a237e;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CABEÇALHO PERSONALIZADO
# ============================================================================
st.markdown("""
<div class="main-header">
    <div class="welcome-text">Bem-vindo, Francisco Matos</div>
    <div class="subtitle">Ferramentas úteis para converter e comprimir seus arquivos</div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FUNÇÕES PRINCIPAIS
# ============================================================================
def criar_pdf_de_imagens(imagens, nome_pdf):
    """Cria PDF a partir de imagens"""
    pdf = FPDF()
    
    for img_bytes in imagens:
        # Salva imagem temporariamente
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name
        
        try:
            # Adiciona página ao PDF
            pdf.add_page()
            
            # Carrega imagem para obter dimensões
            img = Image.open(io.BytesIO(img_bytes))
            width, height = img.size
            
            # Calcula dimensões para A4
            a4_width_mm = 190
            a4_height_mm = 267
            ratio = min(a4_width_mm / width, a4_height_mm / height)
            new_width = width * ratio
            new_height = height * ratio
            
            # Centraliza na página
            x = (210 - new_width) / 2
            y = (297 - new_height) / 2
            
            # Adiciona imagem ao PDF
            pdf.image(tmp_path, x=x, y=y, w=new_width)
            
        finally:
            # Limpa arquivo temporário
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    return pdf.output(dest='S').encode('latin-1')

def comprimir_pdf(pdf_bytes):
    """Comprime um arquivo PDF"""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

# ============================================================================
# SIDEBAR - MENU PRINCIPAL
# ============================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">Menu Principal</div>', unsafe_allow_html=True)
    
    opcao = st.radio(
        "Selecione a ferramenta:",
        ["Converter Imagens para PDF", "Comprimir Arquivo PDF", "Compactar Arquivos em ZIP"],
        key="menu_principal"
    )
    
    st.markdown("---")
    
    # Informações de uso
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        **Converter para PDF:**
        1. Selecione as imagens
        2. Configure o nome do arquivo
        3. Clique em "Criar PDF"
        
        **Comprimir PDF:**
        1. Faça upload do PDF
        2. O sistema comprimirá automaticamente
        3. Baixe a versão reduzida
        
        **Criar ZIP:**
        1. Selecione múltiplos arquivos
        2. Clique em "Criar ZIP"
        3. Baixe o arquivo compactado
        """)
    
    st.markdown("---")
    
    # Informações do sistema
    st.markdown("**Informações:**")
    st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    st.caption("Status: Sistema operacional")

# ============================================================================
# CONTEÚDO PRINCIPAL
# ============================================================================
if opcao == "Converter Imagens para PDF":
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="feature-title">Converter Imagens para PDF</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-description">Transforme suas imagens em um documento PDF organizado e de alta qualidade.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Selecione as imagens",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp'],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_files:
            st.success(f"{len(uploaded_files)} imagem(s) selecionada(s)")
            
            # Mostra preview das imagens
            st.markdown("**Prévia das imagens:**")
            cols = st.columns(min(4, len(uploaded_files)))
            for idx, uploaded_file in enumerate(uploaded_files):
                with cols[idx % 4]:
                    try:
                        img = Image.open(uploaded_file)
                        img.thumbnail((120, 120))
                        st.image(img, caption=uploaded_file.name[:15] + ("..." if len(uploaded_file.name) > 15 else ""), use_container_width=True)
                    except:
                        st.markdown(f'<div class="file-card"><div class="file-name">{uploaded_file.name}</div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-title">Configurações</div>', unsafe_allow_html=True)
        
        nome_pdf = st.text_input(
            "Nome do arquivo PDF:",
            value=f"Documento_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        )
        
        orientacao = st.selectbox(
            "Orientação da página:",
            ["Retrato", "Paisagem"]
        )
        
        qualidade = st.slider(
            "Qualidade do PDF:",
            min_value=1,
            max_value=10,
            value=8
        )
        
        if uploaded_files and st.button("Criar PDF", key="btn_criar_pdf"):
            with st.spinner("Processando imagens..."):
                try:
                    # Prepara as imagens
                    imagens_bytes = [file.getvalue() for file in uploaded_files]
                    
                    # Cria o PDF
                    pdf_bytes = criar_pdf_de_imagens(imagens_bytes, nome_pdf)
                    tamanho_pdf = len(pdf_bytes) / (1024 * 1024)
                    
                    # Mostra métricas
                    col_metric1, col_metric2 = st.columns(2)
                    with col_metric1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Páginas</div>
                            <div class="metric-value">{len(uploaded_files)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_metric2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Tamanho</div>
                            <div class="metric-value">{tamanho_pdf:.2f} MB</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Botão de download
                    st.download_button(
                        label=f"Baixar PDF ({tamanho_pdf:.2f} MB)",
                        data=pdf_bytes,
                        file_name=nome_pdf,
                        mime="application/pdf"
                    )
                    
                except Exception as e:
                    st.error(f"Erro ao criar PDF: {str(e)}")

elif opcao == "Comprimir Arquivo PDF":
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="feature-title">Comprimir Arquivo PDF</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-description">Reduza o tamanho de seus arquivos PDF mantendo a qualidade visual.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader(
            "Selecione o arquivo PDF",
            type=['pdf'],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_pdf:
            tamanho_original = len(uploaded_pdf.getvalue()) / (1024 * 1024)
            
            st.markdown(f"""
            <div class="file-card">
                <div class="file-name">{uploaded_pdf.name}</div>
                <div class="file-size">Tamanho original: {tamanho_original:.2f} MB</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-title">Configurações</div>', unsafe_allow_html=True)
        
        nivel_compression = st.select_slider(
            "Nível de compressão:",
            options=["Leve", "Moderado", "Máximo"],
            value="Moderado"
        )
        
        manter_qualidade = st.checkbox("Manter qualidade visual", value=True)
        
        if uploaded_pdf and st.button("Comprimir PDF", key="btn_comprimir_pdf"):
            with st.spinner("Comprimindo arquivo..."):
                try:
                    # Comprime o PDF
                    pdf_compactado = comprimir_pdf(uploaded_pdf.getvalue())
                    tamanho_novo = len(pdf_compactado) / (1024 * 1024)
                    reducao = ((tamanho_original - tamanho_novo) / tamanho_original) * 100
                    
                    # Mostra resultados
                    st.markdown("**Resultado da compressão:**")
                    
                    col_res1, col_res2, col_res3 = st.columns(3)
                    
                    with col_res1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Original</div>
                            <div class="metric-value">{tamanho_original:.2f} MB</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_res2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Comprimido</div>
                            <div class="metric-value">{tamanho_novo:.2f} MB</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_res3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Redução</div>
                            <div class="metric-value">{reducao:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Botão de download
                    nome_comprimido = f"comprimido_{uploaded_pdf.name}"
                    st.download_button(
                        label=f"Baixar PDF Comprimido ({tamanho_novo:.2f} MB)",
                        data=pdf_compactado,
                        file_name=nome_comprimido,
                        mime="application/pdf"
                    )
                    
                except Exception as e:
                    st.error(f"Erro ao comprimir PDF: {str(e)}")

else:  # Compactar Arquivos em ZIP
    
    st.markdown('<div class="feature-title">Compactar Arquivos em ZIP</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">Agrupe múltiplos arquivos em um único arquivo ZIP para facilitar o compartilhamento.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Selecione os arquivos",
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_files:
            total_size = sum(len(f.getvalue()) for f in uploaded_files) / 1024
            
            st.markdown(f"""
            <div class="file-card">
                <div class="file-name">{len(uploaded_files)} arquivo(s) selecionado(s)</div>
                <div class="file-size">Tamanho total: {total_size:.1f} KB</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Lista arquivos
            for uploaded_file in uploaded_files:
                file_size = len(uploaded_file.getvalue()) / 1024
                st.markdown(f"""
                <div class="file-card" style="margin: 5px 0; padding: 8px 12px; border-left: 3px solid #4CAF50;">
                    <div class="file-name">{uploaded_file.name}</div>
                    <div class="file-size">{file_size:.1f} KB</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-title">Configurações</div>', unsafe_allow_html=True)
        
        nome_zip = st.text_input(
            "Nome do arquivo ZIP:",
            value=f"Arquivos_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
        )
        
        nivel_compressao = st.selectbox(
            "Nível de compressão:",
            ["Normal", "Máximo"]
        )
        
        if uploaded_files and st.button("Criar Arquivo ZIP", key="btn_criar_zip"):
            with st.spinner("Criando arquivo ZIP..."):
                try:
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w', 
                        zipfile.ZIP_DEFLATED if nivel_compressao == "Máximo" else zipfile.ZIP_STORED) as zipf:
                        for uploaded_file in uploaded_files:
                            zipf.writestr(uploaded_file.name, uploaded_file.getvalue())
                    
                    zip_buffer.seek(0)
                    zip_bytes = zip_buffer.getvalue()
                    tamanho_zip = len(zip_bytes) / 1024
                    
                    # Métricas
                    col_zip1, col_zip2 = st.columns(2)
                    
                    with col_zip1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Arquivos</div>
                            <div class="metric-value">{len(uploaded_files)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_zip2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Tamanho ZIP</div>
                            <div class="metric-value">{tamanho_zip:.1f} KB</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Botão de download
                    st.download_button(
                        label="Baixar Arquivo ZIP",
                        data=zip_bytes,
                        file_name=nome_zip,
                        mime="application/zip"
                    )
                    
                except Exception as e:
                    st.error(f"Erro ao criar ZIP: {str(e)}")

# ============================================================================
# RODAPÉ PERSONALIZADO
# ============================================================================
st.markdown("""
<div class="footer">
    <div class="footer-text">
        Criado com dedicação por Adrielly 
        <span class="heart">❤</span>
        <br>
        Para facilitar seu trabalho, Francisco Matos
        <br>
        <small style="opacity: 0.7;">Última atualização: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """</small>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ============================================================================
if __name__ == "__main__":
    # Limpeza de arquivos temporários antigos
    try:
        for filename in os.listdir(tempfile.gettempdir()):
            if filename.startswith("tmp_streamlit_"):
                filepath = os.path.join(tempfile.gettempdir(), filename)
                file_age = datetime.now().timestamp() - os.path.getmtime(filepath)
                if file_age > 3600:  # Mais de 1 hora
                    os.unlink(filepath)
    except:
        pass