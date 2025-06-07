import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    ServiceContext,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.groq import Groq
import warnings
warnings.filterwarnings('ignore')

class RAGSystem:
    def __init__(self):
        # Load .env file
        env_path = Path(__file__).parent / '.env'
        if not env_path.exists():
            raise FileNotFoundError(
                "'.env' file not found! Please create it in the project root with GROQ_API_KEY=your_key"
            )
        
        load_dotenv(env_path)
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found in .env file! Please add it as: GROQ_API_KEY=your_key"
            )
        
        # Configure settings
        Settings.llm = Groq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
        Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        Settings.node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
        
        self.query_engine = None

    def process_files_and_create_index(self, temp_folder_path):
        reader = SimpleDirectoryReader(input_files=[os.path.join(temp_folder_path, file) 
                                                  for file in os.listdir(temp_folder_path) 
                                                  if os.path.isfile(os.path.join(temp_folder_path, file))])
        documents = reader.load_data()
        nodes = Settings.node_parser.get_nodes_from_documents(documents, show_progress=True)
        vector_index = VectorStoreIndex.from_documents(documents, show_progress=True, node_parser=nodes)
        vector_index.storage_context.persist(persist_dir="./storage_mini")
        return vector_index

    def load_existing_index(self):
        storage_context = StorageContext.from_defaults(persist_dir="./storage_mini")
        index = load_index_from_storage(storage_context)
        self.query_engine = index.as_query_engine()

    def query(self, user_input):
        if self.query_engine is None:
            self.load_existing_index()
        return self.query_engine.query(user_input).response

if __name__ == "__main__":
    rag = RAGSystem()
    temp_folder_path = "temp"  # Set the correct path to the temp folder

    # Process files and create index
    vector_index = rag.process_files_and_create_index(temp_folder_path)

    # Get user input for the first prompt
    user_input = input("You: ")

    # Feed in user query
    resp = rag.query(user_input)
    print("Assistant:", resp)

    # Allow the user to ask follow-up questions or queries
    while True:
        user_query = input("You: ")  # Get user input for a query

        # Exit the loop if the user types 'quit'
        if user_query.lower() == 'quit':
            print("Exiting the conversation.")
            break

        # Feed in user query
        resp = rag.query(user_query)
        print("Assistant:", resp)
