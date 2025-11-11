# 🥗 FitPantry: The AI Nutritionist & Meal Planner

**FitPantry** is a smart meal planning application that acts as your personal AI nutritionist. It solves the daily problem of "What should I eat?" by generating custom, healthy meal plans that perfectly match your **calorie and macronutrient goals**, using only the ingredients you **already have in your pantry**.

This project is a complete, full-stack **Retrieval-Augmented Generation (RAG)** system built from scratch to provide a "zero-waste" solution to healthy eating.



## ✨ Features

* **AI-Powered Meal Plans:** Generates full-day (Breakfast, Lunch, Dinner) meal plans that hit your specific calorie and protein targets.
* **Digital Pantry:** Easily track the ingredients you have at home to minimize food waste.
* **Nutritional Goal Setting:** Set custom daily targets for calories, protein, carbs, and fat.
* **Smart Recipe Matching:** Uses vector search to find recipes that match your pantry, not just keywords.
* **LLM "Puzzle Solver":** Uses a Large Language Model to intelligently "solve" your daily nutritional puzzle, mixing and matching recipes to get as close as possible to your goals.
* **100% Free & Open-Source:** Built entirely on a modern stack with generous free tiers.

---

## 🚀 The RAG Architecture

This project is a complete RAG system designed for a specific "puzzle-solving" task.

1.  **Data Ingestion (One-Time Script):**
    * `load_data.py` reads 50,000+ recipes with full nutritional info from the **Food.com Kaggle Dataset**.
    * A **Hugging Face Sentence Transformer** (`all-MiniLM-L6-v2`) converts each recipe's name and ingredients into a 384-dimension vector.
    * The recipes (with nutritional data and vectors) are loaded into a **Supabase PostgreSQL** database with the `pgvector` extension.

2.  **Live Query (The RAG Pipeline):**
    * A user sets their goals (e.g., 1800 cal) and pantry (e.g., chicken, spinach) in the **Next.js** frontend.
    * The **FastAPI** backend embeds the user's pantry list into a vector.
    * FastAPI queries the **Supabase** vector database to "Retrieve" the 20 most semantically similar recipes.
    * These 20 recipes (the "Context," complete with nutritional info) are "Augmented" into a complex prompt for an **LLM** (e.g., `Gemma 2B`).
    * The LLM is instructed to "Generate" a full-day meal plan that hits the user's targets, outputting a structured JSON response.



---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | **Next.js (React)** | Interactive UI, goal setting, pantry management. |
| **Backend** | **FastAPI (Python)** | The RAG API, user management, and AI logic. |
| **Database** | **Supabase (PostgreSQL)** | Primary database for users, pantries, and recipes. |
| **Vector Search** | **`pgvector`** | For efficient semantic similarity search on recipes. |
| **Data Source** | **Kaggle Datasets** | Source of all recipe and nutritional data. |
| **AI (Embedding)** | **Hugging Face `sentence-transformers`** | To create vectors for recipes and pantries. |
| **AI (Generation)**| **Hugging Face Inference API** | To run a free, open-source LLM for meal planning. |
| **Deployment** | **Vercel** (Frontend) & **Render** (Backend) | For a 100% free deployment. |

---

## 🏁 Getting Started

You can get this entire project running for $0. It is broken into two main parts: the `fitpantry_dataloader` and the `fitpantry_app`.

### Part 1: Load The Data (The "Smart" Database)

First, you must populate your vector database with recipes.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR-USERNAME/fitpantry.git](https://github.com/YOUR-USERNAME/fitpantry.git)
    cd fitpantry/fitpantry_dataloader
    ```

2.  **Set up Supabase:**
    * Create a free account on [Supabase.com](https://supabase.com).
    * Create a new project (e.g., "fitpantry").
    * Go to the **SQL Editor** and run this query to enable vector search:
        ```sql
        create extension if not exists vector;
        ```
    * Go to **Project Settings** > **Database** and copy your `psql` connection string.

3.  **Install & Configure:**
    * Create a `.env` file in the `fitpantry_dataloader` folder and add your connection string:
        ```env
        DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres"
        ```
    * Create a virtual environment and install the requirements:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        pip install -r requirements.txt
        ```

4.  **Download the Data:**
    * Download the **"Food.com Recipes and Interactions"** dataset from Kaggle.
    * Place the `RAW_recipes.csv` file inside the `fitpantry_dataloader/data/` folder.

5.  **Run the Pipeline:**
    * This script will create the tables, download the embedding model, and load 50,000+ recipes into your database. This will take several minutes.
    ```bash
    python load_data.py
    ```
    Your "smart" nutritional database is now ready!

### Part 2: Run the Application (Coming Soon)

*(This section is a placeholder for when you build the API and Frontend)*

1.  **Configure the Backend:**
    * Navigate to the `fitpantry_app/backend` folder.
    * Create a `.env` file with your `DATABASE_URL` and a `HF_TOKEN` from Hugging Face.
    * Install requirements and run: `uvicorn main:app --reload`

2.  **Configure the Frontend:**
    * Navigate to the `fitpantry_app/frontend` folder.
    * Create a `.env.local` file pointing to your FastAPI backend URL.
    * Install dependencies and run: `npm run dev`

---

## 🤝 How to Contribute

Contributions are welcome! This project is for learning and building a useful, open-source tool.

1.  **Fork the repository.**
2.  **Create a new feature branch:** `git checkout -b feat/YourAmazingFeature`
3.  **Commit your changes:** `git commit -m 'feat: Add YourAmazingFeature'`
4.  **Push to the branch:** `git push origin feat/YourAmazingFeature`
5.  **Open a Pull Request.**

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
