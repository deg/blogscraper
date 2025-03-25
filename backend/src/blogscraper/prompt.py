"""Defines LLM prompt templates for summarizing blog posts.

Provides predefined prompt text that instructs language models to analyze and
summarize AI and software development blog posts.

Usage:
    Import these constants to include structured prompts when generating LLM
    input data.
"""

# Allow long lines
# flake8: noqa: E501


from blogscraper.types import FilterRangeQuery


def promptPrefix(query: FilterRangeQuery) -> str:
    if query.match_string:
        context_phrase = (
            f"containing stories including some with text matching regex《{query.match_string}》. "
            "I am only interested in those stories. Ignore other stories in these pages"
        )
    else:
        context_phrase = "focused on AI and software development"
    return f"""
# MISSION: SUMMARIZE ARTICLES FROM THE WEB

Here are links to some recent blog posts from {query.start_date} through {query.end_date}, {context_phrase}. Each of these posts typically discusses multiple current stories in great detail.

## URLs of articles to read from the Web
"""


def promptSuffix(query: FilterRangeQuery) -> str:
    if query.match_string:
        context_phrase1 = (
            f" Find the stories about 《{query.match_string}》. Ignore any other stories "
            "in these articles. Also ignore anything that is not mentioned directly and "
            "explicitly in at least one of these articles. Select only stories  about "
            f"《{query.match_string}》 that are in the web pages I'm giving you."
        )
        context_phrase2 = (
            "Select only the relevant stories. Remember that our topic "
            f"is 《{query.match_string}》."
        )
    else:
        context_phrase1 = (
            "Find the most important stories in each of these posts.\n\n"
            "Create a **comprehensive report** aimed at **software practitioners**. "
            "Focus on the ten to twenty most compelling stories."
        )
        context_phrase2 = (
            "Select the most compelling stories. Combine them into one "
            f"or more consistent and accurate narrative about 《{query.match_string}》."
        )

    return f"""
## Your Task:

Read the blog post webpages referenced by each of these URLs.

{context_phrase1}


## Workflow & Requirements:

1. **Read blog posts**

Use your web-browsing capabilities to read each of these web pages. You must read the actual pages. Do not try to extrapolate or guess from the page titles.

2. **Extract & Organize Stories**

   - Identify and extract multiple **distinct stories, insights, or notable points** from each post.
   - Prove that you have actually read the web page contents by including some interesting direct quotes.

3. **Write the Report**

   - {context_phrase2}
   - For each selected story:
     - Create a one-paragraph **summary** of its key points.
     - **Immediately** follow the summary with the **title of the source blog post** and its **URL** in parentheses.
     - You must summarize only stories from the blog posts that I've shared with you.
     - You must follow each summary with a reference (title and URL) from the list that I shared above. No other URLs are acceptable.
   - Ensure the report is **structured and well-organized** for easy readability.

## Formatting Expectations:

- **Each story should be clearly delineated.**
- **Source titles and URLs should be placed immediately after each corresponding story in parentheses.**
- **Each story must have a source title and URL from the provided list.**
- **Use the exact format shown in the example below.**

## Example of Story Formatting:

<START OF SAMPLE DESIRED RESULT>

*Grok 3 Beta: xAI's Advanced AI for Reasoning and Problem-Solving*:

xAI's Grok 3 Beta, powered by a 100k H100 cluster, is designed for reasoning, mathematics, coding, and instruction-following. It uses large-scale reinforcement learning to enhance problem-solving, including backtracking and self-correction. With an Elo score of 1402 in the Chatbot Arena and strong benchmark results (AIME'25: 93.3%, GPQA: 84.6%), Grok 3 rivals top AI models. It introduces a "Think" mode for transparent reasoning and includes a cost-efficient variant, Grok 3 mini.

(Source: "Your Guide To AI: March 2025" - https://nathanbenaich.substack.com/p/your-guide-to-ai-march-2025)

<END OF SAMPLE DESIRED RESULT>
"""
