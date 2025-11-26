from django.core.management.base import BaseCommand

from gestion_flota.services import enviar_alerta_documentos


class Command(BaseCommand):
    help = (
        "Envía por correo un resumen de los documentos de flota "
        "que están vencidos o próximos a vencer."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Número de días hacia adelante para considerar "próximos a vencer".'
        )

    def handle(self, *args, **options):
        dias = options['dias']
        total = enviar_alerta_documentos(dias=dias)

        if total:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Se envió una alerta con {total} documento(s) en riesgo."
                )
            )
        else:
            self.stdout.write("No hay documentos vencidos ni próximos a vencer. No se envió correo.")
