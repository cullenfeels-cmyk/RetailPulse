import streamlit as st

# -----------------------------
# LOGIN FUNCTION
# -----------------------------
def login():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    st.markdown(
        """
        <h1 style='text-align:center;color:#2563EB;'>
        🔐 RetailPulse AI Login
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    st.write("")

    if st.button("Login"):

        if username == "admin" and password == "admin123":

            st.session_state.logged_in = True

            st.success("Login Successful")

            st.rerun()

        else:

            st.error("Invalid Username or Password")

    return False