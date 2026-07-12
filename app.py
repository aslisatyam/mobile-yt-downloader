import streamlit as st
import yt_dlp

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Ab har quality me video download karein full sound ke sath!")

# Initialize session states
if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Details & Filter Sound Formats
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video formats scan ho rahe hain..."):
            try:
                # 403 Error se bachne ke liye user-agent set karna zaroorat hai
                ydl_opts = {
                    'quiet': True, 
                    'no_warnings': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Video')
                    thumbnail = info.get('thumbnail')
                    formats = info.get('formats', [])
                    
                    unique_formats = {}
                    
                    # Sirf wahi formats nikalenge jisme audio + video dono sath ho, taaki download hone par direct sound chale aur 403 na aaye
                    for f in formats:
                        if f.get('height') and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                            res = f"{f.get('height')}p"
                            ext = f.get('ext', 'mp4')
                            label = f"{res} (With Sound - .{ext})"
                            unique_formats[label] = f.get('url')
                    
                    # Fallback agar koi progressive stream nahi mili
                    if not unique_formats:
                        best_url = info.get('url')
                        if best_url:
                            unique_formats["Best Auto Quality (With Sound)"] = best_url
                    
                    sorted_labels = sorted(unique_formats.keys(), key=lambda x: int(x.split('p')[0]) if 'p' in x else 0, reverse=True)
                    
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error(f"Error: Details fetch nahi ho payin. YouTube block ho sakta hai ya link galat hai. Details: {e}")

# Step 2: Show UI & Direct Client-Side Download
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"**🎬 Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_download_url = data['formats_dict'][selected_label]
        
        # Is HTML link se user ka browser khud YouTube se file stream karega, Streamlit Cloud server beech me block nahi hoga
        st.markdown(
            f'<a href="{final_download_url}" target="_blank" download="{data["title"]}.mp4" style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">📥 Download Now ({selected_label})</a>',
            unsafe_allow_html=True
        )
        
        st.info("💡 **Important:** Button dabane par agar naye tab me video play hone lage, toh wahan right side corner me **3 dots (...)** par click karke **Download** daba dein!")
    else:
        st.error("Formats load nahi ho paaye.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
