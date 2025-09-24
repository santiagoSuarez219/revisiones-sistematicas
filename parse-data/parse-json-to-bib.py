import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bwriter import BibTexWriter
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

# ==================== NUEVAS FUNCIONES PARA JSON A BIBTEX ====================

def load_json_articles(json_file_path):
    """
    Carga artículos desde archivo JSON (formato MongoDB)
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"✅ Archivo JSON cargado exitosamente: {json_file_path}")
        print(f"📊 Total de artículos cargados: {len(articles)}")
        
        return articles
    except Exception as e:
        print(f"❌ Error al cargar archivo JSON: {e}")
        return []

def authors_to_bibtex_string(authors_list):
    """
    Convierte lista de autores estructurada a formato BibTeX
    """
    if not authors_list or not isinstance(authors_list, list):
        return ""
    
    author_strings = []
    for author in authors_list:
        if isinstance(author, dict):
            # Usar full_name si está disponible, sino construir desde first y last
            if author.get('full_name'):
                author_strings.append(author['full_name'])
            elif author.get('first_name') and author.get('last_name'):
                # Formato: "Apellido, Nombre"
                author_strings.append(f"{author['last_name']}, {author['first_name']}")
            elif author.get('last_name'):
                author_strings.append(author['last_name'])
        elif isinstance(author, str):
            author_strings.append(author)
    
    # BibTeX usa 'and' como separador de autores
    return " and ".join(author_strings)

def keywords_to_bibtex_string(keywords_list):
    """
    Convierte lista de keywords a string para BibTeX
    """
    if not keywords_list or not isinstance(keywords_list, list):
        return ""
    
    return ", ".join([str(kw) for kw in keywords_list])

def escape_bibtex_text(text):
    """
    Escapa caracteres especiales para BibTeX
    """
    if not text:
        return ""
    
    # Convertir a string si no lo es
    text = str(text)
    
    # Escapar caracteres especiales comunes en BibTeX
    replacements = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '^': '\\^{}',
        '_': '\\_',
        '~': '\\~{}',
        '{': '\\{',
        '}': '\\}',
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text

def determine_entry_type(article):
    """
    Determina el tipo de entrada BibTeX basado en los campos disponibles
    """
    # Verificar campos para determinar tipo
    if article.get('journal'):
        return 'article'
    elif article.get('booktitle'):
        return 'inproceedings'
    elif article.get('publisher') and not article.get('journal'):
        return 'book'
    elif article.get('school'):
        return 'phdthesis'
    elif article.get('institution'):
        return 'techreport'
    else:
        return 'article'  # Por defecto

def convert_mongodb_to_bibtex_entry(article):
    """
    Convierte un artículo en formato MongoDB a entrada BibTeX
    """
    # Generar ID si no existe
    bibtex_id = article.get('bibtex_id')
    if not bibtex_id:
        # Generar ID basado en primer autor y año
        authors = article.get('authors', [])
        year = article.get('year', 'unknown')
        if authors and isinstance(authors, list) and len(authors) > 0:
            first_author = authors[0]
            if isinstance(first_author, dict):
                last_name = first_author.get('last_name', 'unknown')
            else:
                last_name = str(first_author).split()[-1] if first_author else 'unknown'
            bibtex_id = f"{last_name}{year}".replace(' ', '').replace(',', '')
        else:
            bibtex_id = f"article{year}"
    
    # Crear entrada BibTeX
    entry = {
        'ID': bibtex_id,
        'ENTRYTYPE': determine_entry_type(article),
    }
    
    # Mapear campos de MongoDB a BibTeX
    field_mapping = {
        'title': 'title',
        'journal': 'journal',
        'year': 'year',
        'volume': 'volume',
        'publisher': 'publisher',
        'doi': 'doi',
        'url': 'url',
        'isbn': 'isbn',
        'issn': 'issn',
        'abstract': 'abstract',
    }
    
    # Agregar campos básicos
    for mongo_field, bibtex_field in field_mapping.items():
        value = article.get(mongo_field)
        if value:
            # Escapar texto para BibTeX
            entry[bibtex_field] = escape_bibtex_text(str(value))
    
    # Procesar autores
    authors = article.get('authors', [])
    if authors:
        entry['author'] = authors_to_bibtex_string(authors)
    
    # Procesar keywords
    keywords = article.get('keywords', [])
    if keywords:
        entry['keywords'] = keywords_to_bibtex_string(keywords)
    
    # Agregar campos específicos de la revisión sistemática como nota
    labels = article.get('labels', [])
    screening_status = article.get('screening_status', '')
    screening_notes = article.get('screening_notes', '')
    
    # Crear nota con información de revisión
    note_parts = []
    if screening_status:
        note_parts.append(f"Status: {screening_status}")
    if labels:
        note_parts.append(f"Labels: {', '.join(labels)}")
    if screening_notes:
        note_parts.append(f"Notes: {screening_notes}")
    
    if note_parts:
        entry['note'] = escape_bibtex_text("; ".join(note_parts))
    
    return entry

def save_to_bibtex(articles, output_file):
    """
    Guarda lista de artículos como archivo BibTeX
    """
    try:
        # Crear base de datos BibTeX
        bib_database = bibtexparser.bibdatabase.BibDatabase()
        bib_database.entries = []
        
        # Convertir cada artículo
        for article in articles:
            entry = convert_mongodb_to_bibtex_entry(article)
            bib_database.entries.append(entry)
        
        # Configurar writer para formato limpio
        writer = BibTexWriter()
        writer.indent = '  '  # Indentación
        writer.align_values = True  # Alinear valores
        writer.order_entries_by = 'ID'  # Ordenar por ID
        writer.add_trailing_comma = True  # Coma al final
        
        # Escribir archivo
        with open(output_file, 'w', encoding='utf-8') as bib_file:
            bibtexparser.dump(bib_database, bib_file, writer=writer)
        
        print(f"✅ Archivo BibTeX guardado exitosamente: {output_file}")
        print(f"📊 Total de entradas exportadas: {len(bib_database.entries)}")
        
        return True
    except Exception as e:
        print(f"❌ Error al guardar archivo BibTeX: {e}")
        return False

def process_json_to_bibtex(json_file_path, output_bibtex_path=None):
    """
    Función principal para convertir JSON (MongoDB) a BibTeX
    """
    print(f"🔄 Convirtiendo JSON a BibTeX: {json_file_path}")
    
    # Verificar que el archivo existe
    if not os.path.exists(json_file_path):
        print(f"❌ Archivo JSON no encontrado: {json_file_path}")
        return False
    
    try:
        # Cargar artículos desde JSON
        articles = load_json_articles(json_file_path)
        
        if not articles:
            print("❌ No se encontraron artículos en el archivo JSON")
            return False
        
        # Generar nombre de archivo de salida si no se proporciona
        if not output_bibtex_path:
            base_name = os.path.splitext(os.path.basename(json_file_path))[0]
            # Remover sufijo "_mongodb" si existe
            if base_name.endswith('_mongodb'):
                base_name = base_name[:-9]
            output_bibtex_path = f"{os.path.dirname(json_file_path)}/{base_name}_from_mongodb.bib"
        
        # Guardar como BibTeX
        success = save_to_bibtex(articles, output_bibtex_path)
        
        if success:
            # Mostrar preview de primera entrada
            print(f"\n🔍 PREVIEW DE LA PRIMERA ENTRADA BIBTEX:")
            print("-" * 50)
            try:
                with open(output_bibtex_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Mostrar hasta la primera entrada completa
                    entry_lines = []
                    brace_count = 0
                    started = False
                    
                    for line in lines:
                        if line.strip().startswith('@'):
                            started = True
                        if started:
                            entry_lines.append(line)
                            brace_count += line.count('{') - line.count('}')
                            if brace_count == 0 and started:
                                break
                    
                    print(''.join(entry_lines))
            except:
                print("No se pudo mostrar el preview")
        
        return success
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return False


        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return False

if __name__ == "__main__":
    # Usar el archivo JSON que se acaba de crear
    json_file = "/home/santiago/Proyectos/revisiones-sistematicas/parse-data/data/data_mongodb.json"
    success_json_to_bib = process_json_to_bibtex(json_file)
        
    if success_json_to_bib:
        print("\n✅ ¡Conversiones completadas exitosamente!")
    else:
        print("\n⚠️ Conversión BibTeX->JSON exitosa, pero JSON->BibTeX falló")
