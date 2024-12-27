import json
from typing import Callable
from jinja2 import Template
from pydantic import BaseModel, RootModel, ConfigDict, Field
from litellm import completion


class JudgeResponse(BaseModel):
    score: float = Field(
        ge=1,
        le=10,
        description="The score of the prediction compared to the reference on a scale of 1-10.",
    )
    rationale: str | None = Field(None, description="The rationale for the score.")


class JudgeResponses(RootModel[list[JudgeResponse]]):
    root: list[JudgeResponse]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def append(self, item: JudgeResponse):
        self.root.append(item)

    def get_scores(self):
        return [response.score for response in self.root]

    def agg_score(
        self, agg_func: Callable[[list[float]], float] = lambda x: sum(x) / len(x)
    ):
        return agg_func([response.score for response in self.root])


class LLMJudge(BaseModel):
    model: str = Field(
        default="gpt-4o-mini",
        description="The model to use for the LLM.",
    )
    system_prompt: str = Field(
        default="You are a helpful assistant that evaluates text quality on a scale of 1-10.",
        description="The system prompt for the LLM.",
    )
    user_prompt_template: Template = Field(
        default=Template(
            """
            Please evaluate the quality of the following prediction compared to the reference on a scale of 1-10,
            where 1 is completely wrong/irrelevant and 10 is perfect/exact match.
            {{ context if context else ""}}
            
            Reference: {{ ref }}
            Prediction: {{ pred }}
            
            Output format:
            {
                "score": <float {{ min_score }} low quality to {{ max_score }} high quality>,
                {% if incl_rationale %}"rationale": <str>,{% endif %}
            }
            """
        )
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def evaluate(
        self,
        predictions: list[str],
        references: list[str],
        context: str | None = None,
        incl_rationale: bool = False,
        min_score: float = 1,
        max_score: float = 10,
    ):
        """
        Use LLM to assess quality of predictions compared to references on a 1-10 scale.

        :param system_prompt: System prompt for the LLM
        :return: Average quality score (1-10)
        """
        if len(predictions) != len(references):
            raise ValueError("Predictions and references must have the same length.")
        if (not isinstance(predictions, list)) | (not isinstance(references, list)):
            raise ValueError("Predictions and references must be lists.")

        judge_responses: JudgeResponses = []
        for pred, ref in zip(predictions, references):
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": self.user_prompt_template.render(
                            context=context,
                            pred=pred,
                            ref=ref,
                            incl_rationale=incl_rationale,
                            min_score=min_score,
                            max_score=max_score,
                        ),
                    },
                ],
            )

            parsed_response = JudgeResponse(
                **json.loads(response.choices[0].message.content.strip())
            )
            judge_responses.append(parsed_response)

        return JudgeResponses(root=judge_responses)

    def evaluate_agg(
        self, predictions: list[str], references: list[str], context: str | None = None
    ):
        scores = self.evaluate(predictions, references, context)
        return scores.agg_score()
