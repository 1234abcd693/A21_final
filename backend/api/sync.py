"""
数据同步路由（导出/导入）
"""

import os

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse

from tools.sync import export_data, import_data

router = APIRouter()


@router.get("/export")
async def export():
    """导出全库数据（zip 下载）"""
    import tempfile
    result = export_data(tempfile.gettempdir())
    zip_path = result.get("path", "")
    if not zip_path or not os.path.exists(zip_path):
        return {"error": "导出失败", "code": 500}
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=os.path.basename(zip_path),
    )


@router.post("/import")
async def import_package(file: UploadFile = File(...)):
    """导入知识包"""
    import tempfile
    tmp_path = os.path.join(tempfile.gettempdir(), file.filename or "import.zip")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    result = import_data(tmp_path)
    os.remove(tmp_path)
    return result
