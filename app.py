import io
import time
import requests
import os
from flask import Flask, render_template, request, jsonify, send_file
import calculos as c
import pdf_generator as pdf_gen

# ----------------------------------------
# CONFIGURACIÓN FLASK
# ----------------------------------------
app = Flask(__name__)

# ----------------------------------------
# CONFIGURACIÓN GEMINI (IA)
# ----------------------------------------
# Buscamos la API KEY en una variable de entorno llamada GEMINI_API_KEY.
# NUNCA pongas la clave directamente en este archivo.
# En PowerShell (con el venv activo) puedes hacer, por ejemplo:

API_KEY = os.environ.get("GEMINI_API_KEY")

MODEL_NAME = "gemini-2.5-flash"
API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL_NAME}:generateContent?key={API_KEY}"
)


def call_gemini_api(payload):
    """
    Llama a la API de Gemini con reintento (backoff exponencial).
    Devuelve el texto generado o un mensaje de error legible.
    """

    # Leer SIEMPRE la API key del entorno en el momento de la llamada
    api_key = os.environ.get("GEMINI_API_KEY")
    print(">>> API KEY dentro de call_gemini_api:", api_key)

    if not api_key:
        return "Error: No se encontró la API KEY de Gemini. Configura la variable de entorno GEMINI_API_KEY."

    # Construimos la URL usando esta api_key local
    api_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{MODEL_NAME}:generateContent?key={api_key}"
    )

    max_retries = 5
    retry_delay = 1  # segundos

    for attempt in range(max_retries):
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            candidate = result.get("candidates", [{}])[0]

            if candidate and candidate.get("content") and candidate["content"].get("parts"):
                text = candidate["content"]["parts"][0].get("text")
                if text:
                    return text
                else:
                    return (
                        "El modelo de IA devolvió una respuesta vacía "
                        "o fue bloqueada por políticas de seguridad."
                    )

            return f"Error de respuesta del modelo: {result.get('error', 'Estructura inesperada')}"

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))
            else:
                print(f"Error llamando a Gemini API: {e}")
                return f"Error de conexión con la API de Gemini: {e}"
        except Exception as e:
            print(f"Error procesando la respuesta de Gemini: {e}")
            return f"Error interno al procesar la respuesta de IA: {e}"

    return "Error al contactar con el modelo de IA después de múltiples intentos."
    """
    Llama a la API de Gemini con reintento (backoff exponencial).
    Devuelve el texto generado o un mensaje de error legible.
    """

    # Leer SIEMPRE la API key del entorno en el momento de la llamada
    api_key = os.environ.get("GEMINI_API_KEY")
    print(">>> API KEY dentro de call_gemini_api:", api_key)

    if not api_key:
        return "Error: No se encontró la API KEY de Gemini. Configura la variable de entorno GEMINI_API_KEY."

    # Construimos la URL usando esta api_key local
    api_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{MODEL_NAME}:generateContent?key={api_key}"
    )

    max_retries = 5
    retry_delay = 1  # segundos

    for attempt in range(max_retries):
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            candidate = result.get("candidates", [{}])[0]

            if candidate and candidate.get("content") and candidate["content"].get("parts"):
                text = candidate["content"]["parts"][0].get("text")
                if text:
                    return text
                else:
                    return (
                        "El modelo de IA devolvió una respuesta vacía "
                        "o fue bloqueada por políticas de seguridad."
                    )

            return f"Error de respuesta del modelo: {result.get('error', 'Estructura inesperada')}"

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))
            else:
                print(f"Error llamando a Gemini API: {e}")
                return f"Error de conexión con la API de Gemini: {e}"
        except Exception as e:
            print(f"Error procesando la respuesta de Gemini: {e}")
            return f"Error interno al procesar la respuesta de IA: {e}"

    return "Error al contactar con el modelo de IA después de múltiples intentos."
# ----------------------------------------
# RUTA PRINCIPAL: FORMULARIO


@app.route("/")
def index():
    print(">>> Renderizando plantilla desde:", os.path.abspath("templates/index.html"))
    return render_template("index.html")


# ----------------------------------------
# RUTA /calcular  (cálculos técnicos)
# ----------------------------------------

