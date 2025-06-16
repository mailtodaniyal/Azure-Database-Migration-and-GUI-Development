import streamlit as st
import pandas as pd
from pyvis.network import Network
import tempfile
import streamlit.components.v1 as components
import uuid

st.set_page_config(page_title="Client Demo – Web DB GUI", layout="wide")

users = [
    {"id": str(uuid.uuid4()), "username": "alice", "role": "admin"},
    {"id": str(uuid.uuid4()), "username": "bob", "role": "user"},
]

items = [
    {"id": str(uuid.uuid4()), "name": "Customer A", "description": "Top-tier client"},
    {"id": str(uuid.uuid4()), "name": "Project X", "description": "Important initiative"},
    {"id": str(uuid.uuid4()), "name": "Invoice #123", "description": "Pending payment"},
]

relations = [
    {"source_id": items[0]["id"], "target_id": items[1]["id"]},
    {"source_id": items[1]["id"], "target_id": items[2]["id"]},
]

def render_network():
    net = Network(height="500px", width="100%", directed=True)
    for item in items:
        net.add_node(item["id"], label=item["name"], title=item["description"])
    for rel in relations:
        net.add_edge(rel["source_id"], rel["target_id"])
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(temp_file.name)
    return temp_file.name

st.title("📊 Cloud-Based Database GUI Demo")

menu = st.sidebar.radio("Choose Section", ["Data Entry", "User Management", "Reports", "Visual Diagram"])

if menu == "Data Entry":
    st.subheader("➕ Add a New Record")
    new_name = st.text_input("Name")
    new_desc = st.text_area("Description")
    if st.button("Add Item"):
        new_item = {"id": str(uuid.uuid4()), "name": new_name, "description": new_desc}
        items.append(new_item)
        st.success(f"Added: {new_name}")
    st.subheader("🔗 Create a Relationship")
    names = [item["name"] for item in items]
    src = st.selectbox("Source", names, key="src")
    tgt = st.selectbox("Target", names, key="tgt")
    if st.button("Add Link"):
        src_id = next(i["id"] for i in items if i["name"] == src)
        tgt_id = next(i["id"] for i in items if i["name"] == tgt)
        relations.append({"source_id": src_id, "target_id": tgt_id})
        st.success(f"Linked {src} → {tgt}")

elif menu == "User Management":
    st.subheader("👥 Users")
    st.table(pd.DataFrame(users))

elif menu == "Reports":
    st.subheader("📄 Items")
    st.table(pd.DataFrame(items)[["name", "description"]])
    st.subheader("🔗 Relationships")
    rel_data = []
    for rel in relations:
        src = next(i["name"] for i in items if i["id"] == rel["source_id"])
        tgt = next(i["name"] for i in items if i["id"] == rel["target_id"])
        rel_data.append({"Source": src, "Target": tgt})
    st.table(pd.DataFrame(rel_data))

elif menu == "Visual Diagram":
    st.subheader("🕸️ Relationship Network")
    html_file = render_network()
    with open(html_file, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=600, scrolling=True)
