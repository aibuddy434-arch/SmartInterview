"""
Migration script to add question_text and question_type columns to responses table
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Database URL with correct credentials
DATABASE_URL = "mysql+aiomysql://root:Password@localhost:3306/ai_interview"

async def add_columns():
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        # Check if columns exist first
        result = await conn.execute(text("SHOW COLUMNS FROM responses LIKE 'question_text'"))
        if not result.fetchone():
            print("Adding question_text column...")
            await conn.execute(text("""
                ALTER TABLE responses 
                ADD COLUMN question_text TEXT NULL AFTER question_number
            """))
            print("✅ Added question_text column")
        else:
            print("ℹ️ question_text column already exists")
        
        result = await conn.execute(text("SHOW COLUMNS FROM responses LIKE 'question_type'"))
        if not result.fetchone():
            print("Adding question_type column...")
            await conn.execute(text("""
                ALTER TABLE responses 
                ADD COLUMN question_type VARCHAR(50) NULL DEFAULT 'preset' AFTER question_text
            """))
            print("✅ Added question_type column")
        else:
            print("ℹ️ question_type column already exists")
        
        print("\n✅ Migration completed!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_columns())
