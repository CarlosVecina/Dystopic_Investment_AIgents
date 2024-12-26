from pydantic import BaseModel, PrivateAttr
import logging

from dystopic_investment_aigents.agents.base_agents.agent_base import Agent

logging.basicConfig(level=logging.INFO)


class Discussion(BaseModel):
    topic: str
    rules: str | None = "Conciseness is key. You should not repeat the same message multiple times or abuse introduction formulas."
    max_turns: int = 10
    participants: list[tuple[Agent, str]]

    _current_turn: int = PrivateAttr(default=0)
    _history: list[tuple[str, str]] = PrivateAttr(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def __call__(self) -> list[tuple[str, str]]:        
        logging.info(f"Starting discussion on topic: {self.topic}")
        context = (
            f"You are in a conversation with other participants. "
            f"Try to be persuasive and convince the other participants to agree with you. "
            f"Topic of discussion: {self.topic}\n"
            f"Rules: {self.rules}\n"
        )

        if len(self.participants) < 2:
            logging.error("Not enough participants for discussion")
            raise ValueError("Need at least 2 participants for a discussion")

        logging.info(f"Beginning discussion with {len(self.participants)} participants")
        while self._current_turn < self.max_turns:
            logging.info(f"Starting turn {self._current_turn + 1}/{self.max_turns}")
            for agent, agent_goal in self.participants:
                logging.debug(f"Agent with mood {agent.personality.mood.value} is thinking...")
                if self._current_turn == self.max_turns - 1:
                    agent_goal += "You should summarize the discussion as this is the final round."
                agent_context = (
                    f"{context}\n"
                    f"Your mood is: {agent.personality.mood.value}\n"
                    f"Your goal is: {agent_goal}\n"
                    f"Previous messages:\n{self._format_history(self._history, agent)}\n"
                    "Your response:"
                )
                logging.info(f"Starting turn {self._current_turn + 1}/{self.max_turns}")
                logging.info(agent_context)

                logging.debug("Generating Agent response...")
                response = agent.discuss(agent_context)
                logging.info(f"Response received: {response}")
                self._history.append((agent.id, response))

            self._current_turn += 1

        logging.info("Discussion completed")
        return self._history

    def _format_history(self, history: list[tuple[str, str]], agent: Agent) -> str:
        if len(history) == 0:
            return ""
        formatted = []
        for i, entry in enumerate(history):
            agent_id = entry[0]
            message = entry[1]
            if agent_id == agent.id:
                formatted.append(f"[Message number: {i+1} - Participant: 'YOU']: {message}")
            else:
                formatted.append(f"[Message number: {i+1} - Participant: '{agent_id}']: {message}")
        return "\n".join(formatted)
