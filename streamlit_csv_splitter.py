import streamlit as st
import io
import os

st.set_page_config(page_title="CSV / TSV Row Splitter", layout="centered")

st.title("CSV / TSV Row Splitter")
st.write("Split large CSV / TSV files by number of rows (Japanese supported)")

# ================= Encoding detection =================
def detect_encoding(file_bytes):
    for enc in ("utf-8", "cp932", "shift_jis"):
        try:
            file_bytes.decode(enc)
            return enc
        except:
            pass
    return "utf-8"

# ================= Split logic =================
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

# ================= UI =================
uploaded_file = st.file_uploader(
    "Upload CSV / TSV file",
    type=["csv", "tsv", "txt"]
)

rows = st.number_input(
    "Rows per output file",
    min_value=1,
    value=100000,
    step=1000
)

if uploaded_file:
    file_bytes = uploaded_file.read()

    if st.button("Split File"):
        with st.spinner("Splitting file..."):
            parts, encoding_used = split_by_rows(
                file_bytes,
                rows,
                uploaded_file.name
            )

        st.success(f"Done! Created {len(parts)} files (Encoding: {encoding_used})")

        for name, data in parts:
            st.download_button(
                label=f"Download {name}",
                data=data,
                file_name=name,
                mime="text/csv"
            )
