from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import sys
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = FastAPI(title="Readme API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
async def root():
    try:
        return {"message": "서버가 현재 실행 중입니다"}
    except Exception as e:
        print("[ERROR] : ", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/showReadme")
async def show_readme(repo_url: str, language: str):
    try:
        repo_parts = repo_url.split("/")
        owner, repo = repo_parts[-2], repo_parts[-1]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.github.com/repos/{owner}/{repo}/readme")
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="README를 가져오는데 실패했습니다")
            
            readme_info = response.json()
            readme_content = await client.get(readme_info["download_url"])
            
            return readme_content.text
    
    except Exception as e:
        print("[ERROR] : ", e)
        raise HTTPException(status_code=500, detail=str(e))

async def get_repo_info(repo_url: str):
    repo_parts = repo_url.split("/")
    owner, repo = repo_parts[-2], repo_parts[-1]
    
    async with httpx.AsyncClient() as client:
        # Get repository information
        repo_response = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
        repo_info = repo_response.json()
        
        # Get repository contents
        contents_response = await client.get(f"https://api.github.com/repos/{owner}/{repo}/contents")
        contents = contents_response.json()
        
        # Get languages used in the repository
        languages_response = await client.get(f"https://api.github.com/repos/{owner}/{repo}/languages")
        languages = languages_response.json()
        
    return {
        "name": repo_info["name"],
        "description": repo_info["description"],
        "stars": repo_info["stargazers_count"],
        "forks": repo_info["forks_count"],
        "contents": [item["name"] for item in contents if item["type"] == "file"],
        "languages": list(languages.keys())
    }

@app.post("/conjureReadme")
async def conjure_readme(repo_url: str, language: str):
    try:
        repo_info = await get_repo_info(repo_url)
        
        prompt = f"""You are a professional README writer. Create a comprehensive README for the following GitHub repository in {language} language. Use proper Markdown syntax.

Repository Information:
- Name: {repo_info['name']}
- Description: {repo_info['description']}
- Stars: {repo_info['stars']}
- Forks: {repo_info['forks']}
- Main files: {', '.join(repo_info['contents'][:5])}  # Limiting to first 5 files for brevity
- Languages used: {', '.join(repo_info['languages'])}

Please include the following sections:
1. Project Title and Description
2. Features
3. Installation
4. Usage
5. Contributing
6. License

Make sure to use appropriate Markdown formatting, including headers, lists, code blocks, and emphasis where necessary.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates README files for GitHub repositories."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print("[ERROR] : ", e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python conjureReadme.py <endpoint> <repo_url> <language>")
        sys.exit(1)

    endpoint, repo_url, language = sys.argv[1], sys.argv[2], sys.argv[3]

    import asyncio
    if endpoint == "/showReadme":
        result = asyncio.run(show_readme(repo_url, language))
    elif endpoint == "/conjureReadme":
        result = asyncio.run(conjure_readme(repo_url, language))
    else:
        print(f"Unknown endpoint: {endpoint}")
        sys.exit(1)

    print(result)