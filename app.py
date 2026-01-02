from streamlit_ace import st_ace
import streamlit as st
import requests
import base64


# ----- CONFIG -----
GITHUB_USER = "wpzvqrs8"  # Replace with your GitHub username
GITHUB_REPO = "java_pro"      # Replace with your repo name
BRANCH = "main"                # Usually 'main' or 'master'


TOKEN = "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"

headers = {"Authorization": f"token {TOKEN}"}

# ---- FUNCTIONS ----
def get_java_files():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/git/trees/{BRANCH}?recursive=1"
    response = requests.get(url, headers=headers)
    data = response.json()
    files = [item['path'] for item in data['tree'] if item['path'].endswith(".java")]
    return files

def get_file_content(file_path):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{file_path}?ref={BRANCH}"
    response = requests.get(url, headers=headers)
    data = response.json()
    content = base64.b64decode(data['content']).decode('utf-8')
    sha = data['sha']
    return content, sha

def update_file(file_path, new_content, sha, message="Update via Streamlit"):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{file_path}"
    encoded_content = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
    payload = {
        "message": message,
        "content": encoded_content,
        "sha": sha,
        "branch": BRANCH
    }
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code, response.json()

# ---- STREAMLIT UI ----
st.title("📝 Java Repo Editor")

files = get_java_files()
if not files:
    st.warning("No Java files found.")
else:
    selected_file = st.sidebar.selectbox("Select a Java file to edit", files)

    content, sha = get_file_content(selected_file)
    edited_content = st.text_area(f"Editing {selected_file}", content, height=400)
    edited_content = st_ace(value=content, language='java', theme='monokai', height=500)
    if st.button("Save changes to GitHub"):
        status, result = update_file(selected_file, edited_content, sha)
        if status == 200 or status == 201:
            st.success("✅ File updated successfully on GitHub!")
        else:
            st.error(f"❌ Failed to update file: {result}")
