import streamlit as st
import streamlit_authenticator as stauth
import yaml
import json

st.logo(
    image="Images/TUC_logo.png", size="large", icon_image=None )

with open('access.yaml') as file:
    config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'])

try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state['authentication_status']:
    with st.sidebar:
          st.write(f'Welcome *{st.session_state["name"]}*')
          authenticator.logout()
          selected_page = st.radio("Mode", ["Manual", "Automatic"])
          #below is the simpel example to save teh parameters with sqlite.You can do it if ,it is required.
          #this will only show the drop down window in the sidebar. you need to chaneg some code if you add sqlite
          #st.sidebar.selectbox("Saved", ["A", "B", "C","D", "E", "F", "G", "H","I", "J", "K", "L", "M","N", "O", "P"], key="foo")

    if selected_page == "Manual":
        st.header("Manual Heating Control")


        def heating_toggle():
            on = st.toggle("Heating", key="heating_toggle")
            if on:
                st.write("Heating turned on")
            else:
                st.write("Heating turned off")
            return on
        heating_toggle()

        def columns():
            left, right = st.columns(2)
            time = left.number_input("Time (s)", min_value=0, max_value=1000, step=5, key="time_input")
            power = right.number_input("Power (P)", min_value=0, max_value=1000, step=20, key="power_input")
            return time, power
        columns()


#here the buttons are modifies to send json request, the chage will show in json file in repositrey. This can be modified in future.
        def start_button():
            left, middle, right = st.columns(3)
            with middle:
                start_clicked = st.button("Start", use_container_width=True)
            if start_clicked:
                time = st.session_state.get("time_input", 0)
                power = st.session_state.get("power_input", 0)
                heating_on = st.session_state.get("heating_toggle", False)
                data = {
                    "time": time,
                    "power": power,
                    "heating_on": heating_on,
                    "status": "Running" if heating_on else "Idle"
                }
                file_path = "heating_data.json"
                with open(file_path, "w") as json_file:
                    json.dump(data, json_file, indent=4)
        start_button()


        def stop_button():
            left, middle, right = st.columns(3)
            with middle:
                stop_clicked = st.button("Stop", use_container_width=True)
            if stop_clicked:
                time = st.session_state.get("time_input", 0)
                power = st.session_state.get("power_input", 0)
                heating_on = False
                data = {
                    "time": time,
                    "power": power,
                    "heating_on": heating_on,
                    "status": "Stopped"
                }
                file_path = "heating_data.json"
                with open(file_path, "w") as json_file:
                    json.dump(data, json_file, indent=4)

                st.warning("Heating process stopped and data updated in JSON.")
        stop_button()

    elif selected_page == "Automatic":

        st.header("Automatic Heating Control")
#the automatic button will display teh parameters from thh generator, but for now it has inputs value for demonstration purpose this will be change in future.
        def automatic_button():
            left, middle, right  = st.columns(3)
            with left:
                status = st.text_input("Status", placeholder="e.g., Idle")
            with middle:
                resultant_power = st.number_input("Resultant Power", min_value=0, max_value=1000, step=20)
            with right:
                heating_temperature = st.number_input("Heating Temperature ", min_value=0, max_value=1500, step=10)

            st.write("### Current Parameters:")
            st.write(f"**Status:** {status if status else 'Idle'}")
            st.write(f"**Resultant Power:** {resultant_power}")
            st.write(f"**Heating Temperature:** {heating_temperature} ")
            return status, resultant_power, heating_temperature,
        automatic_button()


elif st.session_state.get('authentication_status') is False:
    st.error("Username/password is incorrect")
elif st.session_state.get('authentication_status') is None:
    st.warning("Please enter your username and password")
