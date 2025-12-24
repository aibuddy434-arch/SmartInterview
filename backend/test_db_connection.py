"""
Quick Database Connection Test
Run: python test_db_connection.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Use credentials directly (root:Password as you mentioned)
DATABASE_URL = "mysql+aiomysql://root:Password@localhost:3306/ai_interview"

async def test_connection():
    print(f"📡 Testing connection to MySQL...")
    print(f"   URL: mysql+aiomysql://root:****@localhost:3306/ai_interview")
    
    try:
        engine = create_async_engine(DATABASE_URL)
        
        async with engine.connect() as conn:
            # Test 1: Basic connection
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection: SUCCESS")
            
            # Test 2: Check tables exist
            result = await conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Tables found: {tables}")
            
            # Test 3: Check responses table has new columns
            if 'responses' in tables:
                result = await conn.execute(text("DESCRIBE responses"))
                columns = [row[0] for row in result.fetchall()]
                print(f"✅ Responses columns: {columns}")
                
                if 'question_text' in columns and 'question_type' in columns:
                    print("✅ New columns (question_text, question_type): EXIST")
                else:
                    print("⚠️ New columns missing! Run: python add_question_columns.py")
            else:
                print("⚠️ 'responses' table not found - run backend to create tables")
        
        await engine.dispose()
        print("\n🎉 Database is working correctly!")
        
    except Exception as e:
        print(f"❌ Connection FAILED: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Is MySQL running? Check: net start mysql")
        print("   2. Check credentials: root / Password")
        print("   3. Does database exist? Run in MySQL: CREATE DATABASE ai_interview;")

if __name__ == "__main__":
    asyncio.run(test_connection())
