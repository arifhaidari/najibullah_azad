from django.test import TestCase


class TryDjangoConfigTest(TestCase):
     def test_the_config(self):
          a = 1
          b = 2
          self.assertTrue(a==b)


