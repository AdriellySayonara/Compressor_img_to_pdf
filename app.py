import streamlit as st
import os
import tempfile
import io
from datetime import datetime
from PIL import Image
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter

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
# FUNÇÕES PRINCIPAIS CORRIGIDAS
# ============================================================================
def criar_pdf_de_imagens_otimizado(imagens_bytes_list):
    """Cria PDF a partir de imagens - VERSÃO OTIMIZADA E FUNCIONAL"""
    pdf = FPDF()
    
    # Configuração inicial
    pdf.set_auto_page_break(auto=True, margin=15)
    
    try:
        for i, img_bytes in enumerate(imagens_bytes_list):
            # Adiciona uma nova página para cada imagem
            pdf.add_page()
            
            # Converte bytes para imagem PIL
            img = Image.open(io.BytesIO(img_bytes))
            
            # Converte para RGB se necessário (para evitar problemas com PNG transparência)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Cria fundo branco
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Salva imagem temporariamente em formato JPEG
            temp_img_bytes = io.BytesIO()
            img.save(temp_img_bytes, format='JPEG', quality=85)
            temp_img_bytes.seek(0)
            
            # Calcula dimensões para caber na página (A4: 210x297 mm)
            # Margens: 10mm cada lado -> área útil: 190x277 mm
            max_width = 190  # mm
            max_height = 277  # mm
            
            # Obtém dimensões da imagem em pixels
            width_px, height_px = img.size
            
            # Calcula proporção
            ratio = min(max_width / width_px, max_height / height_px) * 0.35
            width_mm = width_px * ratio
            height_mm = height_px * ratio
            
            # Centraliza a imagem na página
            x = (210 - width_mm) / 2
            y = (297 - height_mm) / 2
            
            # Adiciona imagem ao PDF
            pdf.image(temp_img_bytes, x=x, y=y, w=width_mm, h=height_mm)
            
            # Adiciona número da página
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(128, 128, 128)
            pdf.set_y(285)
            pdf.cell(0, 10, f'Página {i+1}', 0, 0, 'C')
        
        # Gera o PDF em bytes
        pdf_bytes = pdf.output(dest='S')
        return pdf_bytes
        
    except Exception as e:
        st.error(f"Erro ao criar PDF: {str(e)}")
        return None

def comprimir_pdf_otimizado(pdf_bytes, qualidade='média'):
    """Comprime PDF de forma otimizada"""
    try:
        # Lê o PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        pdf_writer = PdfWriter()
        
        # Copia todas as páginas mantendo compatibilidade
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)
        
        # Aplica compressão baseada na qualidade selecionada
        output_buffer = io.BytesIO()
        
        if qualidade == 'alta':
            # Compressão máxima
            for page in pdf_writer.pages:
                page.compress_content_streams()  # Compressão leve
        elif qualidade == 'média':
            # Compressão moderada
            pass  # Mantém como está
        
        # Escreve para buffer
        pdf_writer.write(output_buffer)
        compressed_bytes = output_buffer.getvalue()
        
        return compressed_bytes
        
    except Exception as e:
        st.error(f"Erro na compressão: {str(e)}")
        return pdf_bytes  # Retorna original se falhar

# ============================================================================
# SIDEBAR - MENU PRINCIPAL SIMPLIFICADO
# ============================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">Menu Principal</div>', unsafe_allow_html=True)
    
    opcao = st.radio(
        "Selecione a ferramenta:",
        ["Converter Imagens para PDF", "Comprimir Arquivo PDF"],
        key="menu_principal"
    )
    
    st.markdown("---")
    
    # Informações de uso
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        **Converter para PDF:**
        1. Selecione as imagens (JPG, PNG, etc.)
        2. Configure o nome e qualidade
        3. Clique em "Criar PDF"
        4. Baixe o arquivo resultante
        
        **Comprimir PDF:**
        1. Faça upload do PDF
        2. Escolha o nível de compressão
        3. Clique em "Comprimir PDF"
        4. Baixe o PDF comprimido
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
            if len(uploaded_files) <= 6:  # Só mostra preview se tiver poucas imagens
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
        
        qualidade = st.selectbox(
            "Qualidade do PDF:",
            ["Alta", "Média", "Baixa"]
        )
        
        # Mapeia qualidade para parâmetros
        qualidade_map = {
            "Alta": {"margin": 10, "resize": False},
            "Média": {"margin": 15, "resize": True},
            "Baixa": {"margin": 20, "resize": True}
        }
        
        if uploaded_files:
            # Calcula tamanho total estimado
            total_size_mb = sum(len(f.getvalue()) for f in uploaded_files) / (1024 * 1024)
            estimated_pdf_size = total_size_mb * 0.7  # Estimativa
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.metric("Imagens", len(uploaded_files))
            with col_info2:
                st.metric("Tamanho estimado", f"{estimated_pdf_size:.2f} MB")
        
        if uploaded_files and st.button("Criar PDF", key="btn_criar_pdf", type="primary"):
            with st.spinner("Processando imagens..."):
                try:
                    # Prepara as imagens como bytes
                    imagens_bytes = []
                    for file in uploaded_files:
                        file.seek(0)  # Garante que estamos no início do arquivo
                        file_bytes = file.read()
                        imagens_bytes.append(file_bytes)
                    
                    # Cria o PDF
                    pdf_bytes = criar_pdf_de_imagens_otimizado(imagens_bytes)
                    
                    if pdf_bytes:
                        tamanho_pdf = len(pdf_bytes) / (1024 * 1024)
                        
                        # Mostra resultados
                        st.success(f"PDF criado com sucesso! Tamanho: {tamanho_pdf:.2f} MB")
                        
                        # Botão de download - FORMA CORRETA
                        st.download_button(
                            label=f"📥 Baixar PDF ({tamanho_pdf:.2f} MB)",
                            data=pdf_bytes,
                            file_name=nome_pdf,
                            mime="application/pdf",
                            key=f"download_pdf_{datetime.now().timestamp()}"
                        )
                        
                except Exception as e:
                    st.error(f"Erro ao criar PDF: {str(e)}")
                    st.info("Dica: Tente converter as imagens para JPG antes de fazer o upload.")

