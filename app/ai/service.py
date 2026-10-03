import logging

from langchain_core.messages import AIMessage, HumanMessage

from app.ai.graph import graph
from app.db.repositories.conversation_repository import conversation_repository, resolve_user_id

logger = logging.getLogger(__name__)


class AIService:

    async def generate_response(
        self,
        message: str,
        conversation_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> tuple[str, str]:
        try:
            resolved_user_id = resolve_user_id(user_id)

            if session_id:
                conversation = await conversation_repository.get_session(session_id)
                if conversation is None:
                    conversation = await conversation_repository.create_conversation(user_id=resolved_user_id, session_id=session_id)
                conversation_id = conversation.conversation_id
            elif conversation_id:
                conversation = await conversation_repository.get_conversation(conversation_id)
                if conversation is None:
                    conversation = await conversation_repository.create_conversation(user_id=resolved_user_id, session_id=session_id)
                conversation_id = conversation.conversation_id
            else:
                conversation = await conversation_repository.get_latest_session_for_user(resolved_user_id)
                if conversation is None:
                    conversation = await conversation_repository.create_conversation(user_id=resolved_user_id, session_id=session_id)
                conversation_id = conversation.conversation_id

            session_id = conversation.session_id

            history = await conversation_repository.get_history(conversation_id)
            state_messages = []

            for item in history:
                if item.role == "user":
                    state_messages.append(HumanMessage(content=item.content))
                elif item.role == "assistant":
                    state_messages.append(AIMessage(content=item.content))

            state_messages.append(HumanMessage(content=message))

            result = await graph.ainvoke({"messages": state_messages})
            messages = result.get("messages", [])
            if not messages:
                response_text = "I’m not able to answer that right now. Please try again."
            else:
                response_text = messages[-1].content

            await conversation_repository.append_message(conversation_id, "user", message)
            await conversation_repository.append_message(conversation_id, "assistant", response_text)

            return response_text, conversation_id

        except Exception:
            logger.exception("AI graph invocation failed")
            fallback = "I’m temporarily unable to answer that request. Please try again in a moment."
            return fallback, conversation_id or ""


ai_service = AIService()