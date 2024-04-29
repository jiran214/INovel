#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TextIO, cast, Optional, Dict, Any, List
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from loguru import logger

logfile = "output.log"
logger.remove()
logger.add(logfile, enqueue=True)


class FileCallbackHandler(BaseCallbackHandler):
    """Callback Handler that writes to a file."""

    def on_llm_start(
            self,
            serialized: Dict[str, Any],
            prompts: List[str],
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> Any:
        logger.debug(f"> LLM Prompt Input.\n{prompts}")

    def on_llm_end(
            self,
            response: LLMResult,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        """Run when LLM ends running."""
        logger.debug(f"> Finished LLM.\n{response.llm_output}")