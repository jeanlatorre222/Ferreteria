from django.test import TestCase


class HomePageTests(TestCase):
    def test_home_incluye_productos_destacados_y_estilos(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'home-category-grid')
        self.assertContains(response, 'home-product-grid')
        self.assertContains(response, 'Despacho a todo Chile')
        self.assertContains(response, 'landing.css?v=1')
        self.assertContains(response, 'Martillo')
