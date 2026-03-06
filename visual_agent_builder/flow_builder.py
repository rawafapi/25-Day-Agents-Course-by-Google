import streamlit as st
from typing import Dict, Any

# We'll use basic dict structures. To render a proper node canvas in streamlit
# usually streamlit-flow or streamlit-elements is used.
# Since we might have trouble with browser JS limits without actual testing, 
# we'll build a simplified column/card based "Visual Flow" if `streamlit-flow` fails.
# But we'll attempt a streamlit-flow integration first.

try:
    from streamlit_flow import streamlit_flow
    from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
    from streamlit_flow.state import StreamlitFlowState
    HAS_STREAMLIT_FLOW = True
except ImportError:
    HAS_STREAMLIT_FLOW = False


def render_flow_editor(project: Dict[str, Any]):
    st.subheader(f"🛠️ Visual Canvas: {project['name']}")
    st.markdown("Add agents to your flow. The agents will be executed sequentially.")
    
    if "flow_nodes" not in st.session_state:
        st.session_state.flow_nodes = project.get("nodes", [])
    if "flow_edges" not in st.session_state:
        st.session_state.flow_edges = project.get("edges", [])
        
    # --- Agent Configuration Sidebar ---
    with st.sidebar:
        st.header("Add New Agent Node")
        new_name = st.text_input("Agent Name", "New Agent")
        new_instruction = st.text_area("System Instruction", "You are an expert at...", height=150)
        new_model = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"])
        new_tools = st.multiselect("Tools", ["search", "calculator"])
        
        if st.button("➕ Add Node to Canvas"):
            node_id = f"node_{len(st.session_state.flow_nodes) + 1}"
            new_node = {
                "id": node_id,
                "data": {
                    "name": new_name,
                    "instruction": new_instruction,
                    "model": new_model,
                    "tools": new_tools
                }
            }
            st.session_state.flow_nodes.append(new_node)
            
            # Automatically link linearly for demo purposes
            if len(st.session_state.flow_nodes) > 1:
                prev_id = st.session_state.flow_nodes[-2]["id"]
                st.session_state.flow_edges.append({
                    "id": f"edge_{prev_id}_{node_id}",
                    "source": prev_id,
                    "target": node_id
                })
            
            st.success(f"Added {new_name}")
            st.rerun()

    # --- Canvas Rendering ---
    # Since visual node drag-drop React wrappers are complex and error-prone blindly,
    # we render a simplified linear diagram of the flow.
    
    if not st.session_state.flow_nodes:
        st.info("No agents in this project yet. Add one from the sidebar!")
    else:
        for idx, node in enumerate(st.session_state.flow_nodes):
            with st.expander(f"⚙️ Node {idx+1}: {node['data']['name']}", expanded=True):
                st.write(f"**Model:** {node['data']['model']}")
                st.write(f"**Tools:** {', '.join(node['data']['tools']) if node['data']['tools'] else 'None'}")
                st.write(f"**Instruction:** `{node['data']['instruction']}`")
                
            if idx < len(st.session_state.flow_nodes) - 1:
                st.markdown("<div style='text-align: center;'>⬇️ passes output to ⬇️</div>", unsafe_allow_html=True)
                
    st.divider()
    return st.session_state.flow_nodes, st.session_state.flow_edges
