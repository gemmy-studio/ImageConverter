import os
import glob
from PIL import Image
import cairosvg
import xml.etree.ElementTree as ET
import streamlit as st
import base64
import io
from streamlit.components.v1 import html


def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


def get_svg_size_from_viewbox(svg_data):
    """SVG 데이터에서 viewBox 속성을 파싱하여 width와 height를 반환합니다."""
    root = ET.fromstring(svg_data)
    viewbox = root.get('viewBox', None)

    if viewbox:
        _, _, width, height = map(float, viewbox.split())
        return int(width), int(height)
    return None, None


def convert_image_format(uploaded_file, output_path, output_format, width, height):
    """
    이미지 파일 형식 변환 함수

    Parameters:
    - uploaded_file: Streamlit의 file_uploader에서 업로드된 파일 객체
    - output_path: 변환된 이미지를 저장할 경로
    - output_format: 저장할 이미지 형식 (예: 'JPEG', 'PNG', 'GIF', 'BMP', 'TIFF', 'WEBP', 'ICO')
    - width, height: 변경할 이미지의 너비와 높이
    """

    # uploaded_file을 io.BytesIO 객체로 변환
    if not isinstance(uploaded_file, io.BytesIO):
        uploaded_file = io.BytesIO(uploaded_file)

    img = Image.open(uploaded_file)
    img = img.resize((width, height))

    if output_format == "ICO":
        img.save(output_path, format=output_format, sizes=[(width, height)])
    else:
        if img.mode == "RGBA" and output_format == "JPEG":
            img = img.convert("RGB")
        if img.mode == "P":
            img = img.convert("RGB")
        img.save(output_path, format=output_format)


def main():
    st.set_page_config(page_title="이미지 변환 도구", page_icon="favicon.ico",
                       layout="centered", initial_sidebar_state="auto", menu_items=None)

    button = """
    <script data-name="BMC-Widget" data-cfasync="false" src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js" data-id="woojae" data-description="Support me on Buy me a coffee!" data-message="방문해주셔서 감사합니다 :)" data-color="#40DCA5" data-position="Right" data-x_margin="18" data-y_margin="18"></script>
    """

    st.title('이미지 변환 도구')
    st.divider()
    st.header('이미지를 다양한 형식과 크기로 변환하세요!')

    uploaded_file = st.file_uploader(
        "변환할 파일을 업로드 해주세요. (지원 형식: .jpeg, .png, .gif, .bmp, .tiff, .webp, .svg)")

    if uploaded_file:
        uploaded_file_type = uploaded_file.type
        width, height = 0, 0
        if uploaded_file_type == "image/svg+xml":
            svg_content = uploaded_file.getvalue().decode("utf-8")
            width, height = get_svg_size_from_viewbox(svg_content)
            if width and height:
                st.write(
                    f"기존 이미지 크기 (viewBox 기준): {width} x {height}")
            else:
                st.write("SVG 파일에서 크기 정보를 찾을 수 없습니다.")

            # uploaded_file의 내용을 읽기
            file_content = uploaded_file.read()
            # 복제된 file-like 객체 생성
            cloned_file1 = io.BytesIO(file_content)
            uploaded_file = io.BytesIO(file_content)

            cloned_file1 = cairosvg.svg2png(file_obj=cloned_file1)
            st.image(cloned_file1, caption='업로드 파일')
        else:
            # 이미지 파일을 열기
            with Image.open(uploaded_file) as img:
                width, height = img.size
                st.write(f"이미지 넓이: {width}, 이미지 높이: {height}")

        option = st.selectbox(
            '변환 형식 설정',
            ('JPEG', 'PNG', 'GIF', 'BMP', 'TIFF', 'WEBP', 'ICO'))

        if option == 'ICO':
            converted_width = st.number_input('이미지 넓이(최대: 256)', 0, 256)
            converted_height = st.number_input('이미지 높이(최대: 256)', 0, 256)
        else:
            converted_width = st.number_input('이미지 넓이', 0, 8192, width)
            converted_height = st.number_input('이미지 높이', 0, 8192, height)

        if st.button('이미지 변환하기'):
            with st.spinner('변환하는 중'):
                # 이전에 다운로드 한 파일을 삭제
                files_to_remove = glob.glob('converted_*')
                for file in files_to_remove:
                    os.remove(file)

                image_path = 'converted_image.{}'.format(option.lower())

                if uploaded_file_type == "image/svg+xml":
                    uploaded_file = cairosvg.svg2png(
                        file_obj=uploaded_file, output_width=converted_width, output_height=converted_height)

                convert_image_format(
                    uploaded_file, image_path, option, converted_width, converted_height)

                image = Image.open(image_path)

                st.image(image, caption='변환된 이미지')

                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                    st.download_button(
                        '다운로드', image_bytes, file_name=image_path, mime='image/{}'.format(option.lower()))

    html(button, height=600, width=400)

    st.markdown(
        """
        <style>
            iframe[width="400"] {
                position: fixed;
                bottom: 60px;
                right: 40px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == '__main__':
    main()
