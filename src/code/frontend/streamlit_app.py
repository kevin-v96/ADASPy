import streamlit as st
import requests

API_BASE_URL = "http://localhost:80"


def is_authenticated():
    return st.session_state.get('authenticated', False)


def authenticate_user(email, password):
    response = requests.post(f"{API_BASE_URL}/auth/login", json={"username": email, "password": password})
    if response.status_code == 200:
        st.session_state['token'] = response.json().get("token")
    return response


def signup_user(name, email, password):
    response = requests.post(f"{API_BASE_URL}/auth/signup", json={"username": name, "email": email, "password": password})
    if response.status_code == 201:
        st.session_state['token'] = response.json().get("access_token")
    return response


def create_team(team_name):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.post(f"{API_BASE_URL}/teams/create", json={"team_name": team_name}, headers=headers)
    return response


def get_teams():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{API_BASE_URL}/teams/", headers=headers)
    return response.json()


def manage_team_members(action, team_name, member_email):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    if action == "add":
        response = requests.post(f"{API_BASE_URL}/teams/invite_to_team",
                                 json={"team_name": team_name, "email": member_email}, headers=headers)
    else:
        response = requests.post(f"{API_BASE_URL}/teams/remove_member",
                                 json={"team_name": team_name, "email": member_email}, headers=headers)
    return response


def create_agent(agent_name, description, team_id=None):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    data = {"agent_name": agent_name, "description": description, "team_id": team_id}
    response = requests.post(f"{API_BASE_URL}/agents/create", json=data, headers=headers)
    return response


def get_agents(team_id):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{API_BASE_URL}/agents/?team_id={team_id}", headers=headers)
    return response.json()


def delete_agent(agent_name):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.post(f"{API_BASE_URL}/agents/delete", json={"agent_name": agent_name}, headers=headers)
    return response


def update_agent(agent_id, new_description):
    response = requests.put(f"{API_BASE_URL}/agents/update/{agent_id}", json={"description": new_description})
    return response

def login_signup_page():
    st.title("Login or Signup")

    choice = st.radio("Choose an option", ["Login", "Signup"])

    if choice == "Login":
        username = st.text_input("Username", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            response = authenticate_user(username, password)
            if response.status_code == 200:
                st.session_state['authenticated'] = True
                st.success("Logged in successfully!")
            else:
                st.error("Login failed. Please check your credentials.")

    elif choice == "Signup":
        name = st.text_input("Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Signup"):
            response = signup_user(name, email, password)
            if response.status_code == 201:
                st.session_state['authenticated'] = True
                st.success("Account created successfully!")
                st.experimental_rerun()
            else:
                st.error("Signup failed. Please try again.")


def team_management_page():
    if not is_authenticated():
        st.warning("Please log in or sign up to access this page.")
        return

    st.title("Team Management")

    team_name = st.text_input("Team Name")

    action = st.radio("Manage Team", ["Add Member", "Remove Member"])
    member_email = st.text_input("Member Email")

    if st.button(f"{action}"):
        response = manage_team_members(action.lower(), team_name, member_email)
        if response.status_code == 200:
            st.success(f"Member {action.lower()}ed successfully!")
        else:
            st.error(f"Failed to {action.lower()} member.")

    if st.button("Create Team"):
        response = create_team(team_name)
        if response.status_code == 201:
            st.success("Team created successfully!")
        else:
            st.error("Team creation failed.")

    teams = get_teams()
    if teams:
        selected_team = st.selectbox("Select Team", [team['name'] for team in teams])
    else:
        selected_team = None


def agent_management_page():
    if not is_authenticated():
        st.warning("Please log in or sign up to access this page.")
        return

    st.title("Agent Management")

    teams = get_teams()
    if teams:
        selected_team = st.selectbox("Select Team", [team['name'] for team in teams])
        team_id = next((team['id'] for team in teams if team['name'] == selected_team), None)
        agents = get_agents(team_id)
        st.write("Agents in this team:")
        agent_names = [agent['name'] for agent in agents]
        for agent in agents:
            st.write(agent['name'])

    else:
        st.warning("No teams found. You can only create agents.")
        team_id = None

    agent_name = st.text_input("Agent Name")
    agent_description = st.text_area("Agent Description")

    if st.button("Create Agent"):
        response = create_agent(agent_name, agent_description, team_id)
        if response.status_code == 201:
            st.success("Agent created successfully!")
        else:
            st.error("Agent creation failed.")

    selected_agent = st.selectbox("Select Agent to Update", agent_names) if agent_names else None

    if selected_agent:
        selected_agent_data = next(agent for agent in agents if agent['name'] == selected_agent)
        new_description = st.text_area("New Description", value=selected_agent_data['description'])

        if st.button("Update Agent"):
            response = update_agent(selected_agent_data['id'], new_description)
            if response.status_code == 200:
                st.success("Agent updated successfully!")
            else:
                st.error("Agent update failed.")

    delete_agent_name = st.text_input("Name of the Agent to delete")

    if st.button("Delete Agent"):
        response = delete_agent(delete_agent_name)
        if response.status_code == 200:
            st.success("Agent deleted successfully!")
        else:
            st.error("Agent deletion failed.")


def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Login/Signup", "Team Management", "Agent Management"])

    if page == "Login/Signup":
        login_signup_page()
    elif page == "Team Management":
        team_management_page()
    elif page == "Agent Management":
        agent_management_page()


if __name__ == "__main__":
    main()
