import io
import base64
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


def crear_pdf_informe(
    resultados,
    imagen_cenital_base64,
    imagen_frontal_base64,
    analisis_ia,
    fecha_evento,
    nombre_evento,
    nombre_escenario,
    nombre_empresa,
):
    """
    Crea el documento PDF con todos los resultados del cálculo,
    planos cenital y frontal, metadatos y el análisis de la IA.
    Cada plano va en una página independiente.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title=f"Informe Técnico - {nombre_evento}",
    )

    styles = getSampleStyleSheet()

    estilo_ia = ParagraphStyle(
        name="IAAnalysis",
        parent=styles["Normal"],
        spaceBefore=10,
        spaceAfter=10,
        leftIndent=15,
        rightIndent=15,
        borderPadding=5,
        backColor=colors.lavender,
        borderColor=colors.blue,
        borderWidth=1,
        borderRadius=5,
        fontSize=10.5,
        leading=13,
    )

    estilo_info = ParagraphStyle(
        name="InfoBlock",
        parent=styles["Normal"],
        spaceBefore=5,
        fontSize=10,
    )

    Story = []

    # --- TÍTULO PRINCIPAL ---
    estilo_titulo = styles["Title"]
    estilo_titulo.alignment = 1  # centrado
    estilo_titulo.fontSize = 20
    Story.append(Paragraph("Informe Técnico de Diseño de Escenario", estilo_titulo))
    Story.append(Spacer(1, 0.2 * inch))

    # --- BLOQUE DE METADATOS ---
    Story.append(Paragraph(f"<b>Generado por: {nombre_empresa}</b>", styles["h3"]))

    try:
        fecha_formateada = datetime.strptime(fecha_evento, "%Y-%m-%d").strftime(
            "%d/%m/%Y"
        )
    except Exception:
        fecha_formateada = fecha_evento

    metadata_text = f"""
    <b>EVENTO:</b> {nombre_evento}
    <br/><b>ESCENARIO/SALÓN:</b> {nombre_escenario}
    <br/><b>FECHA DEL EVENTO:</b> {fecha_formateada}
    <br/><b>FECHA DE GENERACIÓN:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """
    Story.append(Paragraph(metadata_text, estilo_info))
    Story.append(Spacer(1, 0.3 * inch))

    # ---------------------------------------
    # 1. ANÁLISIS CONTEXTUAL DE IA
    # ---------------------------------------
    Story.append(
        Paragraph("<b>1. Análisis Contextual y Estratégico (Asistente IA)</b>", styles["h2"])
    )
    Story.append(Spacer(1, 0.1 * inch))

    analisis_formateado = analisis_ia.replace("\n", "<br/>")
    Story.append(Paragraph(analisis_formateado, estilo_ia))
    Story.append(Spacer(1, 0.3 * inch))

    # ---------------------------------------
    # 2. RESUMEN TÉCNICO DEL ESPACIO Y PANTALLAS
    # ---------------------------------------
    Story.append(
        Paragraph("<b>2. Resumen de Dimensiones, Capacidad y Video</b>", styles["h2"])
    )
    Story.append(Spacer(1, 0.1 * inch))

    salon_largo = resultados.get("largo_salon")
    salon_ancho = resultados.get("ancho_salon")
    salon_alto = resultados.get("alto_salon")
    asistentes = resultados.get("num_asistentes")

    tarima = resultados.get("tarima", {})
    sillas = resultados.get("sillas", {})
    pantalla = resultados.get("pantalla_principal") or resultados.get("pantalla", {})
    pantallas_extra = resultados.get("pantallas_adicionales", [])

    # Resumen pantallas adicionales
    extra_resumen = []
    for p in pantallas_extra:
        extra_resumen.append(
            f"{p.get('tipo')} #{p.get('indice')}: {p.get('ancho_m')}m x {p.get('alto_m')}m, "
            f"pitch {p.get('pitch_mm')}mm, pixel map {p.get('pixel_map')}, módulos {p.get('modulos_totales')}"
        )
    extra_resumen_text = "<br/>".join(extra_resumen) if extra_resumen else "Sin pantallas adicionales."

    data_resumen = [
        ["Concepto", "Valor Sugerido", "Detalle"],
        [
            "Salón (Largo x Ancho)",
            f"{salon_largo}m x {salon_ancho}m",
            f"Altura: {salon_alto}m",
        ],
        [
            "Asistentes Previstos",
            f"{asistentes}",
            f"Capacidad Calculada (silletería): {sillas.get('capacidad_calculada', 'N/A')}",
        ],
        [
            "Tarima (Ancho x Largo)",
            f"{tarima.get('ancho_final', 'N/A')}m x {tarima.get('largo_final', 'N/A')}m",
            f"Módulos (1.22x2.44): {tarima.get('modulos_ancho', 'N/A')} x {tarima.get('modulos_largo', 'N/A')}; altura sugerida: {tarima.get('altura_sugerida', 'N/A')}m",
        ],
        [
            "Distancias y Pasillos",
            f"1ª fila a tarima: {sillas.get('distancia_primera_fila_tarima_m', 'N/A')}m",
            f"Pasillos laterales: {sillas.get('ancho_pasillos_laterales', 'N/A')}m | Pasillo central: {sillas.get('ancho_pasillo_central', 'N/A')}m",
        ],
        [
            "Pantalla Principal",
            f"{pantalla.get('ancho_pantalla_w', 'N/A')}m x {pantalla.get('altura_pantalla_h', 'N/A')}m",
            f"{pantalla.get('relacion', '')}; pitch {pantalla.get('pitch_mm', 'N/A')}mm; pixel map {pantalla.get('pixel_map', 'N/A')}; "
            f"módulos LED totales: {pantalla.get('modulos_totales', 'N/A')}",
        ],
        [
            "Pantallas Adicionales",
            f"{len(pantallas_extra)} unidad(es)",
            extra_resumen_text,
        ],
    ]

    tabla_resumen = Table(
        data_resumen,
        colWidths=[2.3 * inch, 2 * inch, 3 * inch],
        repeatRows=1,
    )
    tabla_resumen.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]
        )
    )
    Story.append(tabla_resumen)
    Story.append(Spacer(1, 0.4 * inch))

    # ---------------------------------------
    # 3. PLANO CENITAL (PÁGINA PROPIA)
    # ---------------------------------------
    Story.append(Paragraph("<b>3. Plano Cenital Sugerido</b>", styles["h2"]))
    Story.append(Spacer(1, 0.1 * inch))

    if imagen_cenital_base64 and imagen_cenital_base64.startswith("data:image"):
        img_data = imagen_cenital_base64.split(",")[1]
        img_bytes = base64.b64decode(img_data)
        img = Image(io.BytesIO(img_bytes), width=6.5 * inch, height=4.0 * inch)
        img.hAlign = "CENTER"
        Story.append(img)
    else:
        Story.append(
            Paragraph(
                "<i>No se pudo generar el plano cenital para el informe.</i>",
                styles["Normal"],
            )
        )

    Story.append(PageBreak())

    # ---------------------------------------
    # 4. VISTA FRONTAL (PÁGINA PROPIA)
    # ---------------------------------------
    Story.append(Paragraph("<b>4. Vista Frontal Sugerida</b>", styles["h2"]))
    Story.append(Spacer(1, 0.1 * inch))

    if imagen_frontal_base64 and imagen_frontal_base64.startswith("data:image"):
        img_data = imagen_frontal_base64.split(",")[1]
        img_bytes = base64.b64decode(img_data)
        img = Image(io.BytesIO(img_bytes), width=6.5 * inch, height=3.5 * inch)
        img.hAlign = "CENTER"
        Story.append(img)
    else:
        Story.append(
            Paragraph(
                "<i>No se pudo generar la vista frontal para el informe.</i>",
                styles["Normal"],
            )
        )

    Story.append(Spacer(1, 0.4 * inch))

    # ---------------------------------------
    # 5. LISTA DE REQUERIMIENTOS TÉCNICOS
    # (la IA ya los menciona, pero aquí reforzamos)
    # ---------------------------------------
    Story.append(
        Paragraph("<b>5. Resumen de Requerimientos Técnicos</b>", styles["h2"])
    )
    Story.append(Spacer(1, 0.1 * inch))

    tecnica = resultados.get("tecnica", {})
    lista_req = []

    estructura = tecnica.get("estructura")
    sonido = tecnica.get("sonido")
    iluminacion = tecnica.get("iluminacion")
    control = tecnica.get("control")
    microfonia = tecnica.get("microfonia")
    consolas = tecnica.get("consolas")
    clicker = tecnica.get("clicker")

    if estructura:
        lista_req.append(f"1. Estructura / truss: {estructura}")
    if sonido:
        lista_req.append(f"2. Sonido: {sonido}")
    if iluminacion:
        lista_req.append(f"3. Iluminación: {iluminacion}")
    if control:
        lista_req.append(f"4. Puesto de control: {control}")
    if microfonia:
        lista_req.append(f"5. Microfonía: {microfonia}")
    if consolas:
        lista_req.append(f"6. Consolas de audio y video: {consolas}")
    if clicker:
        lista_req.append(f"7. Sistema de presentación / clicker: {clicker}")

    if lista_req:
        texto_req = "<br/>".join(lista_req)
    else:
        texto_req = "Los requerimientos técnicos detallados se describen en el análisis de la IA."

    Story.append(Paragraph(texto_req, styles["Normal"]))
    Story.append(Spacer(1, 0.2 * inch))

    # --- GENERAR PDF ---
    doc.build(Story)
    buffer.seek(0)
    return buffer
