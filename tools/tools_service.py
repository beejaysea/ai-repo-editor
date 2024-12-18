import os
from fastapi import FastAPI, HTTPException, Depends, Path
from pydantic import BaseModel
from tools.text_edit_tools import TextEditTools
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path as FilePath
import subprocess

app = FastAPI(
    title="Text Editor API",
    description="API for text file manipulation operations",
    version="1.0.0",
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


class BashCommandRequest(BaseModel):
    command: str


class TextEditToolsFactory:
    def __init__(self):
        self._instances: Dict[str, TextEditTools] = {}

    def get_tools(self, directory: str) -> TextEditTools:
        if directory not in self._instances:
            # Prepend work_dir to the directory path
            work_dir_path = f"./work_dir/{directory}"
            if not os.path.exists(work_dir_path):
                os.makedirs(work_dir_path)
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


@app.post(
    "/text_editor/{directory}/view",
    response_model=Dict[str, Any],
    description="View contents of a file",
)
async def view(
    directory: str, request: ViewRequest, tools: TextEditTools = Depends(get_tools)
) -> Dict[str, Any]:
    try:
        logger.info(f"Viewing file {request.path} in directory {directory}")
        return {
            "file": tools.view(request.path, request.view_range, request.truncate_length)
        }
    except Exception as e:
        logger.error(f"Error viewing file: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text_editor/{directory}/list_directory")
def list_directory(
    directory: str,
    request: ListDirectoryRequest,
    tools: TextEditTools = Depends(get_tools),
):
    try:
        return tools.list_directory(request.path, request.depth)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text_editor/{directory}/create")
def create(
    directory: str, request: CreateRequest, tools: TextEditTools = Depends(get_tools)
):
    try:
        return tools.create(request.path, request.file_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text_editor/{directory}/str_replace")
def str_replace(
    directory: str,
    request: StrReplaceRequest,
    tools: TextEditTools = Depends(get_tools),
):
    try:
        return tools.str_replace(request.path, request.old_str, request.new_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text_editor/{directory}/insert")
def insert(
    directory: str, request: InsertRequest, tools: TextEditTools = Depends(get_tools)
):
    try:
        return tools.insert(request.path, request.insert_line, request.new_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text_editor/{directory}/undo_edit")
def undo_edit(
    directory: str, request: PathRequest, tools: TextEditTools = Depends(get_tools)
):
    try:
        return tools.undo_edit(request.path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text_editor/{directory}/delete")
def delete(
    directory: str, request: PathRequest, tools: TextEditTools = Depends(get_tools)
):
    try:
        return tools.delete(request.path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text_editor/{directory}/bash")
async def execute_bash_command(
    directory: str, request: BashCommandRequest
) -> Dict[str, Any]:
    try:
        # Prepend work_dir to the directory path for bash commands
        work_dir_path = f"./work_dir/{directory}"
        if not os.path.exists(work_dir_path):
            os.makedirs(work_dir_path)
        logger.info(f"Executing command '{request.command}' in directory {work_dir_path}")
        # Our command may contain a path. `/repo` should map to ./work_dir/{directory}
        # let's transform it first
        request.command = request.command.replace("/repo", work_dir_path)
        result = subprocess.run(
            request.command, shell=True, cwd="/app", capture_output=True, text=True
        )
        # and the reverse transformation for the output
        result.stdout = result.stdout.replace(work_dir_path, "/repo")
        return {
            "stdout": result.stdout,
            # "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
