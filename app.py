import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Ab har quality me video download karein full sound ke sath!")

# Initialize session states
if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Details & Qualities (Even separated ones)
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video formats scan ho rahe hain..."):
            try:
                ydl_opts = {'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Video')
                    thumbnail = info.get('thumbnail')
                    formats = info.get('formats', [])
                    
                    qualities = set()
                    for f in formats:
                        if f.get('height') and f.get('vcodec') != 'none':
                            # Saari heights (resolutions) collect karein jaise 1080, 720, 480, 360
                            qualities.add(f.get('height'))
                    
                    # Sort qualities high to low
                    sorted_qualities = sorted(list(qualities), reverse=True)
                    quality_labels = [f"{q}p" for q in sorted_qualities]
                    
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'quality_labels': quality_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error(f"Error: Details fetch nahi ho payin. Details: {e}")

# Step 2: Show UI & High-Quality Server Side Processing
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"**🎬 Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['quality_labels']:
        selected_quality = st.selectbox("⚡ Video Quality Select Karein:", data['quality_labels'])
        
        # Streamlit standard Download Button
        # Yeh tabhi chalega jab user download par click karega (Lazy processing)
        height = selected_quality.replace('p', '')
        
        # Temp directory for processing
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, '%(title)s.%(ext)s')
            
            # yt-dlp option jo best video (selected height tak) aur best audio ko download karke merge karega
            # Formats setup: select specific height video + best audio
            ydl_merge_opts = {
                'format': f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best',
                'merge_output_format': 'mp4',
                'outtmpl': output_template,
                'quiet': True
            }
            
            # Button trigger mechanism
            if st.button(f"📥 Process & Download {selected_quality}", use_container_width=True):
                with st.spinner("Server par video aur sound ko combine kiya ja raha hai... Isme 10-20 seconds lag sakte hain."):
                    try:
                        with yt_dlp.YoutubeDL(ydl_merge_opts) as ydl:
                            info_dict = ydl.extract_info(url, download=True)
                            filename = ydl.prepare_filename(info_dict)
                            # Format change safety extension check
                            if not os.path.exists(filename):
                                filename = os.path.splitext(filename)[0] + '.mp4'
                            
                            # Read file bytes to serve to user browser
                            with open(filename, "rb") as file:
                                video_bytes = file.read()
                                
                        # Final download trigger inside browser
                        st.download_button(
                            label="🎉 Video Ready! Click here to Save",
                            data=video_bytes,
                            file_name=f"{data['title']}_{selected_quality}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Processing error: {e}. Make sure 'ffmpeg' is added to your packages.txt file!")
    else:
        st.error("Formats load nahi ho paaye.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