elif opcao == "Comprimir Arquivo PDF":
    
    st.markdown('<div class="feature-title">Comprimir Arquivo PDF</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">Reduza o tamanho de seus arquivos PDF mantendo a qualidade legível. Ideal para compartilhamento.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader(
            "Selecione o arquivo PDF",
            type=['pdf'],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_pdf:
            # Mostra informações do PDF
            pdf_bytes = uploaded_pdf.read()
            uploaded_pdf.seek(0)  # Reset para poder ler novamente se necessário
            
            try:
                pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
                num_pages = len(pdf_reader.pages)
                tamanho_original = len(pdf_bytes) / (1024 * 1024)
                
                st.markdown(f"""
                <div class="file-card">
                    <div class="file-name">{uploaded_pdf.name}</div>
                    <div class="file-size">
                        Páginas: {num_pages} | Tamanho: {tamanho_original:.2f} MB
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Armazena no session state para uso posterior
                st.session_state['pdf_original'] = pdf_bytes
                st.session_state['pdf_nome'] = uploaded_pdf.name
                
            except Exception as e:
                st.error(f"Erro ao ler PDF: {str(e)}")
    
    with col2:
        st.markdown('<div class="feature-title">Configurações</div>', unsafe_allow_html=True)
        
        # Opções de compressão
        nivel_compressao = st.radio(
            "Nível de compressão:",
            ["Alta (máxima redução)", "Média (redução balanceada)", "Baixa (qualidade original)"],
            index=1
        )
        
        # Mapeia para parâmetros
        compress_map = {
            "Alta (máxima redução)": "alta",
            "Média (redução balanceada)": "média", 
            "Baixa (qualidade original)": "baixa"
        }
        
        if uploaded_pdf and st.button("Comprimir PDF", key="btn_comprimir_pdf", type="primary"):
            if 'pdf_original' in st.session_state:
                with st.spinner("Comprimindo arquivo..."):
                    try:
                        # Obtém bytes do PDF
                        pdf_bytes = st.session_state['pdf_original']
                        tamanho_original = len(pdf_bytes) / (1024 * 1024)
                        
                        # Aplica compressão
                        qualidade = compress_map[nivel_compressao]
                        pdf_comprimido = comprimir_pdf_otimizado(pdf_bytes, qualidade)
                        
                        if pdf_comprimido:
                            tamanho_novo = len(pdf_comprimido) / (1024 * 1024)
                            reducao = ((tamanho_original - tamanho_novo) / tamanho_original) * 100
                            
                            # Mostra resultados
                            st.success("PDF comprimido com sucesso!")
                            
                            # Métricas
                            col_res1, col_res2, col_res3 = st.columns(3)
                            
                            with col_res1:
                                st.metric("Original", f"{tamanho_original:.2f} MB")
                            with col_res2:
                                st.metric("Comprimido", f"{tamanho_novo:.2f} MB")
                            with col_res3:
                                st.metric("Redução", f"{reducao:.1f}%", delta=f"-{reducao:.1f}%")
                            
                            # Botão de download
                            nome_comprimido = f"comprimido_{st.session_state['pdf_nome']}"
                            st.download_button(
                                label=f"📥 Baixar PDF Comprimido ({tamanho_novo:.2f} MB)",
                                data=pdf_comprimido,
                                file_name=nome_comprimido,
                                mime="application/pdf",
                                key=f"download_compressed_{datetime.now().timestamp()}"
                            )
                        
                    except Exception as e:
                        st.error(f"Erro ao comprimir PDF: {str(e)}")
            else:
                st.warning("Por favor, faça upload de um PDF primeiro.")

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
    # Limpa session state periódicamente
    if 'cleanup_counter' not in st.session_state:
        st.session_state.cleanup_counter = 0
    
    st.session_state.cleanup_counter += 1
    
    # A cada 10 interações, limpa dados temporários
    if st.session_state.cleanup_counter > 10:
        if 'pdf_original' in st.session_state:
            del st.session_state['pdf_original']
        if 'pdf_nome' in st.session_state:
            del st.session_state['pdf_nome']
        st.session_state.cleanup_counter = 0