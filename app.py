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
# FUNÇÕES PRINCIPAIS CORRIGIDAS - VERSÃO DEFINITIVA
# ============================================================================
def converter_para_bytes(dados):
    """Converte qualquer formato para bytes puros"""
    if isinstance(dados, bytes):
        return dados
    elif isinstance(dados, bytearray):
        return bytes(dados)
    elif isinstance(dados, str):
        return dados.encode('latin-1')
    elif hasattr(dados, 'getvalue'):
        return dados.getvalue()
    else:
        try:
            return bytes(dados)
        except:
            return str(dados).encode('latin-1')

def criar_pdf_de_imagens_definitivo(imagens_bytes_list):
    """Cria PDF a partir de imagens - VERSÃO DEFINITIVA E CONFIÁVEL"""
    try:
        pdf = FPDF()
        
        # Configuração básica
        pdf.set_auto_page_break(auto=False)
        
        # Lista para arquivos temporários
        temp_files = []
        
        for i, img_bytes in enumerate(imagens_bytes_list):
            try:
                # Abre a imagem
                img = Image.open(io.BytesIO(img_bytes))
                
                # Converte para RGB se necessário
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Cria fundo branco para imagens com transparência
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Cria arquivo temporário
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                    img.save(tmp_file, format='JPEG', quality=90)
                    temp_file_path = tmp_file.name
                    temp_files.append(temp_file_path)
                
                # Adiciona nova página
                pdf.add_page()
                
                # Adiciona imagem (centralizada)
                # Dimensões A4: 210 x 297 mm
                # Usa 190mm de largura para margens
                pdf.image(temp_file_path, x=10, y=10, w=190)
                
            except Exception as img_error:
                st.warning(f"Aviso na imagem {i+1}: {str(img_error)}")
                continue
        
        if len(temp_files) == 0:
            return None
        
        # Gera o PDF em um buffer de memória - FORMA MAIS CONFIÁVEL
        pdf_output = pdf.output(dest='S')
        
        # CONVERTE PARA BYTES DE FORMA ABSOLUTA
        pdf_bytes = converter_para_bytes(pdf_output)
        
        return pdf_bytes
        
    except Exception as e:
        st.error(f"Erro crítico ao criar PDF: {str(e)}")
        return None
        
    finally:
        # Limpa arquivos temporários
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass

