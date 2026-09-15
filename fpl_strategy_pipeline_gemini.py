import os, sys
try:
    from google import genai
    from youtube_transcript_api import YouTubeTranscriptApi
    from yt_dlp import YoutubeDL
except:
    sys.exit(1)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

channels = ["https://www.youtube.com/@FPLHarry", "https://www.youtube.com/@FPLRaptor", "https://www.youtube.com/@LetsTalkFPL", "https://www.youtube.com/@GianniButtice_", "https://www.youtube.com/@FantasyFootballHub", "https://www.youtube.com/@FPLFocal"]

transcripts = ""
for url in channels:
    try:
        with YoutubeDL({'quiet': True, 'extract_flat': 'in_playlist', 'playlistend': 5}) as ydl:
            info = ydl.extract_info(url, download=False)
            for entry in (info.get('entries') or [])[:2]:
                try:
                    t = YouTubeTranscriptApi.get_transcript(entry['id'])
                    transcripts += " ".join([x['text'] for x in t])[:1500]
                except: pass
    except: pass

chat = client.chats.create(model="gemini-2.0-flash")
response = chat.send_message(
    f"Analyze these FPL YouTuber transcripts. Give CAPTAIN PICK, VICE-CAPTAIN, TOP 3 TRANSFERS, CHIP, TEAM STRUCTURE:\n{transcripts[:2000]}"
)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
msg = MIMEMultipart()
msg['From'] = os.getenv("SENDER_EMAIL")
msg['To'] = os.getenv("RECIPIENT_EMAIL")
msg['Subject'] = "FPL Strategy"
msg.attach(MIMEText(response.text, 'plain'))
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))
server.send_message(msg)
server.quit()
print("Done")
