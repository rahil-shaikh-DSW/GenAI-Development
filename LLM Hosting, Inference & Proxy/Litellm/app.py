# app.py
import streamlit as st
from inference_module import run_inference

def main():
    st.title("Multi-Provider LLM Inference Demo")
    
    # Provider and model selection
    providers = {
        "Gemini": ["gemini-2.0-flash"],
        "Groq": ["llama-70b-4096", "mixtral-8x7b-32768"],
        "Ollama": ["llama2", "mistral"],
        "xAI (Grok)": ["grok"]
    }
    
    with st.form(key='chat_form'):
        prompt = st.text_area("Enter your prompt:", height=100)
        provider = st.selectbox("Select Provider", list(providers.keys()))
        model = st.selectbox("Select Model", providers[provider])
        api_key = st.text_input(f"{provider} API Key (optional if set in env)", type="password")
        submit_button = st.form_submit_button(label='Send')
    
    if submit_button and prompt:
        with st.spinner("Processing..."):
            provider_key = "xai" if provider == "xAI (Grok)" else provider.lower()
            result = run_inference(prompt, model=model, provider=provider_key, api_key=api_key)
            
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success("Response generated successfully!")
                st.write("**Response:**", result["response"])
                st.write("**Provider:**", result["provider"])
                st.write("**Model:**", result["model"])
                st.write("**Query Tokens:**", result["query_tokens"])
                st.write("**Response Tokens:**", result["response_tokens"])
                st.write("**Total Tokens:**", result["total_tokens"])
                st.write("**Response Time:**", f"{result['response_time']:.2f} seconds")

if __name__ == "__main__":
    main()