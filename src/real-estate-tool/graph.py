import prompts
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from models import OutputState, PropertyAdjectives, State, UserInput

load_dotenv()


llm = ChatOpenAI(model="gpt-4o", temperature=0.6)
llm_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
translator = ChatOpenAI(model="gpt-4o", temperature=0.0).with_structured_output(
    OutputState
)


def translate_to_portuguese(state: State):
    original_output = OutputState(**state)
    messages = ChatPromptTemplate(
        [
            ("system", prompts.translator_system_prompt),
            ("user", original_output.to_str()),
        ]
    ).format_messages()
    translated_output = translator.invoke(messages)
    return translated_output.dict()


def should_translate(state: State):
    language = state["user_input"].language
    if language == "pt":
        return "translate_to_portuguese"
    return END


def generate_title(state: State):
    user_title = state["user_input"].title
    bedrooms = state["user_input"].property_features.bedrooms
    neighborhood = state["user_input"].location_details.neighborhood
    city = state["user_input"].location_details.city

    title_generator_prompt_template = ChatPromptTemplate(
        [
            ("system", prompts.title_generator_system_prompt),
            ("human", prompts.title_generator_user_prompt),
        ]
    )

    messages = title_generator_prompt_template.format_messages(
        title=user_title,
        bedrooms=bedrooms,
        neighborhood=neighborhood,
        city=city,
    )
    return {"title": llm_mini.invoke(messages).content}


def generate_adjectives(state: State):
    adjective_generator = llm.with_structured_output(PropertyAdjectives)
    user_input = state["user_input"]
    messages = ChatPromptTemplate(
        [
            ("system", prompts.adjective_generator_system_prompt),
            ("human", user_input.build_features_paragraph()),
        ]
    ).format_messages()
    response = adjective_generator.invoke(messages)

    return {"adjectives": response}


def generate_full_description(state: State):
    messages = ChatPromptTemplate(
        [
            ("system", prompts.full_description_system_prompt),
            ("human", prompts.generate_full_description_user_prompt(state)),
        ]
    ).format_messages()
    full_description = llm.invoke(messages).content
    return {"full_description": full_description}


def generate_neigborhood_summary(state: State):
    location_details = state["user_input"].location_details
    neighborhood = f"{location_details.neighborhood}, {location_details.city}"
    messages = ChatPromptTemplate(
        [
            ("system", prompts.neighborhood_summary_generator_system_prompt),
            ("human", neighborhood),
        ]
    ).format_messages()
    neighborhood_summary = llm.invoke(messages).content

    return {"neighborhood_summary": neighborhood_summary}


def generate_headline(state: State):
    features = state["adjectives"].all_adjectives_list
    title = state["title"]
    messages = ChatPromptTemplate(
        [
            ("system", prompts.headline_system_prompt),
            ("human", prompts.headline_user_prompt),
        ]
    ).format_messages(title=title, features=features)
    headline = llm_mini.invoke(messages).content

    return {"headline": headline}


def generate_meta_description(state: State):
    messages = ChatPromptTemplate(
        [
            ("system", prompts.meta_description_system_prompt),
            ("human", prompts.generate_full_description_user_prompt(state)),
        ]
    ).format_messages()
    meta_description = llm.invoke(messages).content
    return {"meta_description": meta_description}


def add_key_features(state: State):
    key_features = state["user_input"].key_features_list
    return {"key_features_list": key_features}


def add_call_to_action(state: State):
    city = state["user_input"].location_details.city
    return {
        "call_to_action": f"Don’t miss this opportunity—schedule your viewing today and discover your new home in {city}."
    }


def invoke_graph(user_input: UserInput) -> OutputState:
    builder = StateGraph(State)
    builder.add_node(generate_title)
    builder.add_node(generate_adjectives)
    builder.add_node(generate_full_description)
    builder.add_node(generate_meta_description)
    builder.add_node(generate_neigborhood_summary)
    builder.add_node(generate_headline)
    builder.add_node(add_key_features)
    builder.add_node(add_call_to_action)
    builder.add_node(translate_to_portuguese)

    builder.add_edge(START, "generate_title")
    builder.add_edge("generate_title", "generate_adjectives")
    builder.add_edge("generate_adjectives", "generate_neigborhood_summary")
    builder.add_edge("generate_neigborhood_summary", "generate_headline")
    builder.add_edge("generate_headline", "generate_full_description")
    builder.add_edge("generate_full_description", "generate_meta_description")
    builder.add_edge("generate_meta_description", "add_key_features")
    builder.add_edge("add_key_features", "add_call_to_action")
    builder.add_conditional_edges("add_call_to_action", should_translate)
    builder.add_edge("translate_to_portuguese", END)

    graph = builder.compile()

    # input_state = {
    #     "user_input": UserInput.from_dict(
    #         {
    #             "title": "T3 apartment in Madrid",
    #             "features": {
    #                 "bedrooms": 1,
    #                 "bathrooms": 1,
    #                 "area_sqm": 35,
    #                 "year_built": 2000,
    #                 "balcony": False,
    #                 "parking": False,
    #                 "elevator": True,
    #                 "floor": 3,
    #             },
    #             "location": {
    #                 "city": "Madrid",
    #                 "neighborhood": "Lavapies",
    #             },
    #             "language": "pt",
    #             "price": 5000,
    #             "listing_type": "rent",
    #         }
    #     )
    # }
    result = graph.invoke({"user_input": user_input})
    output_state = OutputState(**result)
    return output_state
