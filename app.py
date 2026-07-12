import streamlit as st
import yt_dlp

st.set_page_config(page_title="YT Downloader", page_icon="📥")
st.title("📥 YouTube Video Downloader")

url = st.text_input("Yahan apni YouTube video ka link paste karein:")

if url:
    try:
        with st.spinner("Link process ho raha hai..."):
            # Streamlit cloud ke liye optimization options
            ydl_opts = {
                'format': 'best', 
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video')
                download_url = info.get('url') # Yeh browser download link hai
                
            st.success(f"**Video Mil Gayi:** {video_title}")
            
            # HTML Button jo Chrome me download activate karega
            st.markdown(
                f'<a href="{download_url}" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #ff4b4b; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%;">👇 Click Here to Download 👇</a>',
                unsafe_allow_html=True
            )
            st.info("💡 Tip: Agar link khulne par video play hone lage, toh Chrome me right side niche 3-dots (...) par click karke 'Download' daba dein.")
            
    except Exception as e:
        st.error(f"Kuch dikkat aayi hai. Error: {e}")
