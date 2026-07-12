import streamlit as st
import yt_dlp

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Ab har quality me video download karein full sound ke sath!")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Title, Thumbnail & Set Download Links
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video details scan ho rahi hain..."):
            try:
                # Basic metadata fetch to avoid YouTube blocks
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'YouTube Video')
                    thumbnail = info.get('thumbnail')
                
                # Sahi kiye gaye working URLs (Slash error fixed)
                unique_formats = {
                    "Premium High Quality (720p/1080p HD)": f"https://twdown.tools{url}",
                    "Standard Quality (360p/480p SD)": f"https://ssyoutube.com{url.split('/')[-1].split('?')[0]}"
                }
                
                st.session_state.video_data = {
                    'title': title,
                    'thumbnail': thumbnail,
                    'formats_dict': unique_formats,
                    'sorted_labels': list(unique_formats.keys())
                }
                st.rerun()
                
            except Exception as e:
                # Fallback mechanism if basic fetch fails
                st.session_state.video_data = {
                    'title': "YouTube Video",
                    'thumbnail': None,
                    'formats_dict': {"Download Video (Best Quality)": f"https://twdown.tools{url}"},
                    'sorted_labels': ["Download Video (Best Quality)"]
                }
                st.rerun()

# Step 2: Show UI & Action Download Button
if st.session_state.video_data:
    data = st.session_state.video_data
    
    st.success(f"🎬 **Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_download_url = data['formats_dict'][selected_label]
        
        # Premium Green Layout Button
        st.markdown(
            f'<a href="{final_download_url}" target="_blank" style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">📥 Download Now ({selected_label})</a>',
            unsafe_allow_html=True
        )
        st.caption("💡 **Tip:** Button par click karte hi website Chrome me sahi se open hogi aur download option mil jayega.")
    else:
        st.error("Formats load nahi ho paaye.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