def comprimir_pdf_definitivo(pdf_bytes):
    """Comprime PDF de forma definitiva"""
    try:
        # Garante que temos bytes
        pdf_bytes = converter_para_bytes(pdf_bytes)
        
        # Lê o PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        pdf_writer = PdfWriter()
        
        # Copia todas as páginas
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)
        
        # Tenta comprimir (não crítico se falhar)
        try:
            for page in pdf_writer.pages:
                page.compress_content_streams()
        except:
            pass  # Continua mesmo se não conseguir comprimir
        
        # Escreve para buffer
        output_buffer = io.BytesIO()
        pdf_writer.write(output_buffer)
        
        return output_buffer.getvalue()
        
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
        2. Configure o nome do arquivo
        3. Clique em "Criar PDF"
        4. Baixe o arquivo resultante
        
        **Comprimir PDF:**
        1. Faça upload do PDF
        2. Clique em "Comprimir PDF"
        3. Baixe o PDF comprimido
        """)
    
    st.markdown("---")
    
    # Informações do sistema
    st.markdown("**Informações:**")
    st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    st.caption("Status: Sistema operacional")

# ============================================================================
# CONTEÚDO PRINCIPAL - CONVERTER IMAGENS PARA PDF
# ============================================================================
if opcao == "Converter Imagens para PDF":
    
    st.markdown('<div class="feature-title">Converter Imagens para PDF</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">Transforme suas imagens em um documento PDF organizado. Suporta JPG, PNG, BMP, TIFF e WebP.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Selecione as imagens",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp'],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="img_uploader"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} imagem(s) selecionada(s)")
            
            # Mostra informações
            total_size_mb = sum(len(f.getvalue()) for f in uploaded_files) / (1024 * 1024)
            st.info(f"**Tamanho total das imagens:** {total_size_mb:.2f} MB")
            
            # Mostra preview
            if len(uploaded_files) <= 6:
                st.markdown("**Prévia das imagens:**")
                cols = st.columns(3)
                for idx, uploaded_file in enumerate(uploaded_files[:6]):
                    with cols[idx % 3]:
                        try:
                            img = Image.open(uploaded_file)
                            img.thumbnail((150, 150))
                            st.image(img, caption=uploaded_file.name[:20] + ("..." if len(uploaded_file.name) > 20 else ""))
                        except:
                            st.text(uploaded_file.name[:20] + "...")
    
    with col2:
        st.markdown('<div class="feature-title">Configurações</div>', unsafe_allow_html=True)
        
        nome_pdf = st.text_input(
            "Nome do PDF:",
            value=f"Documento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            key="pdf_name"
        )
        
        qualidade = st.selectbox(
            "Qualidade:",
            ["Alta", "Média", "Baixa"],
            index=0,
            key="qualidade"
        )
        
        orientacao = st.radio(
            "Orientação:",
            ["Retrato", "Paisagem"],
            horizontal=True,
            key="orientacao"
        )
        
        # Botão para criar PDF
        if uploaded_files:
            if st.button("✨ Criar PDF", type="primary", key="criar_pdf_btn", use_container_width=True):
                with st.spinner("Processando imagens..."):
                    try:
                        # Prepara as imagens
                        imagens_bytes = []
                        
                        # Barra de progresso
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, file in enumerate(uploaded_files):
                            status_text.text(f"Processando imagem {i+1} de {len(uploaded_files)}...")
                            file.seek(0)
                            img_bytes = file.read()
                            imagens_bytes.append(img_bytes)
                            progress_bar.progress((i + 1) / len(uploaded_files))
                        
                        status_text.text("Criando PDF...")
                        
                        # Cria o PDF
                        pdf_bytes = criar_pdf_de_imagens_definitivo(imagens_bytes)
                        
                        if pdf_bytes:
                            tamanho_pdf_mb = len(pdf_bytes) / (1024 * 1024)
                            
                            # Limpa barra de progresso
                            progress_bar.empty()
                            status_text.empty()
                            
                            st.success(f"✅ PDF criado com sucesso!")
                            
                            # Mostra métricas
                            col_metric1, col_metric2 = st.columns(2)
                            with col_metric1:
                                st.metric("Páginas", len(uploaded_files))
                            with col_metric2:
                                st.metric("Tamanho do PDF", f"{tamanho_pdf_mb:.2f} MB")
                            
                            # Botão de download - FORMA 100% CONFIÁVEL
                            st.markdown("---")
                            st.markdown("### 📥 Download")
                            
                            # Garante que são bytes
                            download_bytes = converter_para_bytes(pdf_bytes)
                            
                            st.download_button(
                                label=f"Baixar PDF ({tamanho_pdf_mb:.2f} MB)",
                                data=download_bytes,
                                file_name=nome_pdf,
                                mime="application/pdf",
                                key=f"download_{datetime.now().timestamp()}",
                                use_container_width=True
                            )
                            
                            # Também mostra alternativa de salvar
                            st.caption("💡 Dica: Clique no botão acima para salvar o PDF no seu computador")
                            
                        else:
                            st.error("❌ Falha ao criar o PDF. Nenhuma imagem válida foi processada.")
                            
                    except Exception as e:
                        st.error(f"❌ Erro crítico: {str(e)}")
                        st.info("""
                        **Soluções possíveis:**
                        1. Verifique se as imagens são válidas
                        2. Tente converter para JPG antes de fazer upload
                        3. Reduza o número de imagens
                        4. Tente imagens menores
                        """)
        else:
            st.info("⬆️ Faça upload das imagens acima para começar")

# ============================================================================
# CONTEÚDO PRINCIPAL - COMPRIMIR PDF
# ============================================================================
elif opcao == "Comprimir Arquivo PDF":
    
    st.markdown('<div class="feature-title">Comprimir Arquivo PDF</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">Reduza o tamanho de seus arquivos PDF para facilitar o armazenamento e compartilhamento.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader(
            "Selecione o arquivo PDF",
            type=['pdf'],
            accept_multiple_files=False,
            label_visibility="collapsed",
            key="pdf_uploader"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_pdf:
            try:
                # Lê o PDF
                pdf_bytes = uploaded_pdf.read()
                uploaded_pdf.seek(0)  # Reset para permitir releitura
                
                # Obtém informações
                tamanho_original_mb = len(pdf_bytes) / (1024 * 1024)
                
                st.success(f"✅ PDF carregado: {uploaded_pdf.name}")
                st.info(f"**Tamanho original:** {tamanho_original_mb:.2f} MB")
                
                # Armazena no session state
                st.session_state['pdf_para_comprimir'] = pdf_bytes
                st.session_state['pdf_nome_original'] = uploaded_pdf.name
                st.session_state['tamanho_original'] = tamanho_original_mb
                
            except Exception as e:
                st.error(f"Erro ao ler PDF: {str(e)}")
    
    with col2:
        st.markdown('<div class="feature-title">Configurações</div>', unsafe_allow_html=True)
        
        # Configurações
        nivel = st.selectbox(
            "Nível de compressão:",
            ["Leve (melhor qualidade)", "Moderado (equilibrado)", "Máximo (menor tamanho)"],
            key="nivel_compressao"
        )
        
        manter_qualidade = st.checkbox("Manter qualidade visual", value=True)
        
        # Botão para comprimir
        if 'pdf_para_comprimir' in st.session_state:
            if st.button("⚡ Comprimir PDF", type="primary", key="comprimir_pdf_btn", use_container_width=True):
                with st.spinner("Comprimindo PDF..."):
                    try:
                        # Obtém dados
                        pdf_bytes = st.session_state['pdf_para_comprimir']
                        tamanho_original = st.session_state['tamanho_original']
                        
                        # Comprime
                        pdf_comprimido = comprimir_pdf_definitivo(pdf_bytes)
                        
                        if pdf_comprimido:
                            tamanho_novo_mb = len(pdf_comprimido) / (1024 * 1024)
                            reducao = ((tamanho_original - tamanho_novo_mb) / tamanho_original) * 100
                            
                            st.success(f"✅ PDF comprimido com sucesso!")
                            
                            # Mostra resultados
                            col_res1, col_res2, col_res3 = st.columns(3)
                            
                            with col_res1:
                                st.metric("Original", f"{tamanho_original:.2f} MB")
                            with col_res2:
                                st.metric("Comprimido", f"{tamanho_novo_mb:.2f} MB")
                            with col_res3:
                                st.metric("Redução", f"{reducao:.1f}%", delta=f"-{reducao:.1f}%")
                            
                            # Botão de download
                            st.markdown("---")
                            st.markdown("### 📥 Download")
                            
                            nome_original = st.session_state['pdf_nome_original']
                            nome_comprimido = f"comprimido_{nome_original}"
                            
                            # Garante bytes
                            download_bytes = converter_para_bytes(pdf_comprimido)
                            
                            st.download_button(
                                label=f"Baixar PDF Comprimido ({tamanho_novo_mb:.2f} MB)",
                                data=download_bytes,
                                file_name=nome_comprimido,
                                mime="application/pdf",
                                key=f"download_comp_{datetime.now().timestamp()}",
                                use_container_width=True
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao comprimir: {str(e)}")
        else:
            if uploaded_pdf:
                st.info("⚙️ Configure as opções acima e clique em 'Comprimir PDF'")
            else:
                st.info("⬆️ Faça upload de um PDF para começar")

# ============================================================================
# RODAPÉ PERSONALIZADO
# ============================================================================
st.markdown("""
<div class="footer">
    <div class="footer-text">
        Criado por Adrielly 
        <span class="heart">❤</span>
        <br>
        Para facilitar seu trabalho, te amo Francisco!
        <br>
        <small style="opacity: 0.7;">Última atualização: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """</small>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# LIMPEZA DE SESSION STATE
# ============================================================================
if 'cleanup_counter' not in st.session_state:
    st.session_state.cleanup_counter = 0

st.session_state.cleanup_counter += 1

# Limpa a cada 5 execuções
if st.session_state.cleanup_counter > 5:
    keys_to_clean = ['pdf_para_comprimir', 'pdf_nome_original', 'tamanho_original']
    for key in keys_to_clean:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.cleanup_counter = 0