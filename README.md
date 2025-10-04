# CelesLedger

> [!warning] Working in progress  
> And would definitely take quite a long time to finish :)

# Introduction
This is a smart ledger app using LangGraph. 
It interprets and saves expenditure records; Provides highly customized responses and suggestions; Memorizes important traits of users and conversations.

# Guide

1. Use `git clone https://github.com/CelestriZeta/CelesLedger` to clone this project into your own device.

2. Enter your API key in .env file, exemplified in .env.example. 
- This project uses Deepseek as the LLM provider, you can change to other models by modifying the `llm` initialization arguments in /src/agent.py.

3. run `streamlit run .\src\main.py` to start the app.