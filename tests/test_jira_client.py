from integrations.jira_client import adf_text


def test_adf_un_paragraphe_par_ligne():
    doc = adf_text("ligne 1\n\nligne 3")
    assert doc["type"] == "doc" and len(doc["content"]) == 3
    assert doc["content"][1]["content"] == []
    assert doc["content"][2]["content"][0]["text"] == "ligne 3"
