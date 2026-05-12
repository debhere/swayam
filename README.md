# Swayam
A RAG based chatbot to retrieve Life Insurance Corporation of India (LIC) insurance product information. This is v1.0 of the project which is done with gradio implementation.

## Authors

- [@debhere](https://www.github.com/debhere)

## Run Locally

Clone the repository (main branch)

```bash
git clone https://github.com/debhere/swayam.git

```
Package management is done using uv - instructions below are given as per windows, visit uv [website](https://docs.astral.sh/uv/) for additional details and installation steps.


If already installed, see if you are on the latest version.

```bash
uv self update
```

Now simply run...

```bash
uv sync
```

Verify if you are using python version 3.11 and you should see a .venv folder.

Next step - Cruicial but a personal choice. I am using OPENAI API for my LLM calls, you can visit https://platform.openai.com/ for your api-key set up and billings. As you see, OPENAI API is a paid service and the minimum payment is of $5. However, I don't think the v1.0 of this project will ever breach that limit. You may also choose other provides like Claude from Anthropic or Gemini from Google.

Either way, you need to create a .env file and put your api-key there, and save like this:

```bash
OPENAI_API_KEY=xxxx
ANTHROPIC_API_KEY=xxxx
GOOGLE_API_KEY=xxxx
```

To run the application, open your terminal and run the below command. It will launch the gradio app at your local. 

NOTE: cloud deployment is not done in this version but you are free to make your changes.

```bash

uv run python app.py

```

That's It! You are good to go now.


## Swayam Modules

Although I named this as modules but this does not necessarily mean Python modules. Essentially, we have 3 distinct compartments:

 - scripts
 - src
 - utils 

 ### scripts

scripts contains 2 python files which are in a way pre-requisites for this app to run:

- scraper.py: It downloads the insurance policy documents from the LIC website.
- build_kbase.py: It cleans and converts the insurance pdf documents into json files with proper pagination and metadata in place. This is nothing but the knowledge-base.

### src

src contains the main meat of this app i.e., vector-store creation and RAG pipeline.

- vector\store.py: It creates the vector-store from the knowledge-base.
- pipeline\rag_pipeline.py: This is the RAG pipeline. For every user query, it retrieves the context from the vector-store if available and sends it with the system prompt. Thereafter LLM response is also received and rendered on to thr gradio app.

### utils

As the name suggests, this is the utility module in swayam which are utilized in all other modules.

- config.py: It contains the configurations, specifically the constants.
- exception.py: swayam's custom exception logic.
- logger.py: logging for execution flow.

At Last,

app.py: This is the gradio front-end chat interface that gets the user query and sends it to the callback function in rag_pipeline.


## Support

Please message on [![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/debmalyamondal). Happy to have any suggestions, Thank you.!
