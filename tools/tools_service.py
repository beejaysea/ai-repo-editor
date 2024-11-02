from fastapi import FastAPI, HTTPException, Depends, Path
from pydantic import BaseModel
from text_edit_tools import TextEditTools
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path as FilePath

app = FastAPI(
    title="Text Editor API",
    description="API for text file manipulation operations",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ViewRequest(BaseModel):
    path: str
    view_range: Optional[List[int]] = None
    truncate_length: Optional[int] = None

class ListDirectoryRequest(BaseModel):
    path: str
    depth: int

class CreateRequest(BaseModel):
    path: str
    file_text: str

class StrReplaceRequest(BaseModel):
    path: str
    old_str: str
    new_str: str

class InsertRequest(BaseModel):
    path: str
    insert_line: int
    new_str: str

class PathRequest(BaseModel):
    path: str

class TextEditToolsFactory:
    def __init__(self):
        self._instances: Dict[str, TextEditTools] = {}
    
    def get_tools(self, directory: str) -> TextEditTools:
        if directory not in self._instances:
            # Validate directory exists
            dir_path = FilePath(directory)
            if not dir_path.exists() or not dir_path.is_dir():
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid directory: {directory}"
                )
            self._instances[directory] = TextEditTools(directory=directory)
        return self._instances[directory]

tools_factory = TextEditToolsFactory()

async def get_tools(
    directory: str = Path(..., description="Working directory path")
) -> TextEditTools:
    try:
        return tools_factory.get_tools(directory)
    except Exception as e:
        logger.error(f"Error getting tools for directory {directory}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/text_editor/{directory}/view", 
         response_model=Dict[str, Any],
         description="View contents of a file")
async def view(
    directory: str,
    request: ViewRequest,
    tools: TextEditTools = Depends(get_tools)
) -> Dict[str, Any]:
    try:
        logger.info(f"Viewing file {request.path} in directory {directory}")
        return tools.view(request.path, request.view_range, request.truncate_length)
    except Exception as e:
        logger.error(f"Error viewing file: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/text_editor/{directory}/list_directory")
def list_directory(directory: str, request: ListDirectoryRequest, tools: TextEditTools = Depends(get_tools)):
    try:
        return tools.list_directory(request.path, request.depth)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/text_editor/{directory}/create")
def create(directory: str, request: CreateRequest, tools: TextEditTools = Depends(get_tools)):
    try:
        return tools.create(request.path, request.file_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/text_editor/{directory}/str_replace")
def str_replace(directory: str, request: StrReplaceRequest, tools: TextEditTools = Depends(get_tools)):
    try:
        return tools.str_replace(request.path, request.old_str, request.new_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/text_editor/{directory}/insert")
def insert(directory: str, request: InsertRequest, tools: TextEditTools = Depends(get_tools)):
    try:
        return tools.insert(request.path, request.insert_line, request.new_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/text_editor/{directory}/undo_edit")
def undo_edit(directory: str, request: PathRequest, tools: TextEditTools = Depends(get_tools)):
    try:
        return tools.undo_edit(request.path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/text_editor/{directory}/delete")
def delete(directory: str, request: PathRequest, tools: TextEditTools = Depends(get_tools)):
    try:
        return tools.delete(request.path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
