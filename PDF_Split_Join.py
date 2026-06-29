import copy
import os
import streamlit as st
from pypdf import PdfReader, PdfWriter

# ページのタイトルやデザイン設定
st.set_page_config(page_title="PDF らくらく一括分割・結合ツール", layout="centered")

st.title("📄 PDF らくらく一括分割・結合ツール")
st.write("スマホ、Mac、タブレットからいつでもどこでもPDFを加工できます。")

# --- PDF処理ロジック ---
def split_pdf_pages(input_file):
    """1ページを左右真っ二つに分割する"""
    reader = PdfReader(input_file)
    writer = PdfWriter()

    for page in reader.pages:
        orig_width = page.mediabox.right
        orig_height = page.mediabox.top
        half_width = orig_width / 2

        # 左半分
        page_left = copy.copy(page)
        page_left.mediabox.upper_left = (0, orig_height)
        page_left.mediabox.lower_left = (0, 0)
        page_left.mediabox.upper_right = (half_width, orig_height)
        page_left.mediabox.lower_right = (half_width, 0)
        writer.add_page(page_left)

        # 右半分
        page_right = copy.copy(page)
        page_right.mediabox.upper_left = (half_width, orig_height)
        page_right.mediabox.lower_left = (half_width, 0)
        page_right.mediabox.upper_right = (orig_width, orig_height)
        page_right.mediabox.lower_right = (orig_width, 0)
        writer.add_page(page_right)
        
    return writer

def merge_pdf_pages(input_file):
    """2ページを左右に並べて1ページに結合する"""
    reader = PdfReader(input_file)
    writer = PdfWriter()

    num_pages = len(reader.pages)
    if num_pages == 0:
        return writer

    for i in range(0, num_pages, 2):
        page1 = reader.pages[i]
        w = page1.mediabox.right
        h = page1.mediabox.top

        merged_page = writer.add_blank_page(width=w * 2, height=h)
        merged_page.merge_translated_page(page1, tx=0, ty=0)

        if i + 1 < num_pages:
            page2 = reader.pages[i + 1]
            merged_page.merge_translated_page(page2, tx=w, ty=0)
            
    return writer

# --- UI構築 ---
st.subheader("1. 行いたい処理を選択してください")
mode = st.radio(
    "モード選択",
    ["【分割】 1ページを左右真っ二つにする (A3 → A4×2 など)", 
     "【結合】 2ページを1枚に並べる (A4×2 → A3 など)"],
    label_visibility="collapsed"
)

st.subheader("2. PDFファイルをアップロードしてください")
uploaded_files = st.file_uploader(
    "複数ファイルの選択・ドラッグ＆ドロップが可能です", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    st.subheader("3. 変換を実行する")
    if st.button("一括変換スタート", type="primary"):
        
        # ファイルごとに処理
        for uploaded_file in uploaded_files:
            base_name, ext = os.path.splitext(uploaded_file.name)
            
            with st.spinner(f"{uploaded_file.name} を処理中..."):
                try:
                    if "分割" in mode:
                        writer = split_pdf_pages(uploaded_file)
                        output_name = f"{base_name}_分割完了{ext}"
                    else:
                        writer = merge_pdf_pages(uploaded_file)
                        output_name = f"{base_name}_結合完了{ext}"
                    
                    # メモリ上にPDFを書き出す
                    import io
                    pdf_buffer = io.BytesIO()
                    writer.write(pdf_buffer)
                    pdf_data = pdf_buffer.getvalue()
                    
                    # 変換成功の表示とダウンロードボタンの設置
                    st.success(f"✅ {uploaded_file.name} の処理が完了しました！")
                    st.download_button(
                        label=f"📥 {output_name} をダウンロード",
                        data=pdf_data,
                        file_name=output_name,
                        mime="application/pdf",
                        key=output_name # ボタンの識別キー
                    )
                    
                    # 💡 ここに「Googleドライブへ自動保存するコード」を数行追加すれば、
                    # ダウンロードと同時にご自身のGoogleドライブにも勝手に保存されます。
                    
                except Exception as e:
                    st.error(f"❌ {uploaded_file.name} の処理中にエラーが発生しました: {e}")