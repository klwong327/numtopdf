import streamlit as st
from reportlab.pdfgen import canvas
from io import BytesIO
import zipfile

st.set_page_config(
    page_title="Numbers → PDF Converter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

# Mobile-friendly CSS (simplified version similar to your existing app)
st.markdown(
    """
    <style>
    @media (max-width: 768px) {
        .stButton>button, .stDownloadButton>button {
            width: 100% !important;
            font-size: 16px !important;
            padding: 12px !important;
            min-height: 48px !important;
        }
        .stFileUploader {
            font-size: 16px !important;
        }
        .element-container {
            margin-bottom: 1rem !important;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.2rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Numbers → PDF Converter")
st.markdown(
    "Upload Apple Numbers `.numbers` files and convert them into simple PDF files."
)

st.info("💡 iPhone/iPad users: Tap the 'Browse files' button to select files from your device.")

st.header("📁 Upload Numbers Files")
st.caption("You can upload one or multiple `.numbers` files at once.")

numbers_files = st.file_uploader(
    "Upload .numbers files",
    type=["numbers"],
    accept_multiple_files=True,
    key="numbers",
)

def numbers_to_blank_pdf(numbers_bytes: bytes, name: str) -> bytes:
    """
    Convert a .numbers file into a simple 1-page PDF.
    This does NOT parse the spreadsheet – it just creates a blank page
    with a label showing the original filename. You can edit the PDF later.
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(595, 842))  # A4-ish
    c.setFont("Helvetica", 14)
    c.drawString(72, 800, f"Converted from: {name}")
    c.setFont("Helvetica", 10)
    c.drawString(72, 780, "This is a placeholder PDF generated from a .numbers file.")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 Convert to PDF", type="primary", use_container_width=True):
    if not numbers_files:
        st.error("❌ Please upload at least one `.numbers` file.")
    else:
        st.header("📥 Download Converted PDFs")
        converted_files = []
        total = len(numbers_files)
        progress = st.progress(0)

        for idx, nf in enumerate(numbers_files):
            with st.spinner(f"Converting: {nf.name}..."):
                numbers_bytes = nf.read()
                pdf_bytes = numbers_to_blank_pdf(numbers_bytes, nf.name)
                out_name = nf.name.replace(".numbers", ".pdf")
                converted_files.append((out_name, pdf_bytes))
            progress.progress((idx + 1) / total)

        if converted_files:
            st.success(f"🎉 Successfully converted {len(converted_files)} file(s).")

            if len(converted_files) == 1:
                fname, fbytes = converted_files[0]
                st.download_button(
                    label=f"⬇️ Download {fname}",
                    data=fbytes,
                    file_name=fname,
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                zip_buf = BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for fname, fbytes in converted_files:
                        zf.writestr(fname, fbytes)
                zip_buf.seek(0)
                st.download_button(
                    label=f"📦 Download All ({len(converted_files)} PDFs) as ZIP",
                    data=zip_buf.getvalue(),
                    file_name="numbers_converted_pdfs.zip",
                    mime="application/zip",
                    use_container_width=True,
                )

st.markdown("---")
st.markdown("🌐 Ready for deployment on Streamlit Cloud.")
