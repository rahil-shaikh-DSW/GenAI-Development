import streamlit as st
from groq import Groq
from langfuse import Langfuse
from dotenv import load_dotenv
import uuid
import os
import time
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize Langfuse
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

# Constants for scoring and evaluation
SCORE_TYPES = {
    "relevance": "How relevant the response is to the query (1-10)",
    "accuracy": "Factual accuracy of the response (1-10)",
    "completeness": "How completely the response addresses the query (1-10)",
    "helpfulness": "Overall helpfulness to the user (1-10)",
    "latency_score": "Score based on response time (1-10, auto-calculated)"
}

# Session state initialization for user session tracking
if "user_session_id" not in st.session_state:
    st.session_state.user_session_id = str(uuid.uuid4())

def calculate_latency_score(total_duration_ns):
    """Calculate a score for response latency (higher is better)"""
    # Convert ns to seconds
    duration_sec = total_duration_ns / 1e9
    
    # Simple scoring logic - can be customized
    if duration_sec < 1.0:
        return 10
    elif duration_sec < 2.0:
        return 9
    elif duration_sec < 3.0:
        return 8
    elif duration_sec < 4.0:
        return 7
    elif duration_sec < 5.0:
        return 6
    elif duration_sec < 7.0:
        return 5
    elif duration_sec < 10.0:
        return 4
    elif duration_sec < 15.0:
        return 3
    elif duration_sec < 20.0:
        return 2
    else:
        return 1

def log_to_dataset(prompt, response, trace_id):
    """Log interactions to a Langfuse dataset for future training or evaluation"""
    try:
        # First, ensure the dataset exists by creating it if it doesn't
        try:
            # Check if dataset exists by attempting to fetch it (not directly supported, so we create it)
            langfuse.create_dataset(
                name="groq_interactions",
                description="Dataset for storing Groq interaction logs"  # Optional
            )
        except Exception as e:
            # If the dataset already exists, Langfuse might raise an error (e.g., 409 Conflict).
            # We can safely ignore this since it means the dataset is already there.
            if "already exists" not in str(e).lower():
                st.error(f"Failed to create dataset: {str(e)}")
                return None

        # Now create the dataset item
        dataset_item = langfuse.create_dataset_item(
            dataset_name="groq_interactions",
            input=prompt,
            expected_output=None,  # We don't have a ground truth
            metadata={
                "timestamp": datetime.now().isoformat(),
                "model": "llama3-70b-8192",
                "trace_id": trace_id
            }
        )
        return dataset_item.id
    except Exception as e:
        st.error(f"Failed to log to dataset: {str(e)}")
        return None
