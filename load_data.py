import sys
import pandas as pd
from sqlmodel import create_engine, SQLModel, Session, text
from core.config import settings
from models import Recipe
from sentence_transformers import SentenceTransformer
import ast  # To safely evaluate string-lists (like ingredients)
from tqdm import tqdm # For progress bars

# --- Configuration ---
DATA_FILE_PATH = "data/RAW_recipes.csv"
SAMPLE_SIZE = 50000  # Start with 50k recipes. You can increase this later!
BATCH_SIZE = 1000     # Load 1000 recipes at a time
EMBEDDING_MODEL = 'all-MiniLM-L6-v2' # 384 dimensions, fast and free

def initialize_database(engine):
    """Ensures the pgvector extension is enabled and creates tables."""
    print("Initializing database...")
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        SQLModel.metadata.create_all(engine)
        print("Database initialized and pgvector extension is active.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Please ensure you have run 'create extension if not exists vector;' in your Supabase SQL Editor.")
        sys.exit(1)

def clean_text(text_list_str):
    """Safely parses and joins string representations of lists."""
    try:
        items = ast.literal_eval(text_list_str)
        return ", ".join(items) if isinstance(items, list) else text_list_str
    except (ValueError, SyntaxError):
        return text_list_str # Return as-is if it's not a list

def load_and_clean_data():
    """Loads the CSV, cleans it, and samples it."""
    print(f"Loading data from {DATA_FILE_PATH}...")
    try:
        df = pd.read_csv(DATA_FILE_PATH)
    except FileNotFoundError:
        print(f"ERROR: Data file not found at {DATA_FILE_PATH}")
        print("Please download 'RAW_recipes.csv' from Kaggle and place it in the 'data' folder.")
        sys.exit(1)
        
    print(f"Loaded {len(df)} total songs. Cleaning and processing...")
    
    # 1. Select only the columns we need
    columns_to_keep = ['name', 'nutrition', 'steps', 'ingredients']
    df = df[columns_to_keep]
    
    # 2. Parse the 'nutrition' column
    # It's a string list: [calories, fat(PDV), sugar(PDV), sodium(PDV), protein(PDV), sat fat(PDV), carbs(PDV)]
    # We will assume the PDV values are actually grams, as this is common in messy datasets.
    try:
        nutrition_df = df['nutrition'].apply(lambda x: ast.literal_eval(x))
        df['calories'] = nutrition_df.apply(lambda x: x[0])
        df['fat_g'] = nutrition_df.apply(lambda x: x[1])
        df['protein_g'] = nutrition_df.apply(lambda x: x[4])
        df['carbs_g'] = nutrition_df.apply(lambda x: x[6])
    except Exception as e:
        print(f"Error parsing nutrition column: {e}")
        print("Skipping bad rows.")
        df = df.dropna(subset=['nutrition'])
        nutrition_df = df['nutrition'].apply(lambda x: ast.literal_eval(x))
        df['calories'] = nutrition_df.apply(lambda x: x[0])
        df['fat_g'] = nutrition_df.apply(lambda x: x[1])
        df['protein_g'] = nutrition_df.apply(lambda x: x[4])
        df['carbs_g'] = nutrition_df.apply(lambda x: x[6])

    # 3. Clean 'steps' and 'ingredients' columns
    df['steps'] = df['steps'].apply(clean_text)
    df['ingredients'] = df['ingredients'].apply(clean_text)
    
    # 4. Drop rows with missing or nonsensical data
    df = df.dropna(subset=['name', 'calories', 'protein_g', 'fat_g', 'carbs_g', 'steps', 'ingredients'])
    df = df[df['calories'] > 0] # Remove recipes with 0 calories
    
    # 5. Take a random sample
    if len(df) > SAMPLE_SIZE:
        df = df.sample(n=SAMPLE_SIZE, random_state=42)
        
    print(f"Cleaned and sampled data. Total recipes to load: {len(df)}")
    return df

def create_embeddings_and_load(df, engine, model):
    """Generates embeddings and loads recipes into the DB in batches."""
    print(f"Starting to embed and load {len(df)} recipes in batches of {BATCH_SIZE}...")
    
    with Session(engine) as session:
        for i in tqdm(range(0, len(df), BATCH_SIZE), desc="Loading batches"):
            batch_df = df.iloc[i : i + BATCH_SIZE]
            
            # 1. Create the text to embed
            # We'll embed a combo of the name and ingredients for good search results
            texts_to_embed = (batch_df['name'] + ". Ingredients: " + batch_df['ingredients']).tolist()
            
            # 2. Generate embeddings (the "AI" part)
            embeddings = model.encode(texts_to_embed, show_progress_bar=False)
            
            # 3. Create model objects to add
            objects_to_add = []
            for idx, (row, embedding) in enumerate(zip(batch_df.to_dict('records'), embeddings)):
                objects_to_add.append(
                    Recipe(
                        name=row['name'],
                        calories=row['calories'],
                        protein_g=row['protein_g'],
                        fat_g=row['fat_g'],
                        carbs_g=row['carbs_g'],
                        ingredients=row['ingredients'],
                        steps=row['steps'],
                        embedding=embedding.tolist() # Convert numpy array to list
                    )
                )
            
            # 4. Add and commit to the database
            session.add_all(objects_to_add)
            session.commit()
            
    print("Data loading complete!")

def main():
    try:
        # Connect to the database
        engine = create_engine(settings.DATABASE_URL)
        
        # 1. Initialize DB and pgvector extension
        initialize_database(engine)
        
        # 2. Load the (free) AI embedding model
        print(f"Loading embedding model: '{EMBEDDING_MODEL}'...")
        # This will download the model once and cache it
        model = SentenceTransformer(EMBEDDING_MODEL)
        print("Embedding model loaded.")
        
        # 3. Load and clean data from CSV
        df = load_and_clean_data()
        
        # 4. Embed recipes and load into the database
        create_embeddings_and_load(df, engine, model)
        
        print("\n--- SUCCESSFULLY POPULATED YOUR NUTRITIONAL DATABASE ---")
        print(f"Your Supabase DB now contains {len(df)} recipes, each with a 384-dimension vector.")
        print("You are now ready for Part 2: Building the RAG API.")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your DATABASE_URL in the .env file and ensure your Supabase project is active.")

if __name__ == "__main__":
    main()
