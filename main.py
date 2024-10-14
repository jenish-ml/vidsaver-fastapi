from fastapi import FastAPI, Form, Request
from pytube import YouTube
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import yt_dlp
import instaloader

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/download/")
async def download_video(video_url: str = Form(...)):
    try:
        # Download the video using yt-dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = os.path.join('downloads', f"{info['title']}.mp4")

        return FileResponse(file_path, media_type='video/mp4', filename=os.path.basename(file_path))

    except Exception as e:
        return {"error": str(e)}

async def download_instagram_video(post_url: str):
    try:
        L = instaloader.Instaloader()
        
        # Extract shortcode from post URL
        shortcode = post_url.split("/")[-2]  # Assuming the URL is in the format https://www.instagram.com/p/shortcode/

        # Download the post
        L.download_post(L.check_post(shortcode), target='downloads')

        # Construct file path (assumes video is in downloads folder)
        file_path = os.path.join('downloads', f"{shortcode}.mp4")
        return file_path

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/download/")
async def download_video(video_url: str = Form(...)):
    if "youtube.com" in video_url or "youtu.be" in video_url:
        return FileResponse(await download_youtube_video(video_url), media_type='video/mp4')
    elif "instagram.com/p/" in video_url:
        return FileResponse(await download_instagram_video(video_url), media_type='video/mp4')
    else:
        raise HTTPException(status_code=400, detail="Invalid URL. Only YouTube and Instagram post URLs are supported.")

