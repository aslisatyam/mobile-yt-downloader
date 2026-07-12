import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Premium YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Premium YouTube Downloader (With Audio)")
st.write("Apni video ka link paste karein aur full sound ke sath best quality me download karein!")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Details
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video details scan ho rahi hain..."):
            try:
                ydl_opts = {'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Video')
                    thumbnail = info.get('thumbnail')
                    formats = info.get('formats', [])
                    
                    unique_formats = {}
                    
                    # 1. Sabse pehle un formats ko filter karein jisme video aur audio dono pehle se mixed ho (Progressive Streams)
                    for f in formats:
                        # vcodec aur acodec dono 'none' nahi hone chahiye, matlab dono maujood hain
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('height'):
                            res = f"{f.get('height')}p"
                            ext = f.get('ext', 'mp4')
                            label = f"{res} (Sound Included - .{ext})"
                            unique_formats[label] = f.get('url')
                    
                    # 2. Agar koi mixed format nahi mila, toh fallback ke liye best combine stream uthayein
                    if not unique_formats:
                        best_url = info.get('url')
                        if best_url:
                            unique_formats["Best Available Quality (With Sound)"] = best_url

                    sorted_labels = sorted(unique_formats.keys(), key=lambda x: int(x.split('p')[0]) if 'p' in x else 0, reverse=True)
                    
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error(f"Error: Link sahi nahi hai. Details: {e}")

# Step 2: Show UI & Handover Download
if st.session_state.video_data:
    data = st.session_state.video_data
    
    st.success(f"**🎬 Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_download_url = data['formats_dict'][selected_label]
        
        # Sahi Tarika: Direct anchor link jo browser ko progressive stream file deliver karega
        st.markdown(
            f'<a href="{final_download_url}" target="_blank" download="{data["title"]}.mp4" style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">📥 Download Now ({selected_label})</a>',
            unsafe_allow_html=True
        )
        
        st.caption("💡 **Important Note:** Agar button par click karne ke baad video download hone ki jagah browser me play hone lage, toh video player ke kone me **3 dots (...)** dikhenge, unpar click karke **'Download'** select karein, video audio ke sath save ho jayegi!")
    else:
        st.error("Is video ke liye koi valid sound-supported format nahi mil paya.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
