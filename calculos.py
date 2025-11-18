import math

# --- Constantes y Parámetros ---

# Distancias / seguridad
DISTANCIA_SEGURIDAD_PANTALLA_TARIMA = 0.50  # separación visual
DISTANCIA_PRIMERA_FILA_TARIMA = 2.00        # zona muerta frente a tarima
REGLA_PANTALLA_H_A_D = 8
ANCHO_PASILLO_MINIMO = 1.00  # m

# Tarima
MODULO_TARIMA_LARGO = 2.44
MODULO_TARIMA_ANCHO = 1.22
ALTURA_TARIMA_ESTANDAR = 0.60  # m

# Sillas
ANCHO_SILLA = 0.50
LARGO_SILLA_CON_ESPACIO = 1.00

# Screen Pitch (distancias mínimas)
PITCH_2_5_MIN_DIST = 6.25
PITCH_2_9_MIN_DIST = 7.25

# Módulos LED (suposición típica 0.5 x 0.5 m)
MODULO_LED_ANCHO = 0.5
MODULO_LED_ALTO = 0.5


# --- Helpers ---

def calcular_pixel_y_modulos(ancho_m, alto_m, pitch_mm):
    """Devuelve pixel map y cantidad de módulos para una pantalla."""
    pixel_width = int((ancho_m * 1000) / pitch_mm)
    pixel_height = int((alto_m * 1000) / pitch_mm)

    mod_ancho = math.ceil(ancho_m / MODULO_LED_ANCHO)
    mod_alto = math.ceil(alto_m / MODULO_LED_ALTO)
    num_modulos = mod_ancho * mod_alto

    return {
        "pixel_width": pixel_width,
        "pixel_height": pixel_height,
        "modulos_ancho": mod_ancho,
        "modulos_alto": mod_alto,
        "modulos_totales": num_modulos,
    }


# --- Pantalla principal ---

def sugerir_tamano_pantalla(largo_salon, altura_salon, relacion_aspecto="16:9"):
    """Calcula dimensiones de pantalla LED, pitch, pixel map y módulos."""
    # Distancia máxima de visualización: 90% del largo del salón
    distancia_espectador_max = largo_salon * 0.90
    altura_h_sugerida = distancia_espectador_max / REGLA_PANTALLA_H_A_D

    ratios = {"16:9": 16/9, "9:16": 9/16, "1:1": 1.0}
    ratio = ratios.get(relacion_aspecto, 16/9)
    aspect_ratio_tag = f"{relacion_aspecto} " + (
        "Horizontal" if relacion_aspecto == "16:9"
        else "Vertical" if relacion_aspecto == "9:16"
        else "Cuadrado"
    )

    ancho_w_sugerido = altura_h_sugerida * ratio

    # Altura base (BOS)
    altura_tarima = ALTURA_TARIMA_ESTANDAR
    altura_bos = altura_tarima + DISTANCIA_SEGURIDAD_PANTALLA_TARIMA

    max_top_altura = altura_salon - 0.50
    h_max_por_altura_salon = max_top_altura - altura_bos
    altura_h_final = min(altura_h_sugerida, h_max_por_altura_salon)
    ancho_w_final = altura_h_final * ratio

    # Decisión de pitch
    distancia_minima_visualizacion = largo_salon * 0.10
    if distancia_minima_visualizacion < PITCH_2_5_MIN_DIST:
        pitch_mm = 2.5
        pitch_recomendado = (
            "2.5mm o menor (pitch muy fino / aumentar distancia de primera fila)."
        )
    elif distancia_minima_visualizacion < PITCH_2_9_MIN_DIST:
        pitch_mm = 2.5
        pitch_recomendado = "2.5mm (Mayor calidad/Densidad) - Mínimo requerido."
    else:
        pitch_mm = 2.9
        pitch_recomendado = "2.9mm (Más económico, calidad estándar)."

    pixel_info = calcular_pixel_y_modulos(ancho_w_final, altura_h_final, pitch_mm)

    return {
        "relacion": aspect_ratio_tag,
        "relacion_cruda": relacion_aspecto,
        "altura_pantalla_h": round(altura_h_final, 2),
        "ancho_pantalla_w": round(ancho_w_final, 2),
        "altura_base_pantalla_bos": round(altura_bos, 2),
        "altura_max_tope_top": round(altura_bos + altura_h_final, 2),
        "pitch_sugerido": pitch_recomendado,
        "pitch_mm": pitch_mm,
        **pixel_info,
    }


