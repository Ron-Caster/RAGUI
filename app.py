import streamlit as st
import os
import shutil
from pathlib import Path
from rag_test import RAGSystem

st.set_page_config(
    page_title="WinWiz Chat",
    page_icon="🤖",
    layout="wide"
)

def ensure_temp_folder():
    """Ensure temp folder exists and return its path"""
    temp_dir = Path(__file__).parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir

def get_file_size(filepath):
    """Get human readable file size"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"

def initialize_session_state():
    if "rag" not in st.session_state:
        try:
            st.session_state.rag = RAGSystem()
        except (FileNotFoundError, ValueError) as e:
            st.error(f"Configuration Error: {str(e)}")
            st.stop()
    if "messages" not in st.session_state:
        st.session_state.messages = []

def process_files():
    temp_folder = "temp"
    if os.path.exists(temp_folder) and os.listdir(temp_folder):
        with st.spinner("Processing files and creating index..."):
            st.session_state.rag.process_files_and_create_index(temp_folder)
        st.success("Files processed successfully!")
    else:
        st.error("No files found in the temp folder!")

def file_manager_ui():
    """File management interface"""
    temp_dir = ensure_temp_folder()
    
    # File upload section
    uploaded_files = st.file_uploader(
        "Upload documents",
        accept_multiple_files=True,
        type=['pdf', 'txt', 'doc', 'docx', 'csv'],
        help="Supported formats: PDF, TXT, DOC, DOCX, CSV"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Save uploaded file
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded: {uploaded_file.name}")

    # File listing section
    st.markdown("### Current Files")
    files = list(temp_dir.glob('*'))
    
    if not files:
        st.info("No files in temp folder. Please upload some documents.")
        return
    
    # Create a table of files with actions
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        st.markdown("**Filename**")
    with col2:
        st.markdown("**Size**")
    with col3:
        st.markdown("**Last Modified**")
    with col4:
        st.markdown("**Action**")
    
    for file in files:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            st.text(file.name)
        with col2:
            st.text(get_file_size(file))
        with col3:
            modified_time = os.path.getmtime(file)
            st.text(f"{Path(file).stat().st_mtime:.0f}")
        with col4:
            if st.button("🗑️", key=f"del_{file.name}", help=f"Delete {file.name}"):
                try:
                    os.remove(file)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting file: {e}")

def main():
    initialize_session_state()

    st.title("WinWiz Chat UI 🤖")
    
    with st.sidebar:
        st.header("Document Management")
        
        # Process Files button directly under Document Management
        if st.button("Process Files", key="process_files", use_container_width=True):
            process_files()
        
        st.markdown("---")
        
        # Simplified tab structure with just File Manager and Help
        tabs = st.tabs(["File Manager", "Help"])
        
        with tabs[0]:
            file_manager_ui()
                
        with tabs[1]:
            st.markdown("""
            ### Instructions
            1. Use the **File Manager** tab to upload your documents
            2. Click the **Process Files** button above
            3. Start chatting in the main window!
            
            ### Supported Formats
            - PDF documents (.pdf)
            - Text files (.txt)
            - Word documents (.doc, .docx)
            - CSV files (.csv)
            """)

    # Chat interface
    if not os.listdir(ensure_temp_folder()):
        st.warning("Please upload some documents before starting the chat.")
        return

    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask something about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.rag.query(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
