import unittest
from bs4 import BeautifulSoup

class TestParsers(unittest.TestCase):

     def test_parse_eltiempo(self):
        html = '''
        <article>
            <a href="/noticias/colombia">Egan Bernal y Einer Rubio sacaron la cara por Colombia</a>
        </article>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        resultados = []

        for article in soup.select("article a[href]"):
            titulo = article.get_text(strip=True)
            enlace = article.get("href")
            if enlace and not enlace.startswith("http"):
                enlace = "https://www.eltiempo.com" + enlace
            if titulo and enlace:
                resultados.append(["General", titulo, enlace])

        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0][1], "Egan Bernal y Einer Rubio sacaron la cara por Colombia")
        self.assertTrue(resultados[0][2].startswith("https://www.eltiempo.com"))

     def test_parse_elespectador(self):
        html = '''
        <article>
            <span>Ciclismo</span>
            <a href="/deportes/ciclismo">Así le fue a los colombianos en el Giro de Italia</a>
        </article>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        resultados = []

        for card in soup.select("article"):
            categoria_tag = card.select_one("span")
            titulo_tag = card.select_one("a[href]")

            categoria = categoria_tag.get_text(strip=True) if categoria_tag else "General"
            titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""
            enlace = titulo_tag.get("href") if titulo_tag else ""

            if enlace and not enlace.startswith("http"):
                enlace = "https://www.elespectador.com" + enlace

            if titulo and enlace:
                resultados.append([categoria, titulo, enlace])

        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0][0], "Ciclismo")
        self.assertIn("Giro de Italia", resultados[0][1])
        self.assertTrue(resultados[0][2].startswith("https://www.elespectador.com"))

if __name__ == '__main__':
    unittest.main()
