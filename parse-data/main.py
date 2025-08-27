import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from datetime import datetime
import json
import re
import os

def parse_bibtex_to_mongodb_format(bibtex_file_path):
    """
    Convierte archivo BibTeX a formato semilla para MongoDB
    """
    
    # Configurar parser
    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    
    # Leer archivo
    with open(bibtex_file_path, 'r', encoding='utf-8') as bib_file:
        bib_database = bibtexparser.load(bib_file, parser=parser)
    
    articles_for_mongodb = []
    
    for entry in bib_database.entries:
        article_doc = {
            # Metadatos básicos
            'bibtex_id': entry.get('ID'),
            'title': clean_text(entry.get('title', '')),
            'authors': parse_authors(entry.get('author', '')),
            'year': int(entry.get('year', 0)) if entry.get('year', '').isdigit() else None,
            'publication_date': entry.get('year'),
            
            # Información de publicación
            'journal': entry.get('journal', ''),
            'publisher': entry.get('publisher', ''),
            'volume': entry.get('volume', ''),
            
            # Identificadores
            'doi': entry.get('doi', ''),
            'url': entry.get('url', ''),
            'isbn': entry.get('isbn', ''),
            'issn': entry.get('issn', ''),
            
            # Contenido
            'abstract': clean_text(entry.get('abstract', '')),
            'keywords': parse_keywords(entry.get('keywords', '')),
            
            # Campos para revisión sistemática
            'screening_status': 'pending',  # pending, included, excluded
            'screening_notes': '',
            'labels': [],

            'imported_from': 'bibtex',
            'source_file': bibtex_file_path.split('/')[-1]
        }
        
        articles_for_mongodb.append(article_doc)
    
    return articles_for_mongodb

def clean_text(text):
    """Limpia texto de caracteres especiales de LaTeX"""
    if not text:
        return ""
    
    # Remover llaves de LaTeX
    text = re.sub(r'[{}]', '', text)
    # Limpiar espacios múltiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def parse_authors(author_string):
    """Convierte string de autores a lista estructurada"""
    if not author_string:
        return []
    
    # BibTeX usa 'and' como separador
    authors = author_string.split(' and ')
    
    author_list = []
    for author in authors:
        author = clean_text(author.strip())
        if author:
            # Puedes hacer parsing más sofisticado aquí
            author_list.append({
                'full_name': author,
                'last_name': author.split()[-1] if author.split() else '',
                'first_name': ' '.join(author.split()[:-1]) if len(author.split()) > 1 else ''
            })
    
    return author_list

def save_to_json(articles, output_file):
    """
    Guarda los artículos en formato JSON para MongoDB Compass
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Archivo JSON guardado exitosamente: {output_file}")
        print(f"📊 Total de artículos exportados: {len(articles)}")
        
        return True
    except Exception as e:
        print(f"❌ Error al guardar archivo JSON: {e}")
        return False

def parse_keywords(keywords_string):
    """Convierte string de keywords a lista"""
    if not keywords_string:
        return []
    
    # Diferentes separadores posibles
    keywords = re.split(r'[,;]', keywords_string)
    return [kw.strip() for kw in keywords if kw.strip()]

def process_bibtex_file(bibtex_file_path, output_format='json'):
    """
    Función principal que procesa el archivo BibTeX y genera el output
    """
    print(f"🔄 Procesando archivo BibTeX: {bibtex_file_path}")
    
    # Verificar que el archivo existe
    if not os.path.exists(bibtex_file_path):
        print(f"❌ Archivo no encontrado: {bibtex_file_path}")
        return False
    
    try:
        # Procesar BibTeX
        articles = parse_bibtex_to_mongodb_format(bibtex_file_path)
        
        if not articles:
            print("❌ No se encontraron artículos en el archivo BibTeX")
            return False
        
        # Generar nombres de archivos de salida
        base_name = os.path.splitext(os.path.basename(bibtex_file_path))[0]
        
        if output_format.lower() == 'json':
            output_file = f"/home/santiago/Proyectos/revisiones-sistematicas/parse-data/data/{base_name}_mongodb.json"
            success = save_to_json(articles, output_file)
        else:
            print("❌ Formato no soportado. Use 'json' o 'jsonl'")
            return False
        
        if success:            
            # Mostrar preview de primer artículo
            print(f"\n🔍 PREVIEW DEL PRIMER ARTÍCULO:")
            print("-" * 40)
            print(json.dumps(articles[0], indent=2, ensure_ascii=False))
        
        return success
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return False

if __name__ == "__main__":
    articles = "/home/santiago/Proyectos/revisiones-sistematicas/parse-data/data/data.bib"
    output_format = "json"

    # Procesar archivo
    success = process_bibtex_file(articles, output_format)
    
    if success:
        print("\n✅ ¡Proceso completado exitosamente!")
        print("El archivo está listo para importar en MongoDB Compass")
    else:
        print("\n❌ El proceso falló. Revisa los errores arriba.")