import unittest

from app.routers.routes_doctor import _resumen_desempeno_evaluacion


class TestEvaluationSummary(unittest.TestCase):
    def test_summary_includes_progress_score_and_evidence(self):
        doc = {
            "puntaje_sistema": 82,
            "paso_completado": 3,
            "total_pasos": 5,
            "progreso_pct": 60,
            "detalle_actividad": "Recorrido en /juegos/fonacion/gol con progreso 3/5",
            "audio_transcripcion": "La /a/ está mejorando.",
            "ruta_juego": "/juegos/fonacion/gol",
            "completado": True,
        }

        summary = _resumen_desempeno_evaluacion(doc)

        self.assertEqual(summary["estado"], "Completado")
        self.assertEqual(summary["progreso"], "3/5")
        self.assertEqual(summary["puntaje"], 82)
        self.assertEqual(summary["progreso_pct"], 60)
        self.assertIn("Recorrido", summary["evidencia"][0])
        self.assertIn("La /a/", summary["evidencia"][1])

    def test_summary_includes_notes_and_audio_when_saved_in_result(self):
        doc = {
            "puntaje_sistema": 72,
            "paso_completado": 2,
            "total_pasos": 3,
            "progreso_pct": 67,
            "notas": "Palabras difíciles: traba, claro, tiro.",
            "audio_transcripcion": "La /a/ salió mejor que la semana pasada.",
            "audio_url": "/juegos/evidencia-audio/abc123",
            "ruta_juego": "/juegos/prosodia/trabalenguas",
            "completado": True,
        }

        summary = _resumen_desempeno_evaluacion(doc)

        self.assertIn("Palabras difíciles", " ".join(summary["evidencia"]))
        self.assertIn("La /a/ salió mejor", " ".join(summary["evidencia"]))
        self.assertTrue(any("audio" in item.lower() for item in summary["evidencia"]))


if __name__ == "__main__":
    unittest.main()
