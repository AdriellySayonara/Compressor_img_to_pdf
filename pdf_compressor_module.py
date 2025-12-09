import os
import sys
import img2pdf
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import io

def get_file_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)

def compress_pdf_simple(input_path, output_path):
    """Compressão básica (remove metadados, compacta streams)"""
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.add_metadata(reader.metadata)
    with open(output_path, "wb") as f:
        writer.write(f)

def compress_pdf_with_images(input_path, output_path, quality=80, dpi=150):
    """Converte PDF em imagens, comprime e recria PDF"""
    images = convert_from_path(input_path, dpi=dpi)
    compressed_images = []

    for img in images:
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG", quality=quality, optimize=True)
        img_bytes.seek(0)
        compressed_images.append(img_bytes)

    with open(output_path, "wb") as f:
        f.write(img2pdf.convert([img.getvalue() for img in compressed_images]))

def main():
    print("=== Compressor de PDF com limite de tamanho ===")
    
    input_path = input("Digite o caminho completo do arquivo PDF: ").strip().strip('"')
    if not os.path.isfile(input_path) or not input_path.lower().endswith('.pdf'):
        print("Arquivo inválido!")
        return

    try:
        max_size_mb = float(input("Digite o tamanho máximo desejado (em MB): "))
        if max_size_mb <= 0:
            print("Tamanho deve ser maior que zero!")
            return
    except ValueError:
        print("Valor inválido!")
        return

    original_size = get_file_size_mb(input_path)
    print(f"Tamanho original: {original_size:.2f} MB")
    if original_size <= max_size_mb:
        print("O arquivo já está dentro do limite! Nenhuma compressão necessária.")
        return

    temp_path = "temp_compressed.pdf"
    output_path = os.path.splitext(input_path)[0] + "_compressed.pdf"

    # Primeiro, tenta compressão simples
    compress_pdf_simple(input_path, temp_path)
    size_after_simple = get_file_size_mb(temp_path)
    print(f"Tamanho após compressão simples: {size_after_simple:.2f} MB")

    if size_after_simple <= max_size_mb:
        os.rename(temp_path, output_path)
        print(f"PDF comprimido salvo em: {output_path}")
        return

    # Se ainda estiver grande, usa compressão com imagens
    print("Aplicando compressão avançada com controle de qualidade...")

    quality = 95
    dpi = 150
    step = 5

    while quality >= 10:
        try:
            compress_pdf_with_images(input_path, temp_path, quality=quality, dpi=dpi)
            current_size = get_file_size_mb(temp_path)
            print(f"Qualidade: {quality} | DPI: {dpi} | Tamanho: {current_size:.2f} MB")
            if current_size <= max_size_mb:
                os.rename(temp_path, output_path)
                print(f"PDF comprimido salvo em: {output_path}")
                return
        except Exception as e:
            print(f"Erro na compressão com qualidade {quality}: {e}")

        quality -= step

    # Último recurso: reduzir DPI
    if quality < 10:
        print("Tentando reduzir DPI...")
        quality = 80
        for new_dpi in [120, 100, 80]:
            try:
                compress_pdf_with_images(input_path, temp_path, quality=quality, dpi=new_dpi)
                current_size = get_file_size_mb(temp_path)
                print(f"Qualidade: {quality} | DPI: {new_dpi} | Tamanho: {current_size:.2f} MB")
                if current_size <= max_size_mb:
                    os.rename(temp_path, output_path)
                    print(f"PDF comprimido salvo em: {output_path}")
                    return
            except Exception as e:
                print(f"Erro com DPI {new_dpi}: {e}")

    # Se nada funcionar
    if os.path.exists(temp_path):
        os.remove(temp_path)
    print("Não foi possível comprimir o PDF abaixo do tamanho desejado.")

if __name__ == "__main__":
    main()