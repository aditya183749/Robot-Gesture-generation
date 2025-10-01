import joblib
from typing import List, Dict
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

class RuleBased:
    def __init__(self, vocab: Dict[str, str]):
        self.vocab = {k.lower(): v for k, v in vocab.items()}

    def predict(self, tokens: List[str]) -> List[str]:
        return [self.vocab.get(t.lower(), "neutral") for t in tokens]

def make_pipeline() -> Pipeline:
    vec = TfidfVectorizer(ngram_range=(1,2), analyzer="word", lowercase=True)
    clf = LinearSVC()
    return Pipeline([("vec", vec), ("clf", clf)])

def train_model(dataset: List[Dict], test_size: float = 0.5, random_state: int = 42) -> Dict:
    X = [row["token"] for row in dataset]
    y = [row["gesture"] for row in dataset]

    if len(set(y)) < 2 or len(X) < 10:
        return {"pipeline": None, "report": "Dataset too small for ML; use rule-based only.", "acc": None}

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    pipe = make_pipeline()
    pipe.fit(Xtr, ytr)
    yhat = pipe.predict(Xte)
    acc = accuracy_score(yte, yhat)
    report = classification_report(yte, yhat)
    return {"pipeline": pipe, "report": report, "acc": float(acc)}

def save_model(pipeline: Pipeline, path: str) -> None:
    joblib.dump(pipeline, path)

def load_model(path: str) -> Pipeline:
    return joblib.load(path)
