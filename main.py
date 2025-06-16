import streamlit as st
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import uuid

server = 'your_server.database.windows.net'
database = 'your_database'
username = 'your_username'
password = 'your_password'
driver = '{ODBC Driver 17 for SQL Server}'
conn_str = f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(conn_str)

def init_db():
    with engine.begin() as conn:
        conn.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        CREATE TABLE users (
            id UNIQUEIDENTIFIER PRIMARY KEY,
            username VARCHAR(50),
            role VARCHAR(20)
        )
        ''')
        conn.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='items' AND xtype='U')
        CREATE TABLE items (
            id UNIQUEIDENTIFIER PRIMARY KEY,
            name VARCHAR(100),
            description TEXT
        )
        ''')
        conn.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='relations' AND xtype='U')
        CREATE TABLE relations (
            id UNIQUEIDENTIFIER PRIMARY KEY,
            source_id UNIQUEIDENTIFIER,
            target_id UNIQUEIDENTIFIER,
            FOREIGN KEY (source_id) REFERENCES items(id),
            FOREIGN KEY (target_id) REFERENCES items(id)
        )
        ''')

def add_user(username, role):
    with engine.begin() as conn:
        conn.execute("INSERT INTO users (id, username, role) VALUES (?, ?, ?)", str(uuid.uuid4()), username, role)

def get_users():
    return pd.read_sql("SELECT * FROM users", engine)

def add_item(name, description):
    with engine.begin() as conn:
        conn.execute("INSERT INTO items (id, name, description) VALUES (?, ?, ?)", str(uuid.uuid4()), name, description)

def get_items():
    return pd.read_sql("SELECT * FROM items", engine)

def add_relation(source_id, target_id):
    with engine.begin() as conn:
        conn.execute("INSERT INTO relations (id, source_id, target_id) VALUES (?, ?, ?)", str(uuid.uuid4()), source_id, target_id)

def get_relations():
    return pd.read_sql("SELECT * FROM relations", engine)

def render_network():
    items = get_items()
    relations = get_relations()
    net = Network(height="500px", width="100%", directed=True)
    for _, row in items.iterrows():
        net.add_node(row['id'], label=row['name'])
    for _, row in relations.iterrows():
        net.add_edge(row['source_id'], row['target_id'])
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(temp_file.name)
    return temp_file.name

init_db()
st.title("Azure Database Migration – Streamlit App")

menu = st.sidebar.selectbox("Menu", ["Data Entry", "User Management", "Reporting", "Relationship Diagram"])

if menu == "Data Entry":
    st.header("Add New Item")
    name = st.text_input("Name")
    description = st.text_area("Description")
    if st.button("Add Item"):
        add_item(name, description)
        st.success("Item added")
    st.header("Create Relationship")
    items_df = get_items()
    source = st.selectbox("Source Item", items_df['name'])
    target = st.selectbox("Target Item", items_df['name'])
    if st.button("Add Relationship"):
        source_id = items_df[items_df['name'] == source]['id'].values[0]
        target_id = items_df[items_df['name'] == target]['id'].values[0]
        add_relation(source_id, target_id)
        st.success("Relationship added")

elif menu == "User Management":
    st.header("User Management")
    username = st.text_input("Username")
    role = st.selectbox("Role", ["admin", "user"])
    if st.button("Add User"):
        add_user(username, role)
        st.success("User added")
    users_df = get_users()
    st.dataframe(users_df)

elif menu == "Reporting":
    st.header("Items Overview")
    st.dataframe(get_items())
    st.header("Relationships Overview")
    rel_df = get_relations()
    items_df = get_items()
    merged = rel_df.merge(items_df, left_on='source_id', right_on='id', suffixes=('', '_source'))
    merged = merged.merge(items_df, left_on='target_id', right_on='id', suffixes=('_source', '_target'))
    report_df = merged[['name_source', 'name_target']]
    report_df.columns = ['Source', 'Target']
    st.dataframe(report_df)

elif menu == "Relationship Diagram":
    st.header("Visual Relationship Map")
    html_path = render_network()
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        components.html(html_content, height=550, scrolling=True)
