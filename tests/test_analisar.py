import unittest
from unittest.mock import patch, MagicMock
from scripts.analisar import (
    categorizar_comentario,
    classificar_comentarios,
    calcular_engajamento_posts,
    gerar_relatorio_markdown,
    buscar_dados_perfil,
    executar_analise,
)


class TestAnalisar(unittest.TestCase):
    def test_categorizar_comentario_cta(self):
        c = {"id": "1", "text": "Eu quero! PRATINHO por favor", "username": "maria"}
        cat = categorizar_comentario(c, palavra_cta="PRATINHO")
        self.assertEqual(cat, "cta_lead")

    def test_categorizar_comentario_duvida(self):
        c = {"id": "2", "text": "Pode congelar essa receita? Como preparar?", "username": "joana"}
        cat = categorizar_comentario(c, palavra_cta="PRATINHO")
        self.assertEqual(cat, "duvida")

    def test_categorizar_comentario_pedido_receita(self):
        c = {"id": "3", "text": "Faz uma receita de almoço com inhame!", "username": "carla"}
        cat = categorizar_comentario(c, palavra_cta="PRATINHO")
        self.assertEqual(cat, "pedido_receita")

    def test_categorizar_comentario_elogio(self):
        c = {"id": "4", "text": "Meu bebê adorou, parabéns pelo conteúdo lindo!", "username": "paula"}
        cat = categorizar_comentario(c, palavra_cta="PRATINHO")
        self.assertEqual(cat, "elogio")

    def test_classificar_comentarios_lista(self):
        comentarios = [
            {"id": "1", "text": "PRATINHO", "username": "user1"},
            {"id": "2", "text": "Pode dar para bebê de 6 meses?", "username": "user2"},
            {"id": "3", "text": "Muito bom!", "username": "user3"},
        ]
        res = classificar_comentarios(comentarios, palavra_cta="PRATINHO")
        self.assertEqual(len(res["cta_lead"]), 1)
        self.assertEqual(len(res["duvida"]), 1)
        self.assertEqual(len(res["elogio"]), 1)

    def test_calcular_engajamento_posts(self):
        posts = [
            {"id": "p1", "like_count": 10, "comments_count": 2, "caption": "Post 1"},
            {"id": "p2", "like_count": 30, "comments_count": 5, "caption": "Post 2"},
        ]
        ranking = calcular_engajamento_posts(posts)
        self.assertEqual(ranking[0]["id"], "p2")
        self.assertEqual(ranking[0]["engajamento_total"], 35)
        self.assertEqual(ranking[1]["id"], "p1")

    def test_gerar_relatorio_markdown(self):
        posts = [{"id": "p1", "like_count": 10, "comments_count": 2, "caption": "Panqueca de banana", "permalink": "https://instagr.am/p1"}]
        ranking = calcular_engajamento_posts(posts)
        categorias = {
            "cta_lead": [{"username": "mae1", "text": "PRATINHO"}],
            "duvida": [{"username": "mae2", "text": "Pode congelar?"}],
            "pedido_receita": [],
            "elogio": [],
            "outros": [],
        }
        md = gerar_relatorio_markdown(ranking, categorias, total_posts=1)
        self.assertIn("# Relatório de Desempenho", md)
        self.assertIn("Panqueca de banana", md)
        self.assertIn("PRATINHO", md)
        self.assertIn("Pode congelar?", md)

    @patch("scripts.analisar.ig")
    def test_buscar_dados_perfil(self, mock_ig):
        mock_ig.eu.return_value = {"user_id": "12345", "username": "testuser"}
        mock_ig.get.side_effect = [
            # 1. media list
            {"data": [{"id": "m1", "caption": "Post 1", "like_count": 5, "comments_count": 1, "permalink": "url1"}]},
            # 2. comments list for m1
            {"data": [{"id": "c1", "text": "PRATINHO", "username": "user1"}]},
            # 3. insights (fails or succeeds)
            {"data": []},
        ]
        dados = buscar_dados_perfil(limite=5)
        self.assertEqual(len(dados["posts"]), 1)
        self.assertEqual(len(dados["comentarios"]), 1)
        self.assertEqual(dados["user"]["username"], "testuser")

    @patch("scripts.analisar.buscar_dados_perfil")
    def test_executar_analise(self, mock_buscar):
        mock_buscar.return_value = {
            "user": {"user_id": "12345", "username": "testuser"},
            "posts": [{"id": "m1", "caption": "Post 1", "like_count": 5, "comments_count": 1, "permalink": "url1"}],
            "comentarios": [{"id": "c1", "text": "PRATINHO", "username": "user1"}],
        }
        res = executar_analise(limite=5, palavra_cta="PRATINHO")
        self.assertIn("# Relatório de Desempenho", res)
        self.assertIn("PRATINHO", res)


if __name__ == "__main__":
    unittest.main()
