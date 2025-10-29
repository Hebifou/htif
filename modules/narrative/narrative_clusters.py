from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from typing import List, Dict

_topic_model = None


def get_topic_model(nr_topics=5) -> BERTopic:
    global _topic_model
    if _topic_model is None:
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        vectorizer_model = CountVectorizer(ngram_range=(1, 3), stop_words="english")
        _topic_model = BERTopic(
            embedding_model=embedding_model,
            vectorizer_model=vectorizer_model,
            language="multilingual",
            nr_topics=nr_topics
        )
    return _topic_model


def add_narrative_clusters(entries: List[Dict], nr_topics: int = 5, **kwargs) -> List[Dict]:
    """
    Fügt den Einträgen narrative Cluster-Labels hinzu.
    Akzeptiert **kwargs, damit module_report und topic übergeben werden können.
    """
    module_report = kwargs.get("module_report", {})

    texts = [item.get("quote", "") for item in entries]
    valid_indices = [i for i, t in enumerate(texts) if len(t.strip()) > 10]
    valid_texts = [texts[i] for i in valid_indices]

    if not valid_texts:
        module_report["narrative_clusters"] = "Keine gültigen Quotes gefunden"
        return entries

    try:
        topic_model = get_topic_model(nr_topics=nr_topics)
        topics, _ = topic_model.fit_transform(valid_texts)

        topic_info = topic_model.get_topic_info()
        topic_dict = dict(zip(topic_info.Topic, topic_info.Name))

        for local_idx, data_idx in enumerate(valid_indices):
            topic_id = topics[local_idx]
            topic_name = topic_dict.get(topic_id, f"Topic {topic_id}")
            entries[data_idx]["narrative_topic"] = topic_id
            entries[data_idx]["narrative_label"] = f"{topic_id}_{topic_name.replace(' ', '_')[:50]}"

        module_report["narrative_clusters"] = "Erfolgreich"
    except Exception as e:
        module_report["narrative_clusters"] = f"Fehler: {str(e)}"

    return entries
