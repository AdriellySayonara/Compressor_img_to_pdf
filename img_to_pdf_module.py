import os
import tempfile
from PIL import Image
from fpdf import FPDF
import io
import glob
import natsort

def compress_image(image_path, max_size_kb=100):
    """
    Comprime uma imagem mantendo a qualidade aceitável
    """
    img = Image.open(image_path)
    
    # Converte para RGB se for PNG com canal alpha
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Redimensiona se necessário (mantém proporção)
    max_dimension = 1200
    if max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    # Comprime a imagem
    output = io.BytesIO()
    quality = 85
    
    while quality > 30:
        output.seek(0)
        output.truncate(0)
        img.save(output, format='JPEG', quality=quality, optimize=True)
        
        if len(output.getvalue()) <= max_size_kb * 1024:
            break
        
        quality -= 5
    
    output.seek(0)
    return output

def get_image_files(input_paths):
    """
    Obtém lista de arquivos de imagem a partir de caminhos ou diretórios
    """
    image_files = []
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp')
    
    for path in input_paths:
        if os.path.isfile(path):
            # Se for um arquivo, verifica se é uma imagem
            if path.lower().endswith(supported_formats):
                image_files.append(path)
        elif os.path.isdir(path):
            # Se for um diretório, busca todas as imagens em ordem natural
            for format in supported_formats:
                # Busca arquivos com extensão minúscula e maiúscula
                files_lower = glob.glob(os.path.join(path, f'*{format}'))
                files_upper = glob.glob(os.path.join(path, f'*{format.upper()}'))
                
                # Adiciona todos os arquivos encontrados
                image_files.extend(files_lower)
                image_files.extend(files_upper)
    
    # Remove duplicatas
    image_files = list(set(image_files))
    
    # Ordena naturalmente (1, 2, 3, 10, 11 em vez de 1, 10, 11, 2, 3)
    try:
        # Tenta usar natsort se estiver instalado
        import natsort
        image_files = natsort.natsorted(image_files)
    except ImportError:
        # Fallback para ordenação alfabética simples
        image_files.sort()
    
    return image_files