def get_pi_response(prompt, user_id=None, parent_trace_id=None):
    """Enhanced function to get responses from Groq with comprehensive Langfuse tracking"""
    # Generate unique trace ID
    trace_id = str(uuid.uuid4())
    
    # Create Langfuse trace with user info and parent trace if available
    trace_metadata = {
        "user_id": user_id,
        "app": "streamlit_pi_explainer",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "prompt_length": len(prompt)
    }
    
    # Create trace with parent if needed (for conversation threading)
    if parent_trace_id:
        langfuse_trace = langfuse.trace(
            id=trace_id, 
            name="groq_interaction", 
            metadata=trace_metadata,
            parent_trace_id=parent_trace_id
        )
    else:
        langfuse_trace = langfuse.trace(
            id=trace_id, 
            name="groq_interaction", 
            metadata=trace_metadata
        )
    
    # Manually start the span for the overall process
    process_span = langfuse_trace.span(
        name="complete_response_process"
    )
    
    try:
        # Create an event for receiving the user query
        langfuse_trace.event(
            name="user_query_received",
            metadata={"prompt": prompt}
        )
        
        # Measure start time for total duration
        start_time = time.time_ns()
        
        # Manually start a span for prompt processing
        prompt_processing_span = process_span.span(
            name="prompt_processing"
        )
        # Simulate prompt processing time (if there was any pre-processing)
        time.sleep(0.01)  # 10ms artificial delay
        
        # Log prompt processing event
        langfuse_trace.event(
            name="prompt_processed",
            metadata={"processed_prompt": prompt}
        )
        # Manually end the prompt processing span
        prompt_processing_span.end()
        
        # Create a generation for the actual LLM call
        groq_generation = langfuse_trace.generation(
            name="groq_llama3_generation",
            model="llama3-70b-8192",
            model_parameters={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 4000
            },
            input=prompt,
            metadata={
                "provider": "groq",
                "request_timestamp": datetime.now().isoformat()
            }
        )
        
        # Measure LLM call duration
        llm_call_start = time.time_ns()
        
        # Manually start a span for the API call
        api_call_span = process_span.span(
            name="groq_api_call"
        )
        
        # Get response from Groq
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9,
            stream=False
        )
        
        # Manually end the API call span
        api_call_span.end()
        
        # Calculate LLM call duration
        llm_call_duration = time.time_ns() - llm_call_start
        
        # Get response text and usage
        output_text = response.choices[0].message.content
        
        # Extract usage data
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0
        }
        
        # Calculate total duration
        total_duration = time.time_ns() - start_time
        
        # Create an event for token usage tracking
        langfuse_trace.event(
            name="token_usage",
            metadata=usage
        )
        
        # Calculate a latency score
        latency_score = calculate_latency_score(total_duration)
        
        # End generation tracking with all metrics
        groq_generation.end(
            output=output_text,
            usage={
                "input": usage["prompt_tokens"],
                "output": usage["completion_tokens"],
                "total": usage["total_tokens"]
            },
            metadata={
                "total_duration_ns": total_duration,
                "llm_call_duration_ns": llm_call_duration,
                "latency_score": latency_score,
                "done": True,
                "done_reason": response.choices[0].finish_reason,
                "response_timestamp": datetime.now().isoformat()
            }
        )
        
        # Create an automatic score for latency
        langfuse.score(
            trace_id=trace_id,
            name="latency_score",
            value=latency_score,
            comment="Automatically calculated based on response time"
        )
        
        # Log the interaction to a dataset for future analysis
        dataset_item_id = log_to_dataset(prompt, output_text, trace_id)
        
        # Update trace with final information
        langfuse_trace.update(
            name="completed_groq_interaction",
            input=prompt,
            output=output_text,
            metadata={
                "total_duration_ns": total_duration,
                "total_tokens": usage["total_tokens"],
                "dataset_item_id": dataset_item_id
            }
        )
        
        # Manually end the process span
        process_span.end()
        
        # Debug info for Streamlit
        debug_info = {
            "Trace ID": trace_id,
            "Parent Trace ID": parent_trace_id,
            "User ID": user_id,
            "Total Duration (sec)": total_duration / 1e9,
            "LLM Call Duration (sec)": llm_call_duration / 1e9,
            "Prompt Tokens": usage["prompt_tokens"],
            "Completion Tokens": usage["completion_tokens"],
            "Total Tokens": usage["total_tokens"],
            "Latency Score": latency_score,
            "Dataset Item ID": dataset_item_id
        }
        
        return output_text, debug_info, trace_id
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        process_span.end(status="error", metadata={"error": str(e)})
        
        if 'groq_generation' in locals():
            groq_generation.end(
                output=error_msg,
                status="error",
                metadata={"error": str(e)}
            )
            
        # Log the error as an event
        langfuse_trace.event(
            name="error",
            metadata={"error_message": str(e)}
        )
        
        langfuse_trace.update(
            input=prompt, 
            output=error_msg,
            metadata={"error": str(e)}
        )
        
        return error_msg, {"Trace ID": trace_id, "Error": str(e)}, trace_id

