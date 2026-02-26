from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from typing import Optional
from PIL import Image
import numpy as np
import trimesh
from app.models.logo_converter import LogoConverter
from app.services.led_designer import LEDDesigner
from app.utils.validators import validate_image, validate_dimensions
import io

app = FastAPI(title="Logo to LED Signal Converter")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert-logo")
async def convert_logo(
    request: Request,
    file: UploadFile = File(...),
    width: float = Form(10.0),
    height: float = Form(10.0),
    max_width: float = Form(21.0),
    max_height: float = Form(21.0),
    num_colors: int = Form(4),
    led_spacing: float = Form(5.0),
    led_diameter: float = Form(3.0)
):
    # Validate inputs
    if not validate_dimensions(width, height, max_width, max_height):
        return JSONResponse(
            status_code=400,
            content={"error": f"Dimensions exceed maximum size of {max_width}x{max_height} cm"}
        )
    
    # Read and validate image
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid image file"})
    
    if not validate_image(image):
        return JSONResponse(status_code=400, content={"error": "Unsupported image format"})
    
    # Process logo conversion
    converter = LogoConverter()
    processed_image = converter.process_image(image, num_colors)
    
    # Create LED layout
    designer = LEDDesigner()
    led_positions = designer.calculate_led_positions(width, height, led_spacing)
    
    # Generate 3D model
    model_3d = designer.create_3d_model(
        width, 
        height, 
        processed_image, 
        led_positions, 
        led_diameter
    )
    
    # Save model
    filename = f"{file.filename.split('.')[0]}_led_signal.3mf"
    model_path = f"app/static/models/{filename}"
    model_3d.export(model_path)
    
    return JSONResponse(
        status_code=200,
        content={
            "message": "Conversion successful",
            "model_url": f"/static/models/{filename}",
            "dimensions": {"width": width, "height": height},
            "num_leds": len(led_positions)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)