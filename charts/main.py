
import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import numpy as np
# from wordcloud import WordCloud
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots

# Configuración de estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AcademicTrendsAnalyzer:
    def __init__(self, connection_string, database_name, collection_name):
        """
        Inicializar conexión a MongoDB
        """
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
        self.df = None


    def load_data(self):
        """
        Cargar datos desde MongoDB a DataFrame
        """
        try:
            cursor = self.collection.find({})
            data = list(cursor)
            self.df = pd.DataFrame(data)
            
            # Limpiar y preparar los datos
            if 'labels' in self.df.columns:
                # Expandir labels para análisis
                self.df['label_count'] = self.df['labels'].apply(len)
                
            print(f"Datos cargados exitosamente: {len(self.df)} registros")
            print(f"Columnas disponibles: {list(self.df.columns)}")
            return self.df
        
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            return None
    
    def analyze_label_trends(self):
        """
        Analizar tendencias en los labels
        """
        if self.df is None:
            print("Primero debe cargar los datos")
            return
        
        # Extraer todos los labels
        all_labels = []
        for labels in self.df['labels']:
            if isinstance(labels, list):
                all_labels.extend(labels)
        
        # Contar frecuencias
        label_counts = Counter(all_labels)
        
        # Crear DataFrame para análisis
        trends_df = pd.DataFrame([
            {'label': label, 'count': count} 
            for label, count in label_counts.items()
        ]).sort_values('count', ascending=False)
        
        return trends_df, label_counts
    
    def generate_summary_report(self):
        """
        Generar reporte resumen de tendencias
        """
        trends_df, label_counts = self.analyze_label_trends()
        
        print("=== REPORTE DE TENDENCIAS EN INVESTIGACIÓN ACADÉMICA ===\n")
        
        print(f"📊 Total de artículos analizados: {len(self.df)}")
        
        print(f"\n🔝 CONTEO DE ETIQUETAS POR ARTICULO")
        for i, (label, count) in enumerate(trends_df.values, 1):
            percentage = (count / len(self.df)) * 100
            print(f"{i:2d}. {label:<30} | {count:3d} artículos ({percentage:.1f}%)")
        
        # Análisis por categorías
        categories = {
            'Técnicas de ML': ['Machine Learning', 'Deep Learning'],
            'Imágenes Médicas': ['Mamografia', 'Ultrasonido', 'PET', 'Imagenes Histopatologicas', 'MRI'],
        }
        
        print(f"\n📋 ANÁLISIS POR CATEGORÍAS:")
        for category, keywords in categories.items():
            category_count = sum(label_counts.get(keyword, 0) for keyword in keywords)
            if category_count > 0:
                print(f"   {category}: {category_count} menciones")
    
    def create_visualizations(self, output_dir='visualizations'):
        """
        Crear todas las visualizaciones
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        # self.create_treatment_response_pie_chart(output_dir)
        # self.create_medical_imaging_fig(output_dir)
        # self.create_modality_vs_clinical_bars(output_dir)
        # self.create_db_source_bars(output_dir)
        # self.create_technique_and_radiomics_fig(output_dir)
        # self.create_technique_and_radiomics_fig_with_included_papers(output_dir)
        self.create_trend_bars_modalities_and_techniques(output_dir)

    def create_treatment_response_pie_chart(self, output_dir):
        """
        Crear gráfico de torta con dos análisis:
        1. Total de artículos que predicen/no predicen respuesta al tratamiento.
        2. Distribución de pCR / no pCR dentro de los artículos que predicen respuesta.
        """
        # --- Contadores ---
        predicts_count = 0
        no_predicts_count = 0
        pcr_count = 0
        no_pcr_count = 0

        for idx, row in self.df.iterrows():
            labels = row.get('labels', [])
            if isinstance(labels, list):
                if 'Predice respuesta al tratamiento' in labels:
                    predicts_count += 1
                    # Dentro de los que predicen, mirar pCR vs no pCR
                    if 'pCR' in labels:
                        pcr_count += 1
                    elif 'No pCR' in labels:
                        no_pcr_count += 1
                elif 'No predice respuesta al tratamiento' in labels:
                    no_predicts_count += 1
                else:
                    no_predicts_count += 1

        total_articles = predicts_count + no_predicts_count
        total_predicts = pcr_count + no_pcr_count

        # --- Crear figura con dos subplots ---
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))

        # ======= Primera gráfica: predicen vs no predicen =======
        colors1 = ['#4CAF50', '#FF7043']  # Verde y naranja
        labels1 = ['Predice Respuesta\nal Tratamiento', 'No Predice Respuesta\nal Tratamiento']
        sizes1 = [predicts_count, no_predicts_count]

        wedges1, texts1, autotexts1 = axes[0].pie(
            sizes1,
            labels=labels1,
            autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*total_articles)} artículos)',
            colors=colors1,
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )

        for autotext in autotexts1:
            autotext.set_color('white')
            autotext.set_fontsize(11)

        for text in texts1:
            text.set_fontsize(10)
            text.set_fontweight('bold')
            text.set_color('#2C3E50')

        axes[0].axis('equal')

        # ======= Segunda gráfica: pCR vs no pCR (solo predicen) =======
        colors2 = ['#3498DB', '#E67E22']  # Azul y naranja fuerte
        labels2 = ['pCR', 'No pCR']
        sizes2 = [pcr_count, no_pcr_count]

        if total_predicts > 0:
            wedges2, texts2, autotexts2 = axes[1].pie(
                sizes2,
                labels=labels2,
                autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*total_predicts)} artículos)',
                colors=colors2,
                textprops={'fontsize': 12, 'fontweight': 'bold'}
            )

            for autotext in autotexts2:
                autotext.set_color('white')
                autotext.set_fontsize(11)

            for text in texts2:
                text.set_fontsize(10)
                text.set_fontweight('bold')
                text.set_color('#2C3E50')

            axes[1].axis('equal')
        else:
            axes[1].text(0.5, 0.5, 'No hay artículos con pCR/No pCR',
                        ha='center', va='center', fontsize=12, color='gray')
            axes[1].axis('off')

        # --- Ajustar y guardar ---
        plt.tight_layout()
        plt.savefig(f'{output_dir}/treatment_response_double_pie.png',
                    dpi=300, bbox_inches='tight', transparent=True)
        plt.show()

        # --- Imprimir resumen ---
        print("\n🎯 ANÁLISIS DE PREDICCIÓN DE RESPUESTA AL TRATAMIENTO:")
        print("=" * 70)
        print(f"📊 Total de artículos analizados: {total_articles}")
        print(f"✅ Predicen respuesta al tratamiento: {predicts_count} artículos")
        print(f"❌ No predicen respuesta al tratamiento: {no_predicts_count} artículos")
        print(f"🔎 Dentro de los que predicen ({predicts_count}):")
        print(f"   - pCR: {pcr_count} artículos")
        print(f"   - No pCR: {no_pcr_count} artículos")
        print("=" * 70)

        return {
            'predicts_count': predicts_count,
            'no_predicts_count': no_predicts_count,
            'total_articles': total_articles,
            'pcr_count': pcr_count,
            'no_pcr_count': no_pcr_count
        }

    def create_medical_imaging_fig(self, output_dir):
        """
        Crea una figura con dos gráficas:
        1) Pie: Artículos que usan imágenes médicas vs no usan.
        - Si un artículo no tiene ninguna de las etiquetas ['Imagenes medicas', 'No imagenes medicas'],
            se clasifica como 'No imagenes medicas'.
        2) Barras: Dentro de los que usan imágenes médicas, conteo por tipo
        [Mamografia, Ultrasonido, PET, Imagenes Histopatologicas, MRI].

        Nota: Si un artículo tiene múltiples modalidades, se contabiliza en cada una (conteo multilabel).
        """
        import matplotlib.pyplot as plt
        from collections import Counter

        # --- Configuración de etiquetas esperadas ---
        TAG_IMGS_YES = 'Imagenes medicas'
        TAG_IMGS_NO  = 'No imagenes medicas'
        MODALITIES = ['Mamografia', 'Ultrasonido', 'PET', 'Imagenes Histopatologicas', 'MRI']
        TAG_RESPONSE_TREATMENT = 'Predice respuesta al tratamiento'

        # --- Contadores globales ---
        uses_images_count = 0
        no_images_count = 0
        predicts_count = 0

        # --- Contador por modalidad (solo para artículos con 'Imagenes medicas') ---
        modality_counter = Counter()

        # --- Recorrer DataFrame ---
        for _, row in self.df.iterrows():
            labels = row.get('labels', [])
            labels = labels if isinstance(labels, list) else []

            if TAG_RESPONSE_TREATMENT in labels:
                predicts_count += 1
                if TAG_IMGS_YES in labels:
                    uses_images_count += 1

                    # Contabilizar modalidades si están presentes
                    for mod in MODALITIES:
                        if mod in labels:
                            modality_counter[mod] += 1

                elif TAG_IMGS_NO in labels:
                    no_images_count += 1

                else:
                    # Si no tiene ninguna de las dos etiquetas, lo contamos como No imágenes médicas
                    no_images_count += 1

        total_articles = predicts_count

        # --- Preparar datos para las gráficas ---
        # Pie (izq)
        pie_labels = ['Imagenes médicas', 'No imágenes médicas']
        pie_sizes = [uses_images_count, no_images_count]
        pie_colors = ['#2ECC71', '#E67E22']  # verde, naranja

        # Barras (der)
        bar_labels = MODALITIES
        bar_values = [modality_counter.get(m, 0) for m in MODALITIES]

        # --- Crear figura con dos subplots ---
        fig, axes = plt.subplots(1, 2, figsize=(18, 8))

        # ======= Pie: usa imágenes vs no =======
        total = total_articles if total_articles > 0 else 1  # evitar div/0 en el autopct
        wedges, texts, autotexts = axes[0].pie(
            pie_sizes,
            labels=pie_labels,
            autopct=lambda pct: f'{pct:.1f}%\n({int(round(pct/100*total))})',
            colors=pie_colors,
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )
        for autot in autotexts:
            autot.set_color('white')
            autot.set_fontsize(11)
            autot.set_fontweight('bold')
        for t in texts:
            t.set_color('#2C3E50')
            t.set_fontsize(11)
            t.set_fontweight('bold')
        # axes[0].set_title('Uso de imágenes médicas', fontsize=14, fontweight='bold', color='#2C3E50', pad=14)
        axes[0].axis('equal')

        # ======= Barras: modalidades dentro de los que usan imágenes =======
        ax = axes[1]
        bars = ax.bar(bar_labels, bar_values)
        # ax.set_title('Modalidades en artículos con imágenes médicas', fontsize=14, fontweight='bold', color='#2C3E50', pad=14)
        ax.set_ylabel('Número de artículos', fontsize=12)
        ax.set_xlabel('Modalidad', fontsize=12)
        ax.tick_params(axis='x', labelrotation=20)
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        # Añadir etiquetas de valor encima de cada barra
        for rect in bars:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2.0, height + max(0.03*max(bar_values or [1]), 0.5),
                    f'{int(height)}', ha='center', va='bottom', fontsize=11, fontweight='bold', color='#2C3E50')

        # Si no hay artículos con imágenes, mostrar aviso en el subplot de barras
        if uses_images_count == 0:
            ax.text(0.5, 0.5, 'No hay artículos con "Imagenes medicas"', ha='center', va='center',
                    transform=ax.transAxes, fontsize=12, color='gray')
            ax.set_ylim(0, 1)

        # --- Ajuste y guardado (fondo transparente) ---
        plt.tight_layout()
        plt.savefig(f'{output_dir}/medical_imaging_double_plot.png',
                    dpi=300, bbox_inches='tight', transparent=True)
        plt.show()

        # --- Resumen en consola ---
        print("\n🩻 ANÁLISIS DE IMÁGENES MÉDICAS")
        print("=" * 70)
        print(f"📊 Total de artículos analizados: {total_articles}")
        print(f"🟢 Con imágenes médicas: {uses_images_count}")
        print(f"🟠 Sin imágenes médicas: {no_images_count}")
        print("🔎 Modalidades (solo en artículos con imágenes):")
        for m in MODALITIES:
            print(f"   - {m}: {modality_counter.get(m, 0)}")
        print("=" * 70)

        return {
            'total_articles': total_articles,
            'uses_images_count': uses_images_count,
            'no_images_count': no_images_count,
            'modalities_count': {m: modality_counter.get(m, 0) for m in MODALITIES}
        }

    def create_modality_vs_clinical_bars(self, output_dir):
        """
        Grafica barras agrupadas por modalidad de imagen:
        Para artículos que cumplen:
        - 'Predice respuesta al tratamiento'  y
        - 'Imagenes medicas'
        Se contabiliza por modalidad [Mamografia, Ultrasonido, PET, Imagenes Histopatologicas, MRI]
        y dentro de cada modalidad se separa en:
        - 'Datos clinicos'
        - 'No datos clinicos'  (si no aparece ninguna de las dos, se clasifica como 'No datos clinicos').

        Guarda la figura en PNG con fondo transparente y también la muestra.
        """
        import matplotlib.pyplot as plt
        import numpy as np
        from collections import defaultdict

        # --- Configuración de etiquetas ---
        TAG_PREDICTS   = 'Predice respuesta al tratamiento'
        TAG_IMGS_YES   = 'Imagenes medicas'
        TAG_CLINICAL   = 'Datos clinicos'
        TAG_NOCLINICAL = 'No datos clinicos'
        MODALITIES = ['Mamografia', 'Ultrasonido', 'PET', 'Imagenes Histopatologicas', 'MRI']

        # --- Estructura: por modalidad -> {'clinical': x, 'non_clinical': y} ---
        counts = defaultdict(lambda: {'clinical': 0, 'non_clinical': 0})

        # --- Recorrer DataFrame ---
        for _, row in self.df.iterrows():
            labels = row.get('labels', [])
            if not isinstance(labels, list):
                continue

            # Filtro: solo artículos que predicen y usan imágenes médicas
            if (TAG_PREDICTS in labels) and (TAG_IMGS_YES in labels):
                # Clasificación clínica:
                has_clinical = (TAG_CLINICAL in labels)
                has_nonclinical = (TAG_NOCLINICAL in labels)

                # Si no tiene ninguna de las dos, por defecto 'No datos clinicos'
                clinical_key = 'clinical' if has_clinical else 'non_clinical'

                # Sumar en TODAS las modalidades que aparezcan en el artículo
                # (multietiqueta: un artículo puede aportar a varias modalidades)
                at_least_one_mod = False
                for mod in MODALITIES:
                    if mod in labels:
                        counts[mod][clinical_key] += 1
                        at_least_one_mod = True

                # Si marca 'Imagenes medicas' pero no especifica modalidad,
                # no se suma en ninguna barra (no hay modalidad para clasificar).

        # --- Preparar datos para graficar ---
        bar_labels = MODALITIES
        clinical_vals    = [counts[m]['clinical']      for m in MODALITIES]
        non_clinical_vals= [counts[m]['non_clinical']  for m in MODALITIES]

        # --- Configurar gráfico de barras agrupadas ---
        x = np.arange(len(bar_labels))
        width = 0.4

        fig, ax = plt.subplots(figsize=(16, 8))

        # Colores consistentes y profesionales
        # (clínicos más oscuros, no clínicos más suaves)
        bars1 = ax.bar(x - width/2, clinical_vals, width, label='Datos clínicos', color='#34495E')
        bars2 = ax.bar(x + width/2, non_clinical_vals, width, label='No datos clínicos', color='#95A5A6')

        # Títulos y ejes
        # ax.set_title('Artículos que Predicen + Usan Imágenes: Clínica vs No Clínica por Modalidad',
        #             fontsize=14, fontweight='bold', color='#2C3E50', pad=14)
        ax.set_xlabel('Modalidad de Imagen', fontsize=12)
        ax.set_ylabel('Número de artículos', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(bar_labels, rotation=15)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.legend(fontsize=11)

        # Etiquetas de valor encima de cada barra
        max_val = max(clinical_vals + non_clinical_vals + [0])
        bump = max(0.03*max_val, 0.5)
        for rect in list(bars1) + list(bars2):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2.0,
                    height + bump,
                    f'{int(height)}',
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color='#2C3E50')

        # Si no hay datos, mostrar aviso
        if max_val == 0:
            ax.text(0.5, 0.5,
                    'No hay artículos que cumplan:\n"Predice respuesta" y "Imagenes medicas"',
                    transform=ax.transAxes, ha='center', va='center', fontsize=12, color='gray')

        # --- Ajuste y guardado con fondo transparente ---
        plt.tight_layout()
        plt.savefig(f'{output_dir}/modality_clinical_bars.png',
                    dpi=300, bbox_inches='tight', transparent=True)
        plt.show()

        # --- Resumen en consola ---
        total_clinical = sum(clinical_vals)
        total_nonclinical = sum(non_clinical_vals)
        print("\n🧪 PREDICCIÓN + IMÁGENES: CLÍNICA VS NO CLÍNICA POR MODALIDAD")
        print("=" * 78)
        for m in MODALITIES:
            print(f" - {m:<24} | Datos clínicos: {counts[m]['clinical']:>3} | No datos clínicos: {counts[m]['non_clinical']:>3}")
        print("-" * 78)
        print(f"Total (todas modalidades)  | Datos clínicos: {total_clinical} | No datos clínicos: {total_nonclinical}")
        print("=" * 78)

        return {
            'by_modality': {m: dict(counts[m]) for m in MODALITIES},
            'totals': {
                'clinical': total_clinical,
                'non_clinical': total_nonclinical
            }
        }

    def create_db_source_bars(self, output_dir):
        """
        Grafica barras por fuente de datos para artículos que cumplen:
        - 'Predice respuesta al tratamiento'  y
        - 'Imagenes medicas'

        Categorías:
        - 'Bases de datos publica'
        - 'Base de datos privada'
        - 'No especifica base de datos' (si no marca ninguna de las dos anteriores
            o si explícitamente aparece esta etiqueta)

        Nota: si un artículo marca tanto pública como privada, se suma en ambas (conteo multilabel).
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # --- Etiquetas base ---
        TAG_PREDICTS      = 'Predice respuesta al tratamiento'
        TAG_IMGS_YES      = 'Imagenes medicas'
        TAG_DB_PUBLIC     = 'Bases de datos publica'
        TAG_DB_PRIVATE    = 'Base de datos privada'
        TAG_DB_UNSPEC     = 'No especifica base de datos'

        categories = [TAG_DB_PUBLIC, TAG_DB_PRIVATE, TAG_DB_UNSPEC]
        counts = {cat: 0 for cat in categories}

        # --- Recorrer DataFrame ---
        for _, row in self.df.iterrows():
            labels = row.get('labels', [])
            if not isinstance(labels, list):
                continue

            # Filtro: solo artículos que predicen y usan imágenes médicas
            if (TAG_PREDICTS in labels) and (TAG_IMGS_YES in labels):
                has_public  = TAG_DB_PUBLIC  in labels
                has_private = TAG_DB_PRIVATE in labels
                has_unspec  = TAG_DB_UNSPEC  in labels

                # Conteo multilabel para pública/privada si están presentes
                if has_public:
                    counts[TAG_DB_PUBLIC] += 1
                if has_private:
                    counts[TAG_DB_PRIVATE] += 1

                # Si no se indicó pública ni privada, contar como 'No especifica'
                # (o si explícitamente viene esa etiqueta)
                if (not has_public and not has_private) or has_unspec:
                    counts[TAG_DB_UNSPEC] += 1

        # --- Datos para graficar ---
        bar_labels = ['Bases públicas', 'Bases privadas', 'No especifica']
        bar_map = {
            'Bases públicas': TAG_DB_PUBLIC,
            'Bases privadas': TAG_DB_PRIVATE,
            'No especifica': TAG_DB_UNSPEC
        }
        bar_values = [counts[bar_map[k]] for k in bar_labels]

        # --- Construir gráfico ---
        x = np.arange(len(bar_labels))
        fig, ax = plt.subplots(figsize=(14, 8))

        # Colores sobrios y consistentes
        bars = ax.bar(x, bar_values, width=0.55, color=['#2ECC71', '#3498DB', '#95A5A6'])

        # Títulos y ejes
        # ax.set_title('Fuente de datos en artículos que Predicen + Usan Imágenes',
        #             fontsize=14, fontweight='bold', color='#2C3E50', pad=14)
        ax.set_xlabel('Fuente de datos', fontsize=12)
        ax.set_ylabel('Número de artículos', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(bar_labels, rotation=10)
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        # Etiquetas de valor encima de cada barra
        max_val = max(bar_values + [0])
        bump = max(0.03 * max_val, 0.5)
        for rect in bars:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2.0,
                    height + bump,
                    f'{int(height)}',
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color='#2C3E50')

        # Mensaje si no hay datos
        if max_val == 0:
            ax.text(0.5, 0.5,
                    'No hay artículos que cumplan:\n"Predice respuesta" y "Imagenes medicas"',
                    transform=ax.transAxes, ha='center', va='center', fontsize=12, color='gray')

        # --- Guardar (fondo transparente) y mostrar ---
        plt.tight_layout()
        plt.savefig(f'{output_dir}/db_source_bars.png',
                    dpi=300, bbox_inches='tight', transparent=True)
        plt.show()

        # --- Resumen en consola ---
        total_counted = sum(bar_values)  # puede superar #artículos únicos por multilabel
        print("\n🗂️ FUENTE DE DATOS (Predicen + Imágenes)")
        print("=" * 70)
        for label in bar_labels:
            print(f" - {label:<15}: {counts[bar_map[label]]}")
        print("-" * 70)
        print(f"Total conteos (multilabel): {total_counted}")
        print("=" * 70)

        return {
            'counts': counts,
            'total_multilabel_counts': total_counted
        }

    def create_technique_and_radiomics_fig(self, output_dir):
        """
        Crea una figura con dos gráficas:
        1) Barras: Conteo de artículos (que tienen 'Predice respuesta al tratamiento' y 'Imagenes medicas')
            clasificados por técnica: [Machine Learning, Deep Learning].
        2) Barras agrupadas: Para cada técnica [ML, DL], conteo de [Radiomics, No Radiomics].

        Reglas:
        - Un artículo puede contar en ambas técnicas si marca ML y DL (multilabel).
        - Si no marca ni 'Radiomics' ni 'No Radiomics', se clasifica como 'No Radiomics' por defecto.

        La figura se muestra y se guarda con fondo transparente.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # --- Etiquetas ---
        TAG_PREDICTS  = 'Predice respuesta al tratamiento'
        TAG_IMGS_YES  = 'Imagenes medicas'
        TAG_ML        = 'Machine Learning'
        TAG_DL        = 'Deep Learning'
        TAG_RAD       = 'Radiomics'
        TAG_NORAD     = 'No Radiomics'

        # --- Contadores ---
        ml_count = 0
        dl_count = 0

        # Para la gráfica agrupada por técnica
        ml_radiomics = 0
        ml_no_radiomics = 0
        dl_radiomics = 0
        dl_no_radiomics = 0

        # --- Recorrer DataFrame ---
        for _, row in self.df.iterrows():
            labels = row.get('labels', [])
            if not isinstance(labels, list):
                continue

            # Filtro: solo artículos que predicen y usan imágenes
            if (TAG_PREDICTS in labels) and (TAG_IMGS_YES in labels):
                has_ml = TAG_ML in labels
                has_dl = TAG_DL in labels

                # Conteo por técnica (multilabel permitido)
                if has_ml:
                    ml_count += 1
                if has_dl:
                    dl_count += 1

                # Clasificación Radiomics / No Radiomics (por defecto No Radiomics)
                is_radiomics = TAG_RAD in labels
                is_norad = TAG_NORAD in labels
                rad_key = 'rad' if is_radiomics else 'norad'  # si no está ninguna, norad

                # Sumar por técnica
                if has_ml:
                    if rad_key == 'rad':
                        ml_radiomics += 1
                    else:
                        ml_no_radiomics += 1
                if has_dl:
                    if rad_key == 'rad':
                        dl_radiomics += 1
                    else:
                        dl_no_radiomics += 1

        # --- Datos para gráfica 1 (barras ML vs DL) ---
        left_labels = ['Machine Learning', 'Deep Learning']
        left_values = [ml_count, dl_count]

        # --- Datos para gráfica 2 (agrupadas por técnica) ---
        right_groups = ['Machine Learning', 'Deep Learning']
        right_radiomics = [ml_radiomics, dl_radiomics]
        right_no_radiomics = [ml_no_radiomics, dl_no_radiomics]

        # --- Construcción de la figura ---
        fig, axes = plt.subplots(1, 2, figsize=(18, 8))

        # ======= Gráfica izquierda: ML vs DL =======
        ax1 = axes[0]
        x1 = np.arange(len(left_labels))
        bars1 = ax1.bar(x1, left_values, width=0.55, color=['#3498DB', '#E67E22'])
        # ax1.set_title('Técnica (Predicen + Imágenes Médicas)', fontsize=14, fontweight='bold', color='#2C3E50', pad=14)
        ax1.set_xlabel('Técnica', fontsize=12)
        ax1.set_ylabel('Número de artículos', fontsize=12)
        ax1.set_xticks(x1)
        ax1.set_xticklabels(left_labels, rotation=10)
        ax1.grid(axis='y', linestyle='--', alpha=0.3)

        max_left = max(left_values + [0])
        bump_left = max(0.03 * max_left, 0.5)
        for rect in bars1:
            h = rect.get_height()
            ax1.text(rect.get_x() + rect.get_width()/2.0,
                    h + bump_left,
                    f'{int(h)}',
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color='#2C3E50')

        if max_left == 0:
            ax1.text(0.5, 0.5,
                    'No hay artículos que cumplan:\n"Predice respuesta" y "Imagenes medicas"',
                    transform=ax1.transAxes, ha='center', va='center', fontsize=12, color='gray')

        # ======= Gráfica derecha: Radiomics vs No Radiomics por técnica =======
        ax2 = axes[1]
        x2 = np.arange(len(right_groups))
        width = 0.4

        bars_rad = ax2.bar(x2 - width/2, right_radiomics, width, label='Radiomics', color='#2ECC71')
        bars_norad = ax2.bar(x2 + width/2, right_no_radiomics, width, label='No Radiomics', color='#95A5A6')

        # ax2.set_title('Radiomics por Técnica (Predicen + Imágenes Médicas)', fontsize=14, fontweight='bold', color='#2C3E50', pad=14)
        ax2.set_xlabel('Técnica', fontsize=12)
        ax2.set_ylabel('Número de artículos', fontsize=12)
        ax2.set_xticks(x2)
        ax2.set_xticklabels(right_groups, rotation=10)
        ax2.grid(axis='y', linestyle='--', alpha=0.3)
        ax2.legend(fontsize=11)

        max_right = max(right_radiomics + right_no_radiomics + [0])
        bump_right = max(0.03 * max_right, 0.5)
        for rect in list(bars_rad) + list(bars_norad):
            h = rect.get_height()
            ax2.text(rect.get_x() + rect.get_width()/2.0,
                    h + bump_right,
                    f'{int(h)}',
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color='#2C3E50')

        if max_right == 0:
            ax2.text(0.5, 0.5,
                    'Sin datos para Radiomics / No Radiomics\nen artículos filtrados',
                    transform=ax2.transAxes, ha='center', va='center', fontsize=12, color='gray')

        # --- Guardar y mostrar (fondo transparente) ---
        plt.tight_layout()
        plt.savefig(f'{output_dir}/technique_and_radiomics_double_plot.png',
                    dpi=300, bbox_inches='tight', transparent=True)
        plt.show()

        # --- Resumen en consola ---
        print("\n🤖 TÉCNICA Y RADIOMICS (Predicen + Imágenes Médicas)")
        print("=" * 78)
        print(f"Machine Learning: {ml_count}")
        print(f"Deep Learning   : {dl_count}")
        print("-" * 78)
        print("Radiomics por técnica:")
        print(f" - ML -> Radiomics: {ml_radiomics:>3} | No Radiomics: {ml_no_radiomics:>3}")
        print(f" - DL -> Radiomics: {dl_radiomics:>3} | No Radiomics: {dl_no_radiomics:>3}")
        print("=" * 78)

        return {
            'technique_counts': {
                'Machine Learning': ml_count,
                'Deep Learning': dl_count
            },
            'radiomics_by_technique': {
                'Machine Learning': {'Radiomics': ml_radiomics, 'No Radiomics': ml_no_radiomics},
                'Deep Learning': {'Radiomics': dl_radiomics, 'No Radiomics': dl_no_radiomics}
            }
        }

    def create_technique_and_radiomics_fig_with_included_papers(self, output_dir):
        """
        Crea una figura con dos gráficas:
        1) Barras: Conteo de artículos (que tienen 'Predice respuesta al tratamiento' y 'Imagenes medicas')
            clasificados por técnica: [Machine Learning, Deep Learning].
        2) Barras agrupadas: Para cada técnica [ML, DL], conteo de [Radiomics, No Radiomics].

        Solo se incluyen los artículos con screening_status == 'included'.
        """

        import matplotlib.pyplot as plt
        import numpy as np

        # --- Etiquetas ---
        TAG_PREDICTS  = 'Predice respuesta al tratamiento'
        TAG_IMGS_YES  = 'Imagenes medicas'
        TAG_ML        = 'Machine Learning'
        TAG_DL        = 'Deep Learning'
        TAG_RAD       = 'Radiomics'
        TAG_NORAD     = 'No Radiomics'

        # --- Filtrar artículos "included" ---
        df_included = self.df[self.df['screening_status'].str.lower() == 'included']

        # --- Contadores ---
        ml_count = 0
        dl_count = 0

        ml_radiomics = 0
        ml_no_radiomics = 0
        dl_radiomics = 0
        dl_no_radiomics = 0

        # --- Recorrer DataFrame filtrado ---
        for _, row in df_included.iterrows():
            labels = row.get('labels', [])
            if not isinstance(labels, list):
                continue

            # Filtro: solo artículos que predicen y usan imágenes
            if (TAG_PREDICTS in labels) and (TAG_IMGS_YES in labels):
                has_ml = TAG_ML in labels
                has_dl = TAG_DL in labels

                # Conteo por técnica
                if has_ml:
                    ml_count += 1
                if has_dl:
                    dl_count += 1

                # Clasificación Radiomics / No Radiomics (por defecto No Radiomics)
                is_radiomics = TAG_RAD in labels
                is_norad = TAG_NORAD in labels
                rad_key = 'rad' if is_radiomics else 'norad'

                if has_ml:
                    if rad_key == 'rad':
                        ml_radiomics += 1
                    else:
                        ml_no_radiomics += 1
                if has_dl:
                    if rad_key == 'rad':
                        dl_radiomics += 1
                    else:
                        dl_no_radiomics += 1

        # --- Datos para gráfica 1 (ML vs DL) ---
        left_labels = ['Machine Learning', 'Deep Learning']
        left_values = [ml_count, dl_count]

        # --- Datos para gráfica 2 (Radiomics vs No Radiomics) ---
        right_groups = ['Machine Learning', 'Deep Learning']
        right_radiomics = [ml_radiomics, dl_radiomics]
        right_no_radiomics = [ml_no_radiomics, dl_no_radiomics]

        # --- Crear figura con dos subplots ---
        fig, axes = plt.subplots(1, 2, figsize=(18, 8))

        # ======= Gráfica izquierda: ML vs DL =======
        ax1 = axes[0]
        x1 = np.arange(len(left_labels))
        bars1 = ax1.bar(x1, left_values, width=0.55, color=['#3498DB', '#E67E22'])
        # ax1.set_title('Técnica (Predicen + Imágenes Médicas)', fontsize=14, fontweight='bold', color='#2C3E50', pad=14)
        ax1.set_xlabel('Técnica', fontsize=12)
        ax1.set_ylabel('Número de artículos', fontsize=12)
        ax1.set_xticks(x1)
        ax1.set_xticklabels(left_labels, rotation=10)
        ax1.grid(axis='y', linestyle='--', alpha=0.3)

        max_left = max(left_values + [0])
        bump_left = max(0.03 * max_left, 0.5)
        for rect in bars1:
            h = rect.get_height()
            ax1.text(rect.get_x() + rect.get_width()/2.0,
                    h + bump_left,
                    f'{int(h)}',
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color='#2C3E50')

        if max_left == 0:
            ax1.text(0.5, 0.5,
                    'No hay artículos que cumplan:\n"Predice respuesta" y "Imagenes medicas"',
                    transform=ax1.transAxes, ha='center', va='center', fontsize=12, color='gray')

        # ======= Gráfica derecha: Radiomics por técnica =======
        ax2 = axes[1]
        x2 = np.arange(len(right_groups))
        width = 0.4

        bars_rad = ax2.bar(x2 - width/2, right_radiomics, width, label='Radiomics', color='#2ECC71')
        bars_norad = ax2.bar(x2 + width/2, right_no_radiomics, width, label='No Radiomics', color='#95A5A6')

        # ax2.set_title('Radiomics por Técnica (Predicen + Imágenes Médicas)', fontsize=14, fontweight='bold', color='#2C3E50', pad=14)
        ax2.set_xlabel('Técnica', fontsize=12)
        ax2.set_ylabel('Número de artículos', fontsize=12)
        ax2.set_xticks(x2)
        ax2.set_xticklabels(right_groups, rotation=10)
        ax2.grid(axis='y', linestyle='--', alpha=0.3)
        ax2.legend(fontsize=11)

        max_right = max(right_radiomics + right_no_radiomics + [0])
        bump_right = max(0.03 * max_right, 0.5)
        for rect in list(bars_rad) + list(bars_norad):
            h = rect.get_height()
            ax2.text(rect.get_x() + rect.get_width()/2.0,
                    h + bump_right,
                    f'{int(h)}',
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color='#2C3E50')

        if max_right == 0:
            ax2.text(0.5, 0.5,
                    'Sin datos para Radiomics / No Radiomics\nen artículos filtrados',
                    transform=ax2.transAxes, ha='center', va='center', fontsize=12, color='gray')

        # --- Guardar y mostrar ---
        plt.tight_layout()
        plt.savefig(f'{output_dir}/technique_and_radiomics_included.png',
                    dpi=300, bbox_inches='tight', transparent=True)
        plt.show()

        # --- Resumen en consola ---
        print("\n🤖 TÉCNICA Y RADIOMICS (Solo artículos 'included')")
        print("=" * 78)
        print(f"Machine Learning: {ml_count}")
        print(f"Deep Learning   : {dl_count}")
        print("-" * 78)
        print("Radiomics por técnica:")
        print(f" - ML -> Radiomics: {ml_radiomics:>3} | No Radiomics: {ml_no_radiomics:>3}")
        print(f" - DL -> Radiomics: {dl_radiomics:>3} | No Radiomics: {dl_no_radiomics:>3}")
        print("=" * 78)

        return {
            'technique_counts': {
                'Machine Learning': ml_count,
                'Deep Learning': dl_count
            },
            'radiomics_by_technique': {
                'Machine Learning': {'Radiomics': ml_radiomics, 'No Radiomics': ml_no_radiomics},
                'Deep Learning': {'Radiomics': dl_radiomics, 'No Radiomics': dl_no_radiomics}
            }
        }

    def create_trend_bars_modalities_and_techniques(self, output_dir, start_year=2020, end_year=2025):
        """
        Crea una figura con dos gráficas de barras apiladas (lado a lado):
        - Izquierda: uso de modalidades de imagen por año (start_year..end_year).
        - Derecha  : uso de técnicas (Machine Learning, Deep Learning) por año.

        Filtros:
        - screening_status == 'included'
        - 'Predice respuesta al tratamiento' en labels
        - 'Imagenes medicas' en labels

        Guardado:
        - PNG con fondo transparente en output_dir/trends_modalities_techniques.png
        """
        import matplotlib.pyplot as plt
        import numpy as np
        from collections import defaultdict


        TAG_PREDICTS  = 'Predice respuesta al tratamiento'
        TAG_IMGS_YES  = 'Imagenes medicas'
        MODALITIES = ['Mamografia', 'Ultrasonido', 'PET', 'Imagenes Histopatologicas', 'MRI']
        TAG_ML = 'Machine Learning'
        TAG_DL = 'Deep Learning'

        # --- Rango de años ---
        years = list(range(int(start_year), int(end_year) + 1))

        # --- Filtrar artículos "included" y válidos ---
        df = self.df.copy()
        # Asegurar año numérico
        df['year'] = pd.to_numeric(df.get('year', np.nan), errors='coerce')
        df = df[df['year'].isin(years)]

        # --- Inicializar contadores ---
        # Modalidades: dict[year] -> dict[mod] -> count
        modalities_by_year = {y: defaultdict(int) for y in years}
        # Técnicas: dict[year] -> {'ML': count, 'DL': count}
        techniques_by_year = {y: {'ML': 0, 'DL': 0} for y in years}

        # --- Recorrer artículos filtrados ---
        for _, row in df.iterrows():
            labels = row.get('labels', [])
            if not isinstance(labels, list):
                continue

            # Filtro principal
            if (TAG_PREDICTS in labels) and (TAG_IMGS_YES in labels):
                y = int(row['year'])

                # Modalidades (multietiqueta permitido)
                for mod in MODALITIES:
                    if mod in labels:
                        modalities_by_year[y][mod] += 1

                # Técnicas (multietiqueta permitido)
                if TAG_ML in labels:
                    techniques_by_year[y]['ML'] += 1
                if TAG_DL in labels:
                    techniques_by_year[y]['DL'] += 1

        # --- Preparar datos para gráficas ---
        # Modalidades apiladas por año
        mod_stack = {mod: np.array([modalities_by_year[y][mod] for y in years]) for mod in MODALITIES}
        # Técnicas apiladas por año
        ml_vals = np.array([techniques_by_year[y]['ML'] for y in years])
        dl_vals = np.array([techniques_by_year[y]['DL'] for y in years])

        x = np.arange(len(years))
        width = 0.15  # ancho de barra por año

        # --- Crear figura con 2 subplots ---
        fig, axes = plt.subplots(1, 2, figsize=(20, 8))

        # ===================== Izquierda: Modalidades por año =====================
        ax1 = axes[0]
        # Colores sobrios para modalidades
        modality_colors = {
            'Mamografia': '#2ECC71',                 # verde
            'Ultrasonido': '#3498DB',                # azul
            'PET': '#E67E22',                        # naranja
            'Imagenes Histopatologicas': '#9B59B6',  # púrpura
            'MRI': '#34495E'                         # gris oscuro
        }

        bottoms = np.zeros_like(x, dtype=float)
        bar_handles = []


        # Para agrupar, desplazamos cada modalidad con un offset
        num_modalities = len(MODALITIES)
        for i, mod in enumerate(MODALITIES):
            vals = mod_stack[mod]
            # offset: centra todas las barras alrededor de la posición del año
            offset = (i - num_modalities/2) * width + width/2
            ax1.bar(x + offset, vals, width, label=mod, color=modality_colors[mod])


        ax1.set_xlabel('Año', fontsize=12)
        ax1.set_ylabel('Número de artículos', fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels([str(y) for y in years])
        ax1.grid(axis='y', linestyle='--', alpha=0.3)
        ax1.legend(fontsize=10, ncol=2, frameon=False)

        # Etiquetas del total por año encima de cada barra apilada
        totals_mod = bottoms
        bump1 = max(0.03 * (totals_mod.max() if totals_mod.size else 0), 0.5)
        for xi, total in zip(x, totals_mod):
            if total > 0:
                ax1.text(xi, total + bump1, f'{int(total)}', ha='center', va='bottom',
                        fontsize=11, fontweight='bold', color='#2C3E50')

        # ===================== Derecha: Técnicas por año =====================
        ax2 = axes[1]
        # Apiladas ML + DL
        bars_ml = ax2.bar(x, ml_vals, width, label='Machine Learning', color='#3498DB')
        bars_dl = ax2.bar(x, dl_vals, width, bottom=ml_vals, label='Deep Learning', color='#E67E22')

        ax2.set_xlabel('Año', fontsize=12)
        ax2.set_ylabel('Número de artículos', fontsize=12)
        ax2.set_xticks(x)
        ax2.set_xticklabels([str(y) for y in years])
        ax2.grid(axis='y', linestyle='--', alpha=0.3)
        ax2.legend(fontsize=11, frameon=False)

        totals_tech = ml_vals + dl_vals
        bump2 = max(0.03 * (totals_tech.max() if totals_tech.size else 0), 0.5)
        for xi, total in zip(x, totals_tech):
            if total > 0:
                ax2.text(xi, total + bump2, f'{int(total)}', ha='center', va='bottom',
                        fontsize=11, fontweight='bold', color='#2C3E50')

        # Mensajes si no hay datos
        # if totals_mod.max() if len(totals_mod) else 0 == 0:
        #     ax1.text(0.5, 0.5, 'Sin datos en el rango de años', transform=ax1.transAxes,
        #             ha='center', va='center', fontsize=12, color='gray')
        # if totals_tech.max() if len(totals_tech) else 0 == 0:
        #     ax2.text(0.5, 0.5, 'Sin datos en el rango de años', transform=ax2.transAxes,
        #             ha='center', va='center', fontsize=12, color='gray')

        # --- Guardar (transparente) y mostrar ---
        plt.tight_layout()
        plt.savefig(f'{output_dir}/trends_modalities_techniques.png',
                    dpi=300, bbox_inches='tight', transparent=True)
        plt.show()

        # --- Resumen en consola (opcional) ---
        print("\n📈 TENDENCIAS 2020–2025 (solo 'included', Predicen + Imágenes)")
        print("=" * 80)
        print("Modalidades por año:")
        for y in years:
            row = {m: modalities_by_year[y][m] for m in MODALITIES}
            print(f"  {y}: {row} | total={sum(row.values())}")
        print("-" * 80)
        print("Técnicas por año:")
        for y in years:
            print(f"  {y}: ML={techniques_by_year[y]['ML']}, DL={techniques_by_year[y]['DL']}, total={techniques_by_year[y]['ML']+techniques_by_year[y]['DL']}")
        print("=" * 80)

        return {
            'years': years,
            'modalities_by_year': {y: {m: modalities_by_year[y][m] for m in MODALITIES} for y in years},
            'techniques_by_year': techniques_by_year
        }


# Función principal para ejecutar el análisis
def main():
    """
    Función principal para ejecutar el análisis completo
    """
    # CONFIGURACIÓN - Cambiar según tu setup
    CONNECTION_STRING = "mongodb+srv://root:P1CZEkZEyZmK6PfU@ecuot101.ppslhdh.mongodb.net/bibliografia-tesis?retryWrites=true&w=majority"  # Cambiar por tu string de conexión
    DATABASE_NAME = "bibliografia-tesis"                # Cambiar por tu base de datos
    COLLECTION_NAME = "paper"                  # Cambiar por tu colección
    
    # Inicializar analizador
    analyzer = AcademicTrendsAnalyzer(CONNECTION_STRING, DATABASE_NAME, COLLECTION_NAME)
    
    # Cargar datos
    print("Cargando datos desde MongoDB...")
    df = analyzer.load_data()
    
    if df is not None:
        # Generar reporte
        analyzer.generate_summary_report()
        
        # Crear visualizaciones
        print("\nGenerando visualizaciones...")
        analyzer.create_visualizations()
        
        print("✅ Análisis completado! Revisa la carpeta 'visualizations' para las gráficas.")
    
    return analyzer

# Ejecutar si se ejecuta directamente
if __name__ == "__main__":
    analyzer = main()