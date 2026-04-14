import streamlit as st
import re


def is_strong_password(pw):
    if len(pw) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", pw):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", pw):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", pw):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*]", pw):
        return False, "Need at least one special character (!@#$%^&*)."
    return True, "Strong password!"


st.title("🔐 Password Manager")

website = st.text_input("Website")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

strong, message = is_strong_password(password)

if password:
    if strong:
        st.success(message)
    else:
        st.warning(message)

if st.button("Submit"):
    if not website or not email or not password:
        st.error("Fill all fields first.")
    elif not strong:
        st.error("Fix your password before submitting.")
    else:
        print(f"Website: {website}\nEmail: {email}\nPassword: {password}")
        st.success("Saved!")