@app.route("/calcular", methods=["POST"])
def calcular():
    try:
        # 1. Datos del formulario
        largo = float(request.form.get("largo_salon"))
        ancho = float(request.form.get("ancho_salon"))
        alto = float(request.form.get("alto_salon"))
        asistentes = int(request.form.get("num_asistentes"))
        relacion = request.form.get("relacion_aspecto")

        # Pantallas adicionales (todas opcionales)
        num_pantallas_aux = int(request.form.get("num_pantallas_aux", 0) or 0)
        num_pantallas_lagrimas = int(request.form.get("num_pantallas_lagrimas", 0) or 0)
        num_pantallas_cuadradas = int(request.form.get("num_pantallas_cuadradas", 0) or 0)

        # Metadatos del evento
        fecha_evento = request.form.get("fecha_evento")
        nombre_evento = request.form.get("nombre_evento")
        nombre_escenario = request.form.get("nombre_escenario")
        nombre_empresa = request.form.get("nombre_empresa")

        dimensiones_salon = {
            "largo_salon": largo,
            "ancho_salon": ancho,
            "alto_salon": alto,
            "num_asistentes": asistentes,
            "fecha_evento": fecha_evento,
            "nombre_evento": nombre_evento,
            "nombre_escenario": nombre_escenario,
            "nombre_empresa": nombre_empresa,
        }

        # 2. Ejecutar cálculos usando calculos.py
        pantalla_principal = c.sugerir_tamano_pantalla(largo, alto, relacion)
        tarima = c.sugerir_tarima(ancho, asistentes)
        sillas = c.calcular_sillas_y_corredores(largo, ancho, asistentes)
        tecnica = c.sugerir_tecnica(asistentes, relacion)

        # Pantallas adicionales (auxiliares 16:9, lágrimas 9:16, cuadradas 1:1)
        pantallas_extra = c.configurar_pantallas_adicionales(
            pantalla_principal,
            num_aux_16_9=num_pantallas_aux,
            num_lagrimas_9_16=num_pantallas_lagrimas,
            num_cuadradas_1_1=num_pantallas_cuadradas,
        )

        resultados = {
            "pantalla": pantalla_principal,
            "tarima": tarima,
            "sillas": sillas,
            "tecnica": tecnica,
            "pantallas_extra": pantallas_extra,
        }

        respuesta = {**dimensiones_salon, **resultados}
        return jsonify(respuesta)

    except ValueError:
        return (
            jsonify(
                {
                    "error": "Por favor, introduce valores numéricos válidos "
                    "en las dimensiones y asistentes."
                }
            ),
            400,
        )
    except Exception as e:
        print(f"Error interno en /calcular: {e}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


# ----------------------------------------
# RUTA /analisis_ia  (llamada a Gemini)
# ----------------------------------------

@app.route("/analisis_ia", methods=["POST"])
def analisis_ia():
    try:
        data = request.json or {}
        resultados = data.get("resultados")

        if not resultados:
            return jsonify({"error": "Datos de cálculo incompletos para el análisis de IA."}), 400

        imagenes_base64 = data.get("imagenes_base64", [])

        # -------------------------------
        # 1. Datos base del evento
        # -------------------------------
        nombre_evento = resultados.get("nombre_evento", "N/A")
        fecha_evento = resultados.get("fecha_evento", "N/A")
        nombre_empresa = resultados.get("nombre_empresa", "N/A")
        largo_salon = resultados.get("largo_salon", "N/A")
        ancho_salon = resultados.get("ancho_salon", "N/A")
        alto_salon = resultados.get("alto_salon", "N/A")
        num_asistentes = resultados.get("num_asistentes", "N/A")

        pantalla = resultados.get("pantalla", {}) or {}
        tarima = resultados.get("tarima", {}) or {}
        tecnica = resultados.get("tecnica", {}) or {}
        sillas = resultados.get("sillas", {}) or {}

        # Pantallas adicionales (auxiliares, lágrimas, cuadradas)
        pantallas_extra = resultados.get("pantallas_extra", []) or []

        pantallas_resumen = []
        for p in pantallas_extra:
            pantallas_resumen.append(
                f"{p.get('tipo', 'Pantalla')} #{p.get('indice', '')}: "
                f"{p.get('ancho_m', 'N/A')}m x {p.get('alto_m', 'N/A')}m, "
                f"pitch {p.get('pitch_mm', 'N/A')}mm, "
                f"pixel map {p.get('pixel_map', 'N/A')}, "
                f"módulos {p.get('modulos_totales', 'N/A')}"
            )
        texto_pantallas_extra = (
            "; ".join(pantallas_resumen) if pantallas_resumen else "Sin pantallas adicionales."
        )

        # -------------------------------
        # 2. Prompt de sistema
        # -------------------------------
        system_prompt = (
            "Eres un consultor experto en producción de eventos corporativos en Colombia, "
            "especializado en diseño escénico, audio, video e iluminación.\n\n"
            "Debes analizar el diseño técnico que se te entrega y responder en ESPAÑOL con el siguiente formato:\n\n"
            "1. Diagnóstico del espacio y disposición (dimensiones, tarima, pasillos, distancia de la primera fila, etc.).\n"
            "2. Pantallas y visibilidad (principal, auxiliares 16:9, lágrimas 9:16, pantallas 1:1; tamaños, pitch, pixel map, módulos LED y visibilidad).\n"
            "3. Sonido e iluminación (tipo de sistema recomendado, cobertura, riesgos y sugerencias).\n"
            "4. Recomendaciones para la experiencia del asistente (flujo de público, confort, legibilidad, recomendaciones extra).\n\n"
            "Al final agrega una sección titulada 'Lista de Requerimientos Técnicos' "
            "con una lista numerada (1., 2., 3., ...) que incluya todos los elementos técnicos clave: "
            "pantallas, estructura, audio, iluminación, control, microfonía, distancias y alturas relevantes."
        )

        # -------------------------------
        # 3. Texto con los datos del diseño
        # -------------------------------
        query_text = (
            f"Analiza el siguiente diseño técnico de evento en Colombia para el evento '{nombre_evento}' ({fecha_evento}) "
            f"de la empresa '{nombre_empresa}'.\n\n"
            f"Dimensiones del salón: {largo_salon}m (Largo) x {ancho_salon}m (Ancho) x {alto_salon}m (Alto).\n"
            f"Asistentes previstos: {num_asistentes}.\n\n"
            f"Pantalla principal: {pantalla.get('ancho_pantalla_w', 'N/A')}m de ancho x "
            f"{pantalla.get('altura_pantalla_h', 'N/A')}m de alto "
            f"({pantalla.get('relacion', 'N/A')}), pitch {pantalla.get('pitch_mm', 'N/A')}mm, "
            f"pixel map {pantalla.get('pixel_map', 'N/A')}, módulos LED totales "
            f"{pantalla.get('modulos_totales', 'N/A')}.\n\n"
            f"Pantallas adicionales: {texto_pantallas_extra}.\n\n"
            f"Tarima: {tarima.get('ancho_final', 'N/A')}m de ancho x {tarima.get('largo_final', 'N/A')}m de fondo, "
            f"altura sugerida {tarima.get('altura_sugerida', 'N/A')}m.\n"
            f"Silletería: capacidad calculada {sillas.get('capacidad_calculada', 'N/A')} asistentes, "
            f"distancia primera fila a la tarima {sillas.get('distancia_primera_fila_tarima_m', 'N/A')}m, "
            f"pasillos laterales de {sillas.get('ancho_pasillos_laterales', 'N/A')}m y pasillo central de "
            f"{sillas.get('ancho_pasillo_central', 'N/A')}m.\n\n"
            f"Técnica sugerida (estructura, sonido, iluminación, control y microfonía): {tecnica}.\n\n"
            "Ten en cuenta las fotos del espacio (si se proporcionan) para ajustar el análisis contextual "
            "y la recomendación de truss/stacking."
        )

        # -------------------------------
        # 4. Construir payload para Gemini
        # -------------------------------
        contents = []
        user_parts = [{"text": system_prompt + "\n\n" + query_text}]

        # Añadimos imágenes si vienen desde el frontend
        if imagenes_base64:
            image_parts = []
            for img_data in imagenes_base64:
                if img_data.startswith("data:image/png"):
                    mime_type = "image/png"
                elif img_data.startswith("data:image/jpeg") or img_data.startswith("data:image/jpg"):
                    mime_type = "image/jpeg"
                else:
                    print(f"Tipo de imagen no compatible: {img_data[:30]}...")
                    continue

                base64_part = img_data.split(",")[1]
                image_parts.append(
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": base64_part,
                        }
                    }
                )

            # Primero las imágenes, luego el texto
            user_parts = image_parts + user_parts

        contents.append({"role": "user", "parts": user_parts})

        payload = {"contents": contents}

        # -------------------------------
        # 5. Llamar a Gemini
        # -------------------------------
        analisis_texto = call_gemini_api(payload)

        if isinstance(analisis_texto, str) and analisis_texto.startswith("Error"):
            return jsonify({"error": analisis_texto}), 500

        return jsonify({"analisis_ia": analisis_texto})

    except Exception as e:
        print("Error en ruta /analisis_ia:", e)
        return jsonify({"error": f"Error al generar el análisis de IA: {str(e)}"}), 500

