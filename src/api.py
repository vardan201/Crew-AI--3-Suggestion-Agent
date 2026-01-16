from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime
from typing import Dict
import json
import time
import asyncio
from dotenv import load_dotenv

load_dotenv()

import warnings
import logging
logging.getLogger("litellm").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*apscheduler.*")

from models import (
    StartupInput, 
    AnalysisRequest, 
    AnalysisResponse, 
    AnalysisStatus,
    AnalysisResults,
    AgentSuggestions
)
from main import prepare_inputs
from crew import BoardPanelCrew

app = FastAPI(
    title="Board Panel - Suggestions API",
    description="AI-powered startup advisory - SUGGESTIONS only",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Storage for analysis results
analysis_results: Dict[str, AnalysisStatus] = {}

# Token-based rate limiting
TOKENS_PER_MINUTE_LIMIT = 8000
ESTIMATED_TOKENS_PER_TASK = 2150
SAFETY_MARGIN = 0.8
TASKS_PER_ANALYSIS = 5

SAFE_TPM = TOKENS_PER_MINUTE_LIMIT * SAFETY_MARGIN
DELAY_BETWEEN_TASKS = (60.0 / SAFE_TPM) * ESTIMATED_TOKENS_PER_TASK

print(f"Rate limiting configured: {DELAY_BETWEEN_TASKS:.2f}s delay between tasks to stay under {SAFE_TPM:.0f} TPM")

request_lock = asyncio.Lock()
last_request_time = 0


async def rate_limit_tokens():
    """Enforce token-based rate limiting"""
    global last_request_time
    async with request_lock:
        current_time = time.time()
        time_since_last = current_time - last_request_time
        
        if time_since_last < DELAY_BETWEEN_TASKS:
            wait_time = DELAY_BETWEEN_TASKS - time_since_last
            print(f"Rate limiting: waiting {wait_time:.2f}s before next task")
            await asyncio.sleep(wait_time)
        
        last_request_time = time.time()


def safe_extract_suggestions(task_output, task_name: str, fallback_count: int = 5) -> list:
    """
    Safely extract suggestions from task output with comprehensive error handling
    """
    try:
        # Method 1: Try to get pydantic model directly
        if hasattr(task_output, 'pydantic') and task_output.pydantic:
            if hasattr(task_output.pydantic, 'suggestions'):
                suggestions = task_output.pydantic.suggestions
                if suggestions and len(suggestions) > 0:
                    print(f"✓ {task_name}: Extracted {len(suggestions)} suggestions via pydantic model")
                    return suggestions
        
        # Method 2: Try to parse from raw output
        if hasattr(task_output, 'raw'):
            raw_text = task_output.raw
            print(f"  {task_name}: Attempting to parse raw output (length: {len(raw_text)})")
            
            # Try to find JSON in the raw text
            try:
                # Look for JSON object
                json_start = raw_text.find('{')
                json_end = raw_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = raw_text[json_start:json_end]
                    print(f"  {task_name}: Found JSON substring (length: {len(json_str)})")
                    
                    # Try to parse
                    parsed = json.loads(json_str)
                    
                    if 'suggestions' in parsed and isinstance(parsed['suggestions'], list):
                        suggestions = parsed['suggestions']
                        print(f"✓ {task_name}: Extracted {len(suggestions)} suggestions from raw JSON")
                        return suggestions
            except json.JSONDecodeError as e:
                print(f"  {task_name}: JSON parse error at position {e.pos}: {str(e)}")
                
                # Try to fix common JSON errors
                try:
                    # Remove trailing incomplete data
                    if json_start != -1:
                        # Find last complete suggestion
                        truncated = raw_text[json_start:e.pos]
                        # Try to close the JSON properly
                        if truncated.count('[') > truncated.count(']'):
                            truncated += '"]}'
                        elif truncated.count('{') > truncated.count('}'):
                            truncated += '}'
                        
                        fixed = json.loads(truncated)
                        if 'suggestions' in fixed and isinstance(fixed['suggestions'], list):
                            suggestions = fixed['suggestions']
                            print(f"✓ {task_name}: Recovered {len(suggestions)} suggestions from truncated JSON")
                            return suggestions
                except:
                    pass
            
            # Try to extract suggestions as text list
            try:
                lines = raw_text.split('\n')
                suggestions = []
                for line in lines:
                    line = line.strip()
                    # Look for numbered or bulleted lists
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        # Remove numbering and bullets
                        cleaned = line.lstrip('0123456789.-•) ').strip()
                        if len(cleaned) > 20:  # Reasonable suggestion length
                            suggestions.append(cleaned)
                
                if len(suggestions) >= 3:
                    print(f"✓ {task_name}: Extracted {len(suggestions)} suggestions from text list")
                    return suggestions[:fallback_count]  # Cap at expected count
            except Exception as e:
                print(f"  {task_name}: Text extraction failed: {str(e)}")
        
        # Method 3: Check for 'output' attribute
        if hasattr(task_output, 'output'):
            try:
                output_data = task_output.output
                if isinstance(output_data, str):
                    parsed = json.loads(output_data)
                    if 'suggestions' in parsed:
                        suggestions = parsed['suggestions']
                        print(f"✓ {task_name}: Extracted {len(suggestions)} suggestions from output attribute")
                        return suggestions
            except:
                pass
        
    except Exception as e:
        print(f"  {task_name}: Extraction error: {str(e)}")
    
    # Fallback: Return empty list with warning
    print(f"✗ {task_name}: Could not extract suggestions - returning empty list")
    return []


async def run_analysis(analysis_id: str, startup_data: StartupInput):
    """Run the crew analysis with token-based rate limiting and robust error handling"""
    max_retries = 5
    
    try:
        # Update status
        analysis_results[analysis_id].status = "processing"
        
        # Prepare inputs
        inputs = prepare_inputs(startup_data)
        
        crew_result = None
        
        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                # Apply token-based rate limiting before request
                await rate_limit_tokens()
                
                print(f"\n{'='*60}")
                print(f"Attempt {attempt + 1}/{max_retries} for analysis {analysis_id}")
                print(f"{'='*60}")
                
                # Run the crew
                crew_result = BoardPanelCrew().crew().kickoff(inputs=inputs)
                print(f"\n✓ Analysis {analysis_id} completed successfully")
                break
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if it's a rate limit error
                if "rate_limit" in error_str or "429" in error_str or "rate limit" in error_str:
                    if attempt < max_retries - 1:
                        # Extract wait time from error message if available
                        wait_time = 10
                        if "try again in" in error_str:
                            try:
                                parts = error_str.split("try again in")[1].split("s")[0].strip()
                                wait_time = float(parts) + 2
                            except:
                                wait_time = 10
                        
                        # Exponential backoff
                        delay = max(wait_time, 10 * (2 ** attempt))
                        print(f"⚠ Rate limit hit, waiting {delay:.1f}s before retry {attempt + 2}/{max_retries}")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} retries. Please try again in a few minutes.")
                
                # Check if it's a Pydantic validation error
                if "validation error" in error_str or "invalid json" in error_str:
                    print(f"⚠ Pydantic validation error: {str(e)[:200]}")
                    # Log but don't retry - we'll handle this in extraction
                    break
                
                # For other errors, raise immediately
                raise
        
        if crew_result is None:
            raise Exception("Analysis failed: No result returned from crew")
        
        # Extract Pydantic structured outputs with robust error handling
        tasks_output = crew_result.tasks_output if hasattr(crew_result, 'tasks_output') else []
        
        print(f"\n{'='*60}")
        print(f"Processing {len(tasks_output)} task outputs")
        print(f"{'='*60}")
        
        # Task order: marketing(0), tech(1), org_hr(2), competitive(3), finance(4)
        marketing_suggestions = safe_extract_suggestions(
            tasks_output[0] if len(tasks_output) > 0 else None, 
            "Marketing", 5
        )
        tech_suggestions = safe_extract_suggestions(
            tasks_output[1] if len(tasks_output) > 1 else None, 
            "Tech", 5
        )
        org_hr_suggestions = safe_extract_suggestions(
            tasks_output[2] if len(tasks_output) > 2 else None, 
            "Org/HR", 5
        )
        competitive_suggestions = safe_extract_suggestions(
            tasks_output[3] if len(tasks_output) > 3 else None, 
            "Competitive", 5
        )
        finance_suggestions = safe_extract_suggestions(
            tasks_output[4] if len(tasks_output) > 4 else None, 
            "Finance", 5
        )
        
        # Create results
        results = AnalysisResults(
            marketing_suggestions=marketing_suggestions,
            tech_suggestions=tech_suggestions,
            org_hr_suggestions=org_hr_suggestions,
            competitive_suggestions=competitive_suggestions,
            finance_suggestions=finance_suggestions
        )
        
        # Validation summary
        print(f"\n{'='*60}")
        print("VALIDATION SUMMARY")
        print(f"{'='*60}")
        total_suggestions = 0
        for category, suggestions in [
            ("Marketing", results.marketing_suggestions),
            ("Tech", results.tech_suggestions),
            ("Org/HR", results.org_hr_suggestions),
            ("Competitive", results.competitive_suggestions),
            ("Finance", results.finance_suggestions)
        ]:
            count = len(suggestions)
            total_suggestions += count
            status = "✓" if count >= 3 else "✗"
            print(f"{status} {category}: {count} suggestions")
        
        print(f"\nTotal suggestions: {total_suggestions}")
        
        # Check if we have enough suggestions to consider it successful
        if total_suggestions < 10:
            print(f"\n⚠ WARNING: Only {total_suggestions} total suggestions extracted")
            print("Analysis may be incomplete but returning available results")
        
        # Update result
        analysis_results[analysis_id].status = "completed"
        analysis_results[analysis_id].result = results
        analysis_results[analysis_id].completed_at = datetime.now().isoformat()
        
        print(f"\n✓ Analysis {analysis_id} completed and stored")
        
    except Exception as e:
        print(f"\n✗ Analysis {analysis_id} FAILED")
        print(f"Error: {str(e)}")
        print(f"Type: {type(e).__name__}")
        
        analysis_results[analysis_id].status = "failed"
        analysis_results[analysis_id].error = f"{type(e).__name__}: {str(e)}"
        analysis_results[analysis_id].completed_at = datetime.now().isoformat()


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Submit a startup for analysis. Returns an analysis_id to check status.
    Note: Due to API rate limits (8000 tokens/minute), analysis may take 2-3 minutes.
    """
    analysis_id = str(uuid.uuid4())
    
    # Initialize status
    analysis_results[analysis_id] = AnalysisStatus(
        analysis_id=analysis_id,
        status="queued",
        submitted_at=datetime.now().isoformat()
    )
    
    # Run analysis in background
    background_tasks.add_task(run_analysis, analysis_id, request.startup_data)
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="queued",
        message="Analysis queued. Check status at /api/results/{analysis_id}. Expected completion: 2-3 minutes due to rate limits."
    )


@app.get("/api/results/{analysis_id}", response_model=AnalysisStatus)
async def get_results(analysis_id: str):
    """
    Get the analysis results by analysis_id.
    Returns status and results when completed.
    """
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis ID not found")
    
    return analysis_results[analysis_id]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Board Panel API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "results": "GET /api/results/{analysis_id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
