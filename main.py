import streamlit as st
import requests

# Function to extract repository contents from GitHub
def get_repo_contents(repo_url, token=None):
    repo_parts = repo_url.rstrip('/').split('/')
    if len(repo_parts) < 2:
        st.error("Invalid GitHub repository URL format.")
        return None
    
    owner, repo = repo_parts[-2], repo_parts[-1]
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    if token:
        headers['Authorization'] = f'token {token}'
    
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching repository contents: {response.status_code} - {response.json().get('message', '')}")
        return None

# Function to download content of a specific file
def get_file_content(file_url):
    print("file_url ":file_url)
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Error fetching file content: {response.status_code}")
        return "Unable to retrieve file content."

# Placeholder function for querying the Gemini API
def query_gemini(question, context):
    # Replace this with the actual API call to the Gemini service.
    response = {
        "answer": f"Simulated answer for '{question}' using the provided file content of length {len(context)}."
    }
    return response['answer']

# Streamlit UI setup
st.title("GitHub Repository Chatbot")
repo_url = st.text_input("Enter the GitHub Repository URL:")
token = st.text_input("Enter GitHub Token (if needed for private repositories):", type="password")
user_question = st.text_area("Ask a question about the repository (e.g., 'What is the architecture?', 'What does the file main.py do?'):")

if st.button("Submit"):
    if repo_url and user_question:
        with st.spinner("Fetching repository information..."):
            repo_contents = get_repo_contents(repo_url, token)
            if repo_contents:
                # Analyze the structure of the repository
                file_urls = {item['name']: item['download_url'] for item in repo_contents if item['type'] == 'file'}
                
                # Check if the user is asking about a specific file
                target_file_url = None
                for file_name in file_urls.keys():
                    if file_name.lower() in user_question.lower():
                        target_file_url = file_urls[file_name]
                        break
                
                if target_file_url:
                    # Fetch the content of the specific file
                    file_content = get_file_content(target_file_url)
                    context = file_content  # Use the content of the file as the context
                    st.write(f"File content (first 500 characters):\n\n{file_content[:500]}...")
                else:
                    st.warning("No specific file found in the question. Using README as context.")
                    context = "No specific file content available."

                # Use the content to query the Gemini API
                with st.spinner("Generating answer..."):
                    answer = query_gemini(user_question, context)
                    st.success("Answer:")
                    st.write(answer)
    else:
        st.warning("Please provide both a repository URL and a question.")
