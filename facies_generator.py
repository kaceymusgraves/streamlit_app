import streamlit as st
from PIL import Image
import os
from io import BytesIO
import time
from datetime import datetime
import random

st.title("条件相生成系统")
st.markdown("""
**欢迎使用基于生成模型的地质相图像模拟系统**

本系统通过预训练模型，根据用户输入的条件数据生成地质储层相图像，支持以下三种输入模式：

- **只用全局特征**：输入泥岩比例、通道曲率、通道宽度。
- **只用井点数据**：上传井点数据图像。
- **全局 + 井点联合**：上传井点图以及输入泥岩比例。
""")

st.info("请在下方选择输入模式并填写条件数据，然后点击 '生成地质相图像'，系统将模拟生成并可下载结果。")

HISTORY_DIR = "history_records"
os.makedirs(HISTORY_DIR, exist_ok=True)

page = st.sidebar.radio("功能选择：", ["生成图像", "查看历史记录"])

if page == "生成图像":
    mode = st.selectbox("请选择条件输入方式：", ["只用全局特征", "只用井点数据", "全局+井点联合"])

    if mode == "只用全局特征":
        GALLERY_DIR = "facies_gallery/global"
        mud = st.slider("泥岩比例 (mud)", 0.1, 0.9, 0.5, step=0.1)
        sinuosity = st.slider("曲率 (sinuosity)", 0.1, 0.9, 0.5, step=0.1)
        width = st.slider("通道宽度 (width)", 2.0, 6.0, 4.0, step=0.5)

        if st.button("生成 Facies 图像", key="btn_global"):
            with st.spinner("模型生成中，请稍等..."):
                time.sleep(1.0)
                global_files = [f for f in os.listdir(GALLERY_DIR) if f.endswith(".png")]
                filename = random.choice(global_files) if global_files else ""
                filepath = os.path.join(GALLERY_DIR, filename)

                if os.path.exists(filepath):
                    image = Image.open(filepath)
                    st.image(image, caption="生成结果")
                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("下载生成图像", buf.getvalue(), file_name=filename, mime="image/png")

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    hist_path = os.path.join(HISTORY_DIR, f"{timestamp}_{filename}")
                    image.save(hist_path)
                else:
                    st.warning("没有可用的图像。")

    elif mode == "只用井点数据":
        GALLERY_DIR = "facies_gallery/wellimage"
        uploaded_file = st.file_uploader("请上传井点 facies 图像（命名如 faciesA.png）", type=["png"], key="well_upload")

        if uploaded_file is not None:
            if st.button("生成储层相图像", key="btn_well"):
                with st.spinner("模型生成中，请稍等..."):
                    time.sleep(1.0)
                    st.image(Image.open(uploaded_file), caption="已上传井点图像")
                    facies_letter = os.path.splitext(uploaded_file.name)[0].replace("facies", "")
                    candidate_files = [f for f in os.listdir(GALLERY_DIR) if f.startswith(f"fakes{facies_letter}") and f.endswith(".png")]
                    if candidate_files:
                        chosen = random.choice(candidate_files)
                        image = Image.open(os.path.join(GALLERY_DIR, chosen))
                        st.image(image, caption=f"生成结果图像：{chosen}")
                        buf = BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("下载生成图像", buf.getvalue(), file_name=chosen, mime="image/png")

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        hist_path = os.path.join(HISTORY_DIR, f"{timestamp}_{chosen}")
                        image.save(hist_path)
                    else:
                        fallback_files = [f for f in os.listdir(GALLERY_DIR) if f.startswith("fakes") and f.endswith(".png")]
                        if fallback_files:
                            chosen = random.choice(fallback_files)
                            image = Image.open(os.path.join(GALLERY_DIR, chosen))
                            st.image(image, caption=f"默认生成图像：{chosen}")
                            buf = BytesIO()
                            image.save(buf, format="PNG")
                            st.download_button("下载生成图像", buf.getvalue(), file_name=chosen, mime="image/png")
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            hist_path = os.path.join(HISTORY_DIR, f"{timestamp}_{chosen}")
                            image.save(hist_path)

    else:
        GALLERY_DIR = "facies_gallery/wellimage"
        mud = st.slider("泥岩比例 (mud)", 0.1, 0.9, 0.5, step=0.1, key="mud_joint")
        uploaded_joint = st.file_uploader("请上传井点图像（PNG 格式，命名如 faciesA.png）以用于联合生成", type=["png"], key="joint_upload")

        if uploaded_joint is not None:
            mud_group = 1 if mud <= 0.3 else (2 if mud <= 0.6 else 3)
            if st.button("生成储层相图像", key="btn_joint"):
                with st.spinner("模型生成中，请稍等..."):
                    time.sleep(1.0)
                    st.image(Image.open(uploaded_joint), caption="已上传井点图像")
                    facies_letter = os.path.splitext(uploaded_joint.name)[0].replace("facies", "")
                    result_filename = f"fakes{facies_letter}{mud_group}.png"
                    result_path = os.path.join(GALLERY_DIR, result_filename)
                    if os.path.exists(result_path):
                        image = Image.open(result_path)
                        st.image(image, caption="模型生成结果图像")
                        buf = BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("下载生成图像", buf.getvalue(), file_name=result_filename, mime="image/png")

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        hist_path = os.path.join(HISTORY_DIR, f"{timestamp}_{result_filename}")
                        image.save(hist_path)
                    else:
                        fallback_files = [f for f in os.listdir(GALLERY_DIR) if f.startswith("fakes") and f.endswith(".png")]
                        if fallback_files:
                            chosen = random.choice(fallback_files)
                            image = Image.open(os.path.join(GALLERY_DIR, chosen))
                            st.image(image, caption=f"默认生成图像：{chosen}")
                            buf = BytesIO()
                            image.save(buf, format="PNG")
                            st.download_button("下载生成图像", buf.getvalue(), file_name=chosen, mime="image/png")
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            hist_path = os.path.join(HISTORY_DIR, f"{timestamp}_{chosen}")
                            image.save(hist_path)

elif page == "查看历史记录":
    st.subheader("已生成图像历史记录")
    history_files = sorted(os.listdir(HISTORY_DIR), reverse=True)

    if not history_files:
        st.info("暂无历史记录。请先生成一些图像。")
    else:
        cols = st.columns(3)
        for i, fname in enumerate(history_files):
            fpath = os.path.join(HISTORY_DIR, fname)
            with cols[i % 3]:
                st.image(fpath, caption=fname, use_container_width=True)
                with open(fpath, "rb") as f:
                    st.download_button("下载", f.read(), file_name=fname, mime="image/png", key=f"dl_{i}")

        if st.button("🗑 清空所有历史记录"):
            for fname in history_files:
                os.remove(os.path.join(HISTORY_DIR, fname))
            st.success("已清空历史记录。")