def images_to_pdf(image_paths, output_pdf_path, max_pdf_size_mb=3):
    """
    Converte imagens para PDF com limite de tamanho
    """
    pdf = FPDF()
    temp_files = []
    
    try:
        # Processa cada imagem
        for i, image_path in enumerate(image_paths):
            print(f"Processando imagem {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
            
            # Comprime a imagem
            compressed_image = compress_image(image_path)
            
            # Salva temporariamente para o FPDF
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_file.write(compressed_image.getvalue())
            temp_file.close()
            temp_files.append(temp_file.name)
            
            # Adiciona ao PDF
            pdf.add_page()
            
            # Obtém dimensões da imagem
            img = Image.open(temp_file.name)
            width, height = img.size
            
            # Calcula dimensões para caber na página A4
            a4_width = 190  # mm
            a4_height = 267  # mm
            
            ratio = min(a4_width / width, a4_height / height)
            new_width = width * ratio
            new_height = height * ratio
            
            # Centraliza na página
            x = (210 - new_width) / 2  # 210mm é a largura da A4
            y = (297 - new_height) / 2  # 297mm é a altura da A4
            
            pdf.image(temp_file.name, x=x, y=y, w=new_width)
        
        # Salva o PDF
        pdf.output(output_pdf_path)
        
        # Verifica o tamanho e ajusta se necessário
        pdf_size_mb = os.path.getsize(output_pdf_path) / (1024 * 1024)
        
        if pdf_size_mb > max_pdf_size_mb:
            print(f"PDF gerado tem {pdf_size_mb:.2f}MB (acima do limite de {max_pdf_size_mb}MB)")
            print("Ajustando compressão...")
            
            # Se ainda estiver muito grande, recomeça com compressão mais agressiva
            return images_to_pdf_aggressive(image_paths, output_pdf_path, max_pdf_size_mb)
        else:
            print(f"PDF gerado com sucesso: {pdf_size_mb:.2f}MB")
            return True
            
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return False
    finally:
        # Limpa arquivos temporários
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

def images_to_pdf_aggressive(image_paths, output_pdf_path, max_pdf_size_mb=3):
    """
    Versão mais agressiva de compressão para PDFs grandes
    """
    pdf = FPDF()
    temp_files = []
    
    try:
        for i, image_path in enumerate(image_paths):
            print(f"Processando com compressão agressiva: {i+1}/{len(image_paths)}")
            
            img = Image.open(image_path)
            
            # Converte para RGB se necessário
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Redimensiona mais agressivamente
            max_dimension = 800
            if max(img.size) > max_dimension:
                ratio = max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Compressão mais agressiva
            output = io.BytesIO()
            quality = 50
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_file.write(output.getvalue())
            temp_file.close()
            temp_files.append(temp_file.name)
            
            pdf.add_page()
            
            # Dimensões reduzidas
            width, height = img.size
            a4_width = 150
            a4_height = 200
            ratio = min(a4_width / width, a4_height / height)
            new_width = width * ratio
            new_height = height * ratio
            
            x = (210 - new_width) / 2
            y = (297 - new_height) / 2
            
            pdf.image(temp_file.name, x=x, y=y, w=new_width)
        
        pdf.output(output_pdf_path)
        pdf_size_mb = os.path.getsize(output_pdf_path) / (1024 * 1024)
        
        if pdf_size_mb > max_pdf_size_mb:
            print(f"Ainda muito grande ({pdf_size_mb:.2f}MB). Reduzindo qualidade ainda mais...")
            return reduce_pages_or_quality(image_paths, output_pdf_path, max_pdf_size_mb)
        else:
            print(f"PDF gerado com compressão agressiva: {pdf_size_mb:.2f}MB")
            return True
            
    except Exception as e:
        print(f"Erro na compressão agressiva: {e}")
        return False
    finally:
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

def reduce_pages_or_quality(image_paths, output_pdf_path, max_pdf_size_mb):
    """
    Reduz ainda mais a qualidade ou número de páginas se necessário
    """
    pdf = FPDF()
    temp_files = []
    
    try:
        for i, image_path in enumerate(image_paths):
            print(f"Processando com compressão máxima: {i+1}/{len(image_paths)}")
            
            img = Image.open(image_path)
            
            # Converte para RGB se necessário
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Redimensiona muito agressivamente
            max_dimension = 600
            if max(img.size) > max_dimension:
                ratio = max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Compressão máxima
            output = io.BytesIO()
            quality = 30
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_file.write(output.getvalue())
            temp_file.close()
            temp_files.append(temp_file.name)
            
            pdf.add_page()
            
            # Dimensões muito reduzidas
            width, height = img.size
            a4_width = 120
            a4_height = 150
            ratio = min(a4_width / width, a4_height / height)
            new_width = width * ratio
            new_height = height * ratio
            
            x = (210 - new_width) / 2
            y = (297 - new_height) / 2
            
            pdf.image(temp_file.name, x=x, y=y, w=new_width)
        
        pdf.output(output_pdf_path)
        pdf_size_mb = os.path.getsize(output_pdf_path) / (1024 * 1024)
        
        if pdf_size_mb > max_pdf_size_mb:
            print(f"PDF final: {pdf_size_mb:.2f}MB (ainda acima do limite, mas é o melhor possível)")
            return True
        else:
            print(f"PDF gerado com compressão máxima: {pdf_size_mb:.2f}MB")
            return True
            
    except Exception as e:
        print(f"Erro na compressão máxima: {e}")
        return False
    finally:
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

def natural_sort_key(s):
    """
    Função para ordenação natural de strings
    """
    import re
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

# Exemplo de uso
if __name__ == "__main__":
    # Lista de caminhos das imagens ou diretórios
    input_paths = [
        r"E:\Código uteis\img_to_pdf\conversas2"  # Use raw string ou caminho correto
    ]
    
    # Obtém todas as imagens
    image_files = get_image_files(input_paths)
    
    # Ordena naturalmente (para garantir a ordem correta)
    try:
        image_files.sort(key=natural_sort_key)
    except:
        image_files.sort()
    
    print(f"Encontradas {len(image_files)} imagens na ordem:")
    for i, img in enumerate(image_files, 1):
        print(f"  {i:2d}. {os.path.basename(img)}")
    
    if not image_files:
        print("Nenhuma imagem válida encontrada!")
    else:
        # Gera o PDF
        success = images_to_pdf(image_files, "Conversas com genitor II.pdf", max_pdf_size_mb=3)
        
        if success:
            print("PDF criado com sucesso!")
            print(f"Arquivo: {os.path.abspath('Conversas com genitor II.pdf')}")
        else:
            print("Falha ao criar PDF.")