def user_feedback(trace_id, score_type, score_value, comment=""):
    """Allow users to provide feedback on responses"""
    try:
        # Use the score method with direct parameters instead of CreateScoreRequest
        langfuse.score(
            trace_id=trace_id,
            name=score_type,
            value=float(score_value),
            comment=comment
        )
        return True
    except Exception as e:
        st.error(f"Failed to submit feedback: {str(e)}")
        return False

# Streamlit app with enhanced features
def main():
    st.title("Pi Explainer with Groq Llama 3.1")
    
    # Check environment variables
    if not os.getenv("GROQ_API_KEY") or not os.getenv("LANGFUSE_PUBLIC_KEY"):
        st.error("Missing API keys. Check your .env file.")
        st.write(f"GROQ_API_KEY: {'Set' if os.getenv('GROQ_API_KEY') else 'Not set'}")
        st.write(f"LANGFUSE_PUBLIC_KEY: {'Set' if os.getenv('LANGFUSE_PUBLIC_KEY') else 'Not set'}")
        return
    
    # Sidebar for app options and user info
    with st.sidebar:
        st.subheader("Session Information")
        st.write(f"Session ID: {st.session_state.user_session_id}")
        
        st.subheader("Model Settings")
        # These don't actually change anything in this demo but show how you could
        # expose model parameters and track them in Langfuse
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
        max_tokens = st.slider("Max Tokens", 500, 8000, 4000)
        
        st.subheader("Debug Options")
        show_debug = st.checkbox("Show Debug Info", value=True)
        
        st.markdown("---")
        st.markdown("#### View in Langfuse")
        st.markdown("[Open Langfuse Dashboard](https://cloud.langfuse.com)")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "trace_ids" not in st.session_state:
        st.session_state.trace_ids = []
    
    if "parent_trace_id" not in st.session_state:
        st.session_state.parent_trace_id = None
    
    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and i > 0:
                # Create columns for feedback buttons
                feedback_cols = st.columns(len(SCORE_TYPES))
                
                # Get the trace ID for this message
                if i // 2 < len(st.session_state.trace_ids):
                    current_trace_id = st.session_state.trace_ids[i // 2]
                    
                    # Add feedback options for assistant messages
                    for col_idx, (score_type, description) in enumerate(SCORE_TYPES.items()):
                        with feedback_cols[col_idx]:
                            # Don't show latency score feedback since it's automatic
                            if score_type != "latency_score":
                                st.caption(f"{score_type.capitalize()}")
                                score = st.select_slider(
                                    f"Rate {score_type}",
                                    options=list(range(1, 11)),
                                    value=5,
                                    key=f"rating_{score_type}_{i}",
                                    label_visibility="collapsed"
                                )
                                if st.button("Submit", key=f"submit_{score_type}_{i}"):
                                    success = user_feedback(
                                        current_trace_id, 
                                        score_type, 
                                        score,
                                        f"User feedback on {score_type}"
                                    )
                                    if success:
                                        st.success(f"{score_type.capitalize()} feedback submitted!")
            
            if "debug" in message and show_debug:
                with st.expander("Debug Info"):
                    st.json(message["debug"])
    
    # User input
    prompt = st.chat_input("Ask about pi or anything else...")
    
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Pass user ID and parent trace ID for conversation threading
                response, debug_info, trace_id = get_pi_response(
                    prompt, 
                    user_id=st.session_state.user_session_id,
                    parent_trace_id=st.session_state.parent_trace_id
                )
                
                # Store the trace ID for this response
                st.session_state.trace_ids.append(trace_id)
                
                # Update the parent trace ID for the next interaction
                st.session_state.parent_trace_id = trace_id
                
                # Display the response
                st.markdown(response)
                
                if show_debug:
                    with st.expander("Debug Info"):
                        st.json(debug_info)
                
                # Store in session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "debug": debug_info
                })

if __name__ == "__main__":
    main()
# total_duration=47109953700 
# load_duration=38236200 
# prompt_eval_count=28 
# prompt_eval_duration=97000000 
# eval_count=390 eval_duration=46974000000 