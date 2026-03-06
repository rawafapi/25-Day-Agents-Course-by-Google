import streamlit as st
from storage import load_projects, create_project, get_project, save_flow, delete_project
from flow_builder import render_flow_editor
from agent_engine import execute_flow

st.set_page_config(page_title="Visual Agent Factory", layout="wide", page_icon="🤖")

def show_dashboard():
    st.title("🤖 Visual Agent Factory Dashboard")
    st.markdown("Create and manage your Multi-Agent projects here.")
    
    # Create new project
    with st.expander("➕ Create New Project"):
        new_name = st.text_input("Project Name")
        new_desc = st.text_area("Description")
        if st.button("Create Project"):
            if new_name:
                create_project(new_name, new_desc)
                st.success(f"Project '{new_name}' created!")
                st.rerun()
            else:
                st.error("Project name is required.")
                
    st.divider()
    st.subheader("Your Projects")
    
    projects = load_projects()
    if not projects:
        st.info("No projects yet. Create one above!")
        return

    # Display projects in a grid
    cols = st.columns(3)
    for i, p in enumerate(projects):
        with cols[i % 3]:
            st.card_container = st.container(border=True)
            with st.card_container:
                st.subheader(p["name"])
                st.write(p["description"])
                st.write(f"Agents defined: {len(p.get('nodes', []))}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Open Builder", key=f"open_{p['id']}", use_container_width=True):
                        st.session_state.current_project_id = p["id"]
                        st.session_state.flow_nodes = p.get("nodes", [])
                        st.session_state.flow_edges = p.get("edges", [])
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"del_{p['id']}", type="primary", use_container_width=True):
                        delete_project(p["id"])
                        st.rerun()

def show_builder():
    project_id = st.session_state.current_project_id
    project = get_project(project_id)
    
    if not project:
        st.error("Project not found.")
        if st.button("Back to Dashboard"):
            del st.session_state.current_project_id
            st.rerun()
        return

    cols = st.columns([1, 8, 1])
    with cols[0]:
        if st.button("⬅️ Back"):
            del st.session_state.current_project_id
            if "flow_nodes" in st.session_state: del st.session_state.flow_nodes
            if "flow_edges" in st.session_state: del st.session_state.flow_edges
            if "execution_result" in st.session_state: del st.session_state.execution_result
            st.rerun()
            
    with cols[2]:
        if st.button("💾 Save Flow", type="primary"):
            save_flow(project_id, st.session_state.flow_nodes, st.session_state.flow_edges)
            st.success("Project Saved!")

    # Render Builder UI
    nodes, edges = render_flow_editor(project)
    
    # Execution Block
    st.divider()
    st.subheader("🚀 Execute Workflow")
    initial_input = st.text_area("Initial Prompt / Task Input:", "Do some research on Artificial Intelligence.")
    
    if st.button("▶️ Run Pipeline", type="primary", use_container_width=True):
        with st.spinner("Compiling ADK Agents and Executing..."):
            result = execute_flow(nodes, edges, initial_input)
            st.session_state.execution_result = result
            
    if "execution_result" in st.session_state:
        st.subheader("📝 Execution Output")
        st.info(st.session_state.execution_result)

if __name__ == "__main__":
    if "current_project_id" not in st.session_state:
        show_dashboard()
    else:
        show_builder()