# ----------------------------------------
# RUTA /generar_pdf  (genera informe en PDF)
# ----------------------------------------

@app.route("/generar_pdf", methods=["POST"])
def generar_pdf():
    try:
        data = request.json
        if (
            not data
            or "resultados" not in data
            or "imagen_cenital_base64" not in data
            or "analisis_ia" not in data
        ):
            return (
                jsonify(
                    {
                        "error": "Datos incompletos para generar el PDF "
                        "(cálculos, plano cenital o análisis IA faltan)."
                    }
                ),
                400,
            )

        resultados = data["resultados"]
        imagen_cenital_base64 = data.get("imagen_cenital_base64")
        imagen_frontal_base64 = data.get("imagen_frontal_base64")  # puede ser None
        analisis_ia = data["analisis_ia"]

        fecha_evento = resultados.get("fecha_evento", "N/A")
        nombre_evento = resultados.get("nombre_evento", "N/A")
        nombre_escenario = resultados.get("nombre_escenario", "N/A")
        nombre_empresa = resultados.get("nombre_empresa", "N/A")

        pdf_buffer = pdf_gen.crear_pdf_informe(
            resultados,
            imagen_cenital_base64,
            imagen_frontal_base64,
            analisis_ia,
            fecha_evento,
            nombre_evento,
            nombre_escenario,
            nombre_empresa,
        )

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="Informe_Evento_Tecnico.pdf",
        )

    except Exception as e:
        print(f"Error generando PDF: {e}")
        return jsonify({"error": "Fallo al generar el documento PDF."}), 500


# ----------------------------------------
# EJECUCIÓN LOCAL
# ----------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=8080)