# --- Tarima ---

def sugerir_tarima(ancho_salon, num_asistentes):
    """Sugiere dimensiones de tarima en múltiplos de módulos."""
    ancho_tarima_sugerido = min(ancho_salon * 0.40, 15.0)
    largo_tarima_sugerido = MODULO_TARIMA_ANCHO  # 1.22 profundidad mínima

    modulos_ancho = math.ceil(ancho_tarima_sugerido / MODULO_TARIMA_ANCHO)
    ancho_final = modulos_ancho * MODULO_TARIMA_ANCHO

    modulos_largo = math.ceil(largo_tarima_sugerido / MODULO_TARIMA_LARGO)
    largo_final = modulos_largo * MODULO_TARIMA_LARGO

    return {
        "largo_final": round(largo_final, 2),
        "ancho_final": round(ancho_final, 2),
        "modulos_largo": modulos_largo,
        "modulos_ancho": modulos_ancho,
        "altura_sugerida": ALTURA_TARIMA_ESTANDAR,
    }


# --- Sillas y corredores ---

def calcular_sillas_y_corredores(largo_salon, ancho_salon, num_asistentes):
    """Calcula distribución simple de sillas y pasillos."""
    espacio_ocupado_frontal = sugerir_tarima(ancho_salon, num_asistentes)['largo_final'] \
                               + DISTANCIA_PRIMERA_FILA_TARIMA

    largo_silleteria = max(largo_salon - espacio_ocupado_frontal, 0)

    num_filas = math.floor(largo_silleteria / LARGO_SILLA_CON_ESPACIO)

    ancho_libre_sillas = ancho_salon - (2 * ANCHO_PASILLO_MINIMO)
    sillas_por_fila_total = math.floor(ancho_libre_sillas / ANCHO_SILLA)

    sillas_por_bloque = math.floor(
        (sillas_por_fila_total - ANCHO_PASILLO_MINIMO / ANCHO_SILLA) / 2
    )

    if sillas_por_bloque < 1 or num_filas < 1:
        sillas_por_bloque = 0
        bloques = 0
        capacidad_max = 0
    else:
        bloques = 2
        capacidad_max = num_filas * (sillas_por_bloque * 2)

    return {
        "largo_silleteria_disponible": round(largo_silleteria, 2),
        "num_filas": num_filas,
        "sillas_por_bloque": sillas_por_bloque,
        "bloques_sillas": bloques,
        "ancho_pasillos_laterales": ANCHO_PASILLO_MINIMO,
        "ancho_pasillo_central": ANCHO_PASILLO_MINIMO,
        "capacidad_calculada": capacidad_max,
        "distancia_primera_fila_tarima": DISTANCIA_PRIMERA_FILA_TARIMA,
    }


# --- Pantallas adicionales ---

