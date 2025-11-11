from sqlmodel import SQLModel, Field
from pgvector.sqlalchemy import Vector
from typing import Optional, List

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    
    # Nutritional Info
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    
    # Recipe Text (for the LLM)
    ingredients: str
    steps: str
    
    # The "AI" vector representation
    # The 'dim=384' MUST match the model we are using (all-MiniLM-L6-v2)
    embedding: List[float] = Field(sa_column=Vector(dim=384))
