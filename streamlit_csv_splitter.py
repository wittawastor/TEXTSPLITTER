import streamlit as st
import os

st.set_page_config(page_title="CSV / TSV Splitter", layout="centered")

st.title("CSV / TSV Splitter")
st.write("Split large CSV / TSV files by **rows** or **file size (MB)**")
st.write("Japanese (CP932 / Shift-JIS / UTF-8) supported")

# ================= Encoding detection =================
def detect_encoding(file_bytes):
    for enc in ("utf-8", "cp932", "shift_jis"):
        try:
            file_bytes.decode(enc)
            return enc
        except:
            pass
    return "utf-8"

# ================= Split by ROWS =================
def split_by_rows(file_bytes, rows_per_file, filename):
    encoding = detect_encoding(file_bytes)
    text = file_bytes.decode(encoding)

    lines = text.splitlines(keepends=True)
    header = lines[0]
    body = lines[1:]

    parts = []
    part_no = 1

    for i in range(0, len(body), rows_per_file):
        chunk = body[i:i + rows_per_file]
        content = header + "".join(chunk)
        out_name = f"{os.path.splitext(filename)[0]}_part{part_no}.csv"
        parts.append((out_name, content.encode(encoding)))
        part_no += 1

    return parts, encoding

# ================= Split by FILE SIZE =================
def split_by_size(file_bytes, max_mb, filename):
    encoding = detect_encoding(file_bytes)
    text = file_bytes.decode(encoding)

    lines = text.splitlines(keepends=True)
    header = lines[0]
    body = lines[1:]

    max_bytes = max_mb * 1024 * 1024
    header_bytes = len(header.encode(encoding))

    parts = []
    part_no = 1
    buffer = header
    current_size = header_bytes

    for line in body:
        line_size = len(line.encode(encoding))

        if current_size + line_size > max_bytes:
            out_name = f"{os.path.splitext(filename)[0]}_part{part_no}.csv"
            parts.append((out_name, buffer.encode(encoding)))
            part_no += 1
            buffer = header + line
            current_size = header_bytes + line_size
        else:
            buffer += line
            current_size += line_size

    if buffer.strip():
        out_name = f"{os.path.splitext(filename)[0]}_part{part_no}.csv"
        parts.append((out_name, buffer.encode(encoding)))

    return parts, encoding

# ================= UI =================
uploaded_file = st.file_uploader(
    "Upload CSV / TSV file",
    type=["csv", "tsv", "txt"]
)

split_mode = st.radio(
    "Split mode",
    ["By rows", "By file size (MB)"]
)

if split_mode == "By rows":
    rows = st.number_input(
        "Rows per output file",
        min_value=1,
        value=100000,
        step=1000
    )
else:
    max_mb = st.number_input(
        "Max file size per output (MB)",
        min_value=1,
        value=50,
        step=10
    )

if uploaded_file:
    file_bytes = uploaded_file.read()

    if st.button("Split File"):
        with st.spinner("Processing..."):
            if split_mode == "By rows":
                parts, enc = split_by_rows(
                    file_bytes,
                    rows,
                    uploaded_file.name
                )
            else:
                parts, enc = split_by_size(
                    file_bytes,
                    max_mb,
                    uploaded_file.name
                )

        st.success(
            f"Done! Created {len(parts)} files "
            f"(Encoding preserved: {enc})"
        )

        for name, data in parts:
            st.download_button(
                label=f"Download {name}",
                data=data,
                file_name=name,
                mime="text/csv"
            )
