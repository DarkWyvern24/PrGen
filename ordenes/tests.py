from django.test import TestCase
from django.urls import reverse
from .models import OrdenTrabajo


class OrdenTrabajoModelTest(TestCase):
    def test_creacion_ot(self):
        ot = OrdenTrabajo.objects.create(
            numero="12345678",
            numero_cotizacion="87654321",
            cliente="Cliente Prueba",
            referencia="Referencia Test",
            atencion="Juan Pérez",
            responsable="María Soto",
            estado="Pendiente",
            nivel_urgencia="Alta"
        )

        self.assertEqual(ot.numero, "12345678")
        self.assertEqual(str(ot), "OT 12345678")


class OrdenTrabajoViewsTest(TestCase):
    def setUp(self):
        self.ot = OrdenTrabajo.objects.create(
            numero="12345678",
            numero_cotizacion="87654321",
            cliente="Cliente Prueba",
            referencia="Referencia Test",
            atencion="Juan Pérez",
            responsable="María Soto",
            estado="Pendiente",
            nivel_urgencia="Alta"
        )

    def test_listado_ot_responde_200(self):
        response = self.client.get(reverse("ordenes:listado_ot"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "12345678")

    def test_detalle_ot_responde_200(self):
        response = self.client.get(
            reverse("ordenes:detalle_ot", kwargs={"pk": self.ot.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente Prueba")