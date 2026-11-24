def sugerir_accion(intencion: str, sentimiento: str) -> str:
    if intencion == "INTENCION_NO_CLARA":
        return "DERIVAR_A_SUPERVISOR"
    if intencion == "REPORTE_CALIDAD":
        return "ALERTA_CRITICA_CALIDAD" if sentimiento == "NEGATIVO" else "REGISTRAR_CONTROL_CALIDAD"
    if intencion == "FALLA_EQUIPO":
        return "ORDEN_MANTENIMIENTO_INMEDIATO"
    if intencion == "CONSULTA_INVENTARIO":
        return "CONSULTAR_STOCK_ALMACEN"
    if intencion == "SOLICITUD_DESPACHO":
        return "PROGRAMAR_MUELLE_Y_GUIA"
    return "REVISION_OPERATIVA"