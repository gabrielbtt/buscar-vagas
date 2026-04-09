from app.services.notifier import build_digest_email


def test_build_digest_email_lists_jobs_with_scores():
    html = build_digest_email(
        [
            {
                "title": "Estagio em Automacao Industrial",
                "company": "IHM Stefanini",
                "location": "Belo Horizonte, MG",
                "score": 0.91,
                "url": "https://example.com/jobs/1",
            }
        ]
    )
    assert "IHM Stefanini" in html
    assert "0.91" in html
    assert "https://example.com/jobs/1" in html
