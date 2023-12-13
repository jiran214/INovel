#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langchain_core.prompts import PromptTemplate


def temple(string_temple) -> PromptTemplate:
    return PromptTemplate.from_template(string_temple)