from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import build_instrument_context, get_language_instruction, get_news
from tradingagents.dataflows.config import get_config


def create_social_media_analyst(llm):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        asset_type = state.get("asset_type", "stock")
        instrument_context = build_instrument_context(state["company_of_interest"])

        tools = [
            get_news,
        ]

        if asset_type == "crypto":
            base_prompt = (
                "You are a crypto sentiment and social media analyst tasked with assessing community sentiment "
                "and social signals for a cryptocurrency over the past week. "
                "Use the get_news(query, start_date, end_date) tool to search for relevant discussions. "
                "Focus on: Twitter/X crypto influencer sentiment and trending narratives, Reddit communities "
                "(r/CryptoCurrency, r/Bitcoin, r/ethereum, and coin-specific subreddits), Telegram and Discord "
                "community tone, FUD vs. FOMO indicators, whale wallet activity mentions, developer activity "
                "and GitHub commit sentiment, and any viral narratives that could drive short-term price action. "
                "Identify whether community sentiment is broadly bullish, bearish, or uncertain, and explain the "
                "dominant narratives driving that sentiment. Provide specific, actionable insights to help traders "
                "interpret the social signal strength."
            )
        elif asset_type == "b3":
            base_prompt = (
                "You are a Brazilian market sentiment and social media analyst tasked with assessing retail and "
                "institutional sentiment for a B3-listed stock over the past week. "
                "Use the get_news(query, start_date, end_date) tool to search for relevant discussions. "
                "Focus on: Brazilian investor communities on Twitter/X (in Portuguese), Reddit r/investimentos, "
                "r/investimentos_br, and r/financaspessoais, stock forums on InfoMoney, Seu Dinheiro, and "
                "Suno Research, retail sentiment on platforms like Fundamentus and StatusInvest, analyst "
                "recommendations from BTG Pactual, XP Inc., Itaú BBA, and other Brazilian brokerages, "
                "and any viral narratives specific to Brazilian market dynamics (e.g. dividend expectations, "
                "SELIC sensitivity debates, government policy concerns). "
                "Note whether content discusses ON vs PN preference, foreign investor flow sentiment, or "
                "upcoming dividend/JCP payment expectations. "
                "Identify whether community sentiment is broadly bullish, bearish, or uncertain, and explain "
                "the dominant narratives. Provide actionable insights for traders in the Brazilian market."
            )
        else:
            base_prompt = (
                "You are a social media and company specific news researcher/analyst tasked with analyzing social media posts, recent company news, and public sentiment for a specific company over the past week. You will be given a company's name your objective is to write a comprehensive long report detailing your analysis, insights, and implications for traders and investors on this company's current state after looking at social media and what people are saying about that company, analyzing sentiment data of what people feel each day about the company, and looking at recent company news. Use the get_news(query, start_date, end_date) tool to search for company-specific news and social media discussions. Try to look at all sources possible from social media to sentiment to news. Provide specific, actionable insights with supporting evidence to help traders make informed decisions."
            )

        system_message = (
            base_prompt
            + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. {instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