def configurar_pantallas_adicionales(pantalla_principal,
                                     num_aux_16_9=0,
                                     num_lagrimas_9_16=0,
                                     num_cuadradas_1_1=0):
    """Genera configuración de pantallas adicionales a partir de la principal."""
    pantallas = []
    pitch_mm = pantalla_principal.get("pitch_mm", 2.9)

    # Auxiliares 16:9 laterales (70% tamaño de la principal)
    for i in range(num_aux_16_9):
        altura = pantalla_principal["altura_pantalla_h"] * 0.8
        ancho = altura * (16 / 9)
        info_px = calcular_pixel_y_modulos(ancho, altura, pitch_mm)
        pantallas.append({
            "nombre": f"Pantalla Auxiliar {i + 1}",
            "tipo": "auxiliar 16:9 lateral",
            "relacion": "16:9",
            "ancho_m": round(ancho, 2),
            "altura_m": round(altura, 2),
            "pitch_mm": pitch_mm,
            **info_px,
            "indice": i + 1,
        })

    # Lágrimas 9:16
    for i in range(num_lagrimas_9_16):
        altura = pantalla_principal["altura_pantalla_h"] * 0.9
        ancho = altura * (9 / 16)
        info_px = calcular_pixel_y_modulos(ancho, altura, pitch_mm)
        pantallas.append({
            "nombre": f"Lágrima {i + 1}",
            "tipo": "lágrima 9:16",
            "relacion": "9:16",
            "ancho_m": round(ancho, 2),
            "altura_m": round(altura, 2),
            "pitch_mm": pitch_mm,
            **info_px,
            "indice": i + 1,
        })

    # Pantallas cuadradas 1:1
    for i in range(num_cuadradas_1_1):
        altura = pantalla_principal["altura_pantalla_h"] * 0.6
        ancho = altura
        info_px = calcular_pixel_y_modulos(ancho, altura, pitch_mm)
        pantallas.append({
            "nombre": f"Pantalla 1:1 - {i + 1}",
            "tipo": "auxiliar 1:1",
            "relacion": "1:1",
            "ancho_m": round(ancho, 2),
            "altura_m": round(altura, 2),
            "pitch_mm": pitch_mm,
            **info_px,
            "indice": i + 1,
        })

    return pantallas


# --- Técnica general ---

def sugerir_tecnica(num_asistentes, relacion_aspecto):
    """Sugiere técnica según escala del evento (práctica en Colombia)."""
    tecnica = {
        "estructura": "",
        "iluminacion": "",
        "sonido": "",
        "control": "",
        "microfonia": "",
        "consolas": "",
        "clicker": "PerfectCue o similar (obligatorio para presentaciones)",
    }

    # Estructura
    if num_asistentes > 300:
        tecnica["estructura"] = (
            "TRUSS Ground Support o volado para pantalla principal y auxiliares, "
            "más rigging para Line Array."
        )
    else:
        tecnica["estructura"] = (
            "Stacking para la pantalla principal y/o truss frontal ligero para iluminación."
        )

    # Sonido
    if num_asistentes < 150:
        tecnica["sonido"] = (
            "Sistema L/R de punto fuente o columnas activas, con 1-2 subwoofers por lado."
        )
        tecnica["consolas"] = (
            "Consola de sonido digital compacta (X32/M32) + switcher de video sencillo."
        )
    else:
        tecnica["sonido"] = (
            "Sistema Line Array L/R con subwoofers apilados o colgados; monitores de tarima."
        )
        tecnica["consolas"] = (
            "Consola digital profesional (DiGiCo / Allen&Heath) + matriz de video escalable."
        )

    # Iluminación
    if num_asistentes < 150:
        tecnica["iluminacion"] = (
            "PAR LED / paneles para bañar tarima y 2-4 perfiles LEKO para recorte de ponente."
        )
    else:
        tecnica["iluminacion"] = (
            "Moving heads Spot/Wash, barras LED para fondos, elipsoidales para ponente y mesa."
        )

    # Control
    tecnica["control"] = (
        "Puesto de control a 2/3 del largo del salón, centrado, elevado 0.30m, "
        "con espacio para audio, video e iluminación."
    )

    # Microfonía
    tecnica["microfonia"] = (
        "Micrófonos de solapa/diadema para ponentes, 2–4 micrófonos de mano inalámbricos, "
        "sistema de respaldo cableado."
    )

    return tecnica
