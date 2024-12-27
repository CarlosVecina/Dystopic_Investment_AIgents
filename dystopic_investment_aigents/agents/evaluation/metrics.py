from sentence_transformers import SentenceTransformer, util

from pydantic import BaseModel, Field, ConfigDict
from typing import List


class Metrics(BaseModel):
    model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence Transformer model to use for semantic evaluation",
    )
    model: SentenceTransformer = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.model = SentenceTransformer(self.model_name)

    def _semantic_similarity(
        self, predictions: List[str] | None = None, references: List[str] | None = None
    ) -> float:
        """
        Calculate the semantic similarity between predictions and references.

        :param predictions: Optional list of predictions to evaluate. If None, uses instance predictions.
        :param references: Optional list of references to evaluate. If None, uses instance references.
        :return: Average semantic similarity score.
        """
        embeddings_pred = self.model.encode(predictions, convert_to_tensor=True)
        embeddings_ref = self.model.encode(references, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(embeddings_pred, embeddings_ref).diagonal()
        return similarities.mean().item() * 100

    def contextual_relevance(
        self, predictions: List[str] | None = None, references: List[str] | None = None
    ) -> float:
        """
        Evaluate the contextual relevance by comparing embeddings.

        :param predictions: Optional list of predictions to evaluate. If None, uses instance predictions.
        :param references: Optional list of references to evaluate. If None, uses instance references.
        :return: Relevance score (higher is better).
        """
        return self._semantic_similarity(predictions, references)
