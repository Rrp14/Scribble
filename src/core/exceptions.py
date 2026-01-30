from fastapi import Request
from fastapi.responses import JSONResponse


async def value_error_handler(req:Request,exc:ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "error":"Bad Request",
            "message":str(exc),
            "path":req.url.path
        }
    )

