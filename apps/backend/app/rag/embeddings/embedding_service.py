from sklearn.feature_extraction.text import TfidfVectorizer


def embed_documents(texts: list[str]) -> tuple[TfidfVectorizer, list[list[float]]]:
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix.toarray().tolist()
