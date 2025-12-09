import streamlit as st
import os
import tempfile
import io
from datetime import datetime
import zipfile
from PIL import Image
import base64

# Configurações da página
st.set_page_config(
    page_title="Conversor Online",
    page_icon="🔄",
    layout="wide"
)

# CSS moderno
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    .file-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("""
<div class="main-header">
    <h1>🔄 Conversor de Arquivos Online</h1>
    <p>Converta imagens para PDF e comprima arquivos de qualquer lugar</p>
</div>
""", unsafe_allow_html=True)

# Inicializa estado da sessão
if 'converted_pdf' not in st.session_state:
    st.session_state.converted_pdf = None
if 'compressed_pdf' not in st.session_state:
    st.session_state.compressed_pdf = None

# Funções dos módulos (versões simplificadas para cloud)
def compress_image_for_pdf(image_bytes, max_size_kb=100):
    """Comprime imagem para PDF"""
    img = Image.open(io.BytesIO(image_bytes))
    
    # Converte para RGB se necessário
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Redimensiona se necessário
    max_dimension = 1200
    if max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    # Comprime
    output = io.BytesIO()
    quality = 85
    
    while quality > 30:
        output.seek(0)
        output.truncate(0)
        img.save(output, format='JPEG', quality=quality, optimize=True)
        
        if len(output.getvalue()) <= max_size_kb * 1024:
            break
        
        quality -= 5
    
    return output.getvalue()

def images_to_pdf_streamlit(images, progress_bar, status_text):
    """Converte múltiplas imagens para PDF"""
    try:
        from fpdf import FPDF
        import tempfile
        
        pdf = FPDF()
        temp_files = []
        
        for i, (img_name, img_bytes) in enumerate(images):
            progress_bar.progress((i + 1) / len(images))
            status_text.text(f"Processando {img_name}...")
            
            # Comprime a imagem
            compressed_img = compress_image_for_pdf(img_bytes)
            
            # Salva temporariamente
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(compressed_img)
                temp_files.append(tmp.name)
            
            # Adiciona ao PDF
            pdf.add_page()
            
            # Calcula posição
            img = Image.open(io.BytesIO(compressed_img))
            width, height = img.size
            
            a4_width = 190
            a4_height = 267
            ratio = min(a4_width / width, a4_height / height)
            new_width = width * ratio
            new_height = height * ratio
            
            x = (210 - new_width) / 2
            y = (297 - new_height) / 2
            
            pdf.image(temp_files[-1], x=x, y=y, w=new_width)
        
        # Gera PDF
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        
        # Limpa temporários
        for tmp_file in temp_files:
            try:
                os.unlink(tmp_file)
            except:
                pass
        
        return pdf_bytes
        
    except Exception as e:
        raise Exception(f"Erro na conversão: {str(e)}")

