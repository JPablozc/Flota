from datetime import date, timedelta

from django.conf import settings
from django.core.mail import send_mail

from .models import DocumentoVehiculo


def obtener_documentos_para_alerta(dias=30):
    """
    Devuelve dos QuerySets:
    - proximos: documentos que vencen en <= dias
    - vencidos: documentos cuya fecha de vencimiento ya pasó
    """
    hoy = date.today()
    limite = hoy + timedelta(days=dias)

    proximos = DocumentoVehiculo.objects.filter(
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=limite
    )
    vencidos = DocumentoVehiculo.objects.filter(
        fecha_vencimiento__lt=hoy
    )

    return proximos, vencidos


def enviar_alerta_documentos(dias=30):
    """
    Construye un correo con el resumen de documentos vencidos / por vencer
    y lo envía a ALERTAS_EMAIL_DESTINO.
    Devuelve el número total de documentos incluidos en la alerta.
    """
    destino = getattr(settings, 'ALERTAS_EMAIL_DESTINO', None)
    if not destino:
        return 0

    proximos, vencidos = obtener_documentos_para_alerta(dias=dias)

    if not proximos and not vencidos:
        # Nada que reportar
        return 0

    lineas = []

    if vencidos:
        lineas.append("DOCUMENTOS VENCIDOS:")
        for d in vencidos:
            lineas.append(
                f"- {d.vehiculo.placa} | {d.tipo.nombre} | venció el {d.fecha_vencimiento}"
            )
        lineas.append("")  # línea en blanco

    if proximos:
        lineas.append(f"DOCUMENTOS PRÓXIMOS A VENCER (en {dias} días):")
        for d in proximos:
            lineas.append(
                f"- {d.vehiculo.placa} | {d.tipo.nombre} | vence el {d.fecha_vencimiento}"
            )

    cuerpo = "\n".join(lineas)

    send_mail(
        subject="Alertas de documentos de flota",
        message=cuerpo,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[destino],
    )

    return len(proximos) + len(vencidos)