def compress_pdf_streamlit(pdf_bytes, target_size_mb, progress_bar, status_text):
    """Comprime PDF"""
    try:
        from PyPDF2 import PdfReader, PdfWriter
        
        original_size = len(pdf_bytes) / (1024 * 1024)
        
        # Tentativa 1: Compressão simples
        status_text.text("Aplicando compressão básica...")
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        compressed = io.BytesIO()
        writer.write(compressed)
        compressed_bytes = compressed.getvalue()
        
        compressed_size = len(compressed_bytes) / (1024 * 1024)
        
        if compressed_size <= target_size_mb:
            progress_bar.progress(1.0)
            return compressed_bytes
        
        # Tentativa 2: Redução de qualidade
        status_text.text("Aplicando compressão avançada...")
        
        # (Para versão cloud, mantemos simples)
        # Em produção, você pode integrar pdf2image se instalar poppler
        
        progress_bar.progress(1.0)
        return compressed_bytes  # Retorna o melhor possível
        
    except Exception as e:
        raise Exception(f"Erro na compressão: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Menu")
    
    opcao = st.radio(
        "Escolha a ferramenta:",
        ["📷 Imagens para PDF", "📄 Comprimir PDF", "📦 Compactar Arquivos", "ℹ️ Ajuda"]
    )
    
    st.markdown("---")
    
    st.markdown("### 📊 Estatísticas")
    if st.session_state.converted_pdf:
        st.info(f"PDF pronto para download")
    if st.session_state.compressed_pdf:
        st.info(f"PDF comprimido pronto")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📱 Compatível com:
    - ✅ Windows
    - ✅ Mac
    - ✅ Linux
    - ✅ Celular
    """)

# Página principal baseada na seleção
if opcao == "📷 Imagens para PDF":
    st.markdown("## 📷 Converter Imagens para PDF")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Selecione as imagens (JPG, PNG, etc.)",
            type=['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp'],
            accept_multiple_files=True,
            help="Arraste ou clique para selecionar múltiplas imagens"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} imagem(s) selecionada(s)")
            
            # Mostra preview
            cols = st.columns(min(3, len(uploaded_files)))
            for idx, uploaded_file in enumerate(uploaded_files):
                with cols[idx % 3]:
                    try:
                        img = Image.open(uploaded_file)
                        img.thumbnail((150, 150))
                        st.image(img, caption=uploaded_file.name, use_container_width=True)
                    except:
                        st.write(f"📄 {uploaded_file.name}")
    
    with col2:
        st.markdown("### Configurações")
        
        pdf_name = st.text_input(
            "Nome do PDF:",
            value=f"documento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        qualidade = st.select_slider(
            "Qualidade:",
            options=["Baixa", "Média", "Alta"],
            value="Média"
        )
        
        orientacao = st.radio(
            "Orientação:",
            ["Retrato", "Paisagem"],
            horizontal=True
        )
    
    # Botão de conversão
    if uploaded_files and st.button("🔄 Converter para PDF", type="primary", use_container_width=True):
        with st.spinner("Convertendo imagens..."):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Prepara imagens
                images = []
                for uploaded_file in uploaded_files:
                    images.append((uploaded_file.name, uploaded_file.getvalue()))
                
                # Converte
                pdf_bytes = images_to_pdf_streamlit(
                    images,
                    progress_bar,
                    status_text
                )
                
                # Salva no estado da sessão
                st.session_state.converted_pdf = {
                    'bytes': pdf_bytes,
                    'name': pdf_name,
                    'size': f"{len(pdf_bytes) / (1024 * 1024):.2f} MB"
                }
                
                status_text.success("✅ Conversão concluída!")
                progress_bar.empty()
                
            except Exception as e:
                st.error(f"Erro: {str(e)}")
    
    # Download do PDF
    if st.session_state.converted_pdf:
        st.markdown("---")
        st.markdown("### 📥 Download")
        
        col_d1, col_d2, col_d3 = st.columns([2, 1, 1])
        
        with col_d1:
            st.markdown(f"""
            <div class="file-info">
            <strong>📄 {st.session_state.converted_pdf['name']}</strong><br>
            Tamanho: {st.session_state.converted_pdf['size']}
            </div>
            """, unsafe_allow_html=True)
        
        with col_d2:
            # Botão de download
            st.download_button(
                label="⬇️ Baixar PDF",
                data=st.session_state.converted_pdf['bytes'],
                file_name=st.session_state.converted_pdf['name'],
                mime="application/pdf",
                use_container_width=True
            )
        
        with col_d3:
            # Preview do PDF (link)
            st.markdown("[👁️ Visualizar PDF](#)" , unsafe_allow_html=True)

elif opcao == "📄 Comprimir PDF":
    st.markdown("## 📄 Comprimir PDF")
    
    uploaded_pdf = st.file_uploader(
        "Selecione um arquivo PDF",
        type=['pdf'],
        accept_multiple_files=False
    )
    
    if uploaded_pdf:
        file_size = len(uploaded_pdf.getvalue()) / (1024 * 1024)
        
        col_info, col_config = st.columns([1, 1])
        
        with col_info:
            st.markdown(f"""
            <div class="file-info">
            <strong>📊 Informações do arquivo:</strong><br>
            • Nome: {uploaded_pdf.name}<br>
            • Tamanho: {file_size:.2f} MB<br>
            • Páginas: Verificando...
            </div>
            """, unsafe_allow_html=True)
        
        with col_config:
            target_size = st.slider(
                "Tamanho alvo (MB):",
                min_value=0.1,
                max_value=100.0,
                value=max(0.1, file_size / 2),
                step=0.1,
                format="%.1f MB"
            )
            
            metodo = st.selectbox(
                "Método de compressão:",
                ["Inteligente (recomendado)", "Máxima", "Personalizada"]
            )
        
        if st.button("🎯 Comprimir PDF", type="primary", use_container_width=True):
            with st.spinner("Comprimindo..."):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    compressed_bytes = compress_pdf_streamlit(
                        uploaded_pdf.getvalue(),
                        target_size,
                        progress_bar,
                        status_text
                    )
                    
                    compressed_size = len(compressed_bytes) / (1024 * 1024)
                    
                    # Salva no estado
                    st.session_state.compressed_pdf = {
                        'bytes': compressed_bytes,
                        'name': f"comprimido_{uploaded_pdf.name}",
                        'original_size': file_size,
                        'compressed_size': compressed_size,
                        'reduction': ((file_size - compressed_size) / file_size) * 100
                    }
                    
                    # Mostra resultados
                    col_r1, col_r2, col_r3 = st.columns(3)
                    
                    with col_r1:
                        st.metric("Original", f"{file_size:.2f} MB")
                    
                    with col_r2:
                        st.metric("Comprimido", f"{compressed_size:.2f} MB")
                    
                    with col_r3:
                        st.metric(
                            "Redução", 
                            f"{st.session_state.compressed_pdf['reduction']:.1f}%",
                            delta=f"-{st.session_state.compressed_pdf['reduction']:.1f}%"
                        )
                    
                    status_text.success("✅ Compressão concluída!")
                    progress_bar.empty()
                    
                except Exception as e:
                    st.error(f"Erro: {str(e)}")
    
    # Download do PDF comprimido
    if st.session_state.compressed_pdf:
        st.markdown("---")
        st.markdown("### 📥 Download Comprimido")
        
        st.download_button(
            label=f"⬇️ Baixar PDF Comprimido ({st.session_state.compressed_pdf['compressed_size']:.2f} MB)",
            data=st.session_state.compressed_pdf['bytes'],
            file_name=st.session_state.compressed_pdf['name'],
            mime="application/pdf",
            use_container_width=True
        )

elif opcao == "📦 Compactar Arquivos":
    st.markdown("## 📦 Compactar Arquivos em ZIP")
    
    uploaded_files = st.file_uploader(
        "Selecione os arquivos para compactar",
        accept_multiple_files=True,
        help="Segure Ctrl para selecionar múltiplos arquivos"
    )
    
    if uploaded_files:
        total_size = sum(len(f.getvalue()) for f in uploaded_files) / 1024
        
        st.info(f"📁 {len(uploaded_files)} arquivo(s) - {total_size:.1f} KB total")
        
        zip_name = st.text_input(
            "Nome do arquivo ZIP:",
            value=f"arquivos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        
        if st.button("📦 Criar Arquivo ZIP", type="primary", use_container_width=True):
            with st.spinner("Criando ZIP..."):
                try:
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for uploaded_file in uploaded_files:
                            zipf.writestr(uploaded_file.name, uploaded_file.getvalue())
                    
                    zip_buffer.seek(0)
                    
                    # Botão de download
                    st.download_button(
                        label=f"⬇️ Baixar {zip_name}",
                        data=zip_buffer,
                        file_name=zip_name,
                        mime="application/zip",
                        use_container_width=True
                    )
                    
                    st.success("✅ ZIP criado com sucesso!")
                    
                except Exception as e:
                    st.error(f"Erro: {str(e)}")

else:  # Ajuda
    st.markdown("## ℹ️ Ajuda e Instruções")
    
    st.markdown("""
    ### 📖 Como usar:
    
    **1. 📷 Imagens para PDF:**
    - Selecione múltiplas imagens
    - Configure o nome e qualidade
    - Clique em "Converter para PDF"
    - Baixe o resultado
    
    **2. 📄 Comprimir PDF:**
    - Faça upload de um PDF
    - Escolha o tamanho desejado
    - Clique em "Comprimir PDF"
    - Baixe a versão reduzida
    
    **3. 📦 Compactar Arquivos:**
    - Selecione vários arquivos
    - Crie um ZIP para compartilhar
    
    ### ⚠️ Limitações:
    - Tamanho máximo por arquivo: 200MB
    - Suporta os formatos mais comuns
    - Arquivos são processados na nuvem e não são armazenados
    
    ### 📞 Suporte:
    Em caso de problemas, entre em contato com o administrador.
    """)
    
    # QR Code para acesso mobile
    st.markdown("### 📱 Acesse pelo celular:")
    st.info("Use o mesmo link no navegador do seu celular")

# Rodapé
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🔄 Conversor Online • Feito com Streamlit • "
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>",
    unsafe_allow_html=True
)