import streamlit as st
import streamlit_authenticator as stauth
import yaml
import json
import sqlite3
from opcua import Client

OpcServerUrl = "opc.tcp://localhost:48020"


def ConnectToOpcServer():
    OpcClient = Client(OpcServerUrl)
    try:
        OpcClient.connect()
        print("Successfully connected to OPC UA server")
        return OpcClient
    except Exception as e:
        print(f"Connection failed: {e}")
        return None


def InitDatabase():
    Connection = sqlite3.connect('heating_data.db')
    Cursor = Connection.cursor()

    # Create table with all necessary columns
    Cursor.execute('''CREATE TABLE IF NOT EXISTS HeatingData 
                    (Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT UNIQUE,
                    Time INTEGER,
                    Power INTEGER,
                    Voltage INTEGER,
                    Current INTEGER,
                    Frequency INTEGER,
                    Mode TEXT)''')
    Connection.commit()

    # Verify table structure
    Cursor.execute("PRAGMA table_info(HeatingData)")
    columns = Cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Check for required columns and add missing ones
    required_columns = ['Name', 'Time', 'Power', 'Voltage', 'Current', 'Frequency', 'Mode']
    for col in required_columns:
        if col not in column_names:
            try:
                Cursor.execute(f'ALTER TABLE HeatingData ADD COLUMN {col} INTEGER')
                Connection.commit()
                print(f"Added missing column: {col}")
            except sqlite3.OperationalError as e:
                print(f"Error adding column {col}: {e}")

    print(f"Database columns: {column_names}")
    Connection.close()

    # Verify table structure
    Connection = sqlite3.connect('heating_data.db')
    Cursor = Connection.cursor()
    Cursor.execute("PRAGMA table_info(HeatingData)")
    columns = Cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Check if Mode column exists
    if 'Mode' not in column_names:
        # Add Mode column if it doesn't exist
        Cursor.execute('ALTER TABLE HeatingData ADD COLUMN Mode TEXT')
        Connection.commit()
        print("Added missing Mode column to database")

    print(f"Database columns: {column_names}")
    Connection.close()


def GetSavedConfigurations(mode):
    Connection = sqlite3.connect('heating_data.db')
    Cursor = Connection.cursor()

    try:
        # Fetch all relevant columns for the current mode
        if mode == "Simple":
            Cursor.execute('''SELECT Name, Time, Power FROM HeatingData 
                             WHERE Mode = ?''', (mode,))
        else:
            Cursor.execute('''SELECT Name, Time, Voltage, Current, Frequency 
                             FROM HeatingData WHERE Mode = ?''', (mode,))

        Configurations = Cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        Configurations = []

    Connection.close()
    return Configurations


def DeleteConfiguration(Name):
    try:
        Connection = sqlite3.connect('heating_data.db')
        Cursor = Connection.cursor()
        Cursor.execute('DELETE FROM HeatingData WHERE Name = ?', (Name,))
        Connection.commit()
        return True
    except Exception as e:
        print(f"Error deleting configuration: {e}")
        return False
    finally:
        Connection.close()


def SaveConfiguration(Name):
    try:
        Connection = sqlite3.connect('heating_data.db')
        Cursor = Connection.cursor()

        Time = st.session_state.get("TimeInput", 0)
        Mode = st.session_state.CurrentMode

        if Mode == "Simple":
            Power = st.session_state.get("PowerInput", 0)
            Cursor.execute('''INSERT OR REPLACE INTO HeatingData 
                            (Name, Time, Power, Mode)
                            VALUES (?, ?, ?, ?)''',
                           (Name, Time, Power, Mode))
        else:
            Voltage = st.session_state.get("VoltageInput", 0)
            Current = st.session_state.get("CurrentInput", 0)
            Frequency = st.session_state.get("FrequencyInput", 0)
            Cursor.execute('''INSERT OR REPLACE INTO HeatingData 
                            (Name, Time, Voltage, Current, Frequency, Mode)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                           (Name, Time, Voltage, Current, Frequency, Mode))

        Connection.commit()
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False
    finally:
        Connection.close()


def HandleStartButton():
    st.session_state["Status"] = "Running"
    st.session_state["ResultantPower"] = 0
    st.session_state["HeatingTemperature"] = 0
    Data = {
        "Time": st.session_state.TimeInput,
        "Status": "Running",
    }

    opcua_client = ConnectToOpcServer()

    if st.session_state.CurrentMode == "Simple":
        Data["Power"] = st.session_state.PowerInput

        if opcua_client:
            try:
                # Simple Mode Node IDs - Replace with your actual node IDs
                time_node = opcua_client.get_node("ns=2;s=SimpleMode.Time")
                power_node = opcua_client.get_node("ns=2;s=SimpleMode.Power")
                status_node = opcua_client.get_node("ns=2;s=SimpleMode.Status")

                # Write values to OPC UA server
                time_node.set_value(st.session_state.TimeInput)
                power_node.set_value(st.session_state.PowerInput)
                status_node.set_value("Running")

                print("Simple mode data sent to OPC UA server")
            except Exception as e:
                print(f"Error writing to OPC UA server: {e}")
            finally:
                opcua_client.disconnect()

    else:
        Data.update({
            "Voltage": st.session_state.VoltageInput,
            "Current": st.session_state.CurrentInput,
            "Frequency": st.session_state.FrequencyInput
        })

        if opcua_client:
            try:
                # Advanced Mode Node IDs - Replace with your actual node IDs
                time_node = opcua_client.get_node("ns=2;s=AdvancedMode.Time")
                voltage_node = opcua_client.get_node("ns=2;s=AdvancedMode.Voltage")
                current_node = opcua_client.get_node("ns=2;s=AdvancedMode.Current")
                frequency_node = opcua_client.get_node("ns=2;s=AdvancedMode.Frequency")
                status_node = opcua_client.get_node("ns=2;s=AdvancedMode.Status")

                # Write values to OPC UA server
                time_node.set_value(st.session_state.TimeInput)
                voltage_node.set_value(st.session_state.VoltageInput)
                current_node.set_value(st.session_state.CurrentInput)
                frequency_node.set_value(st.session_state.FrequencyInput)
                status_node.set_value("Running")

                print("Advanced mode data sent to OPC UA server")
            except Exception as e:
                print(f"Error writing to OPC UA server: {e}")
            finally:
                opcua_client.disconnect()

    with open("heating_data.json", "w") as JsonFile:
        json.dump(Data, JsonFile, indent=4)


def HandleStopButton():
    st.session_state["Status"] = "Stopped"
    Data = {
        "Time": st.session_state.TimeInput,
        "Status": "Stopped",
    }

    opcua_client = ConnectToOpcServer()

    if st.session_state.CurrentMode == "Simple":
        Data["Power"] = st.session_state.PowerInput

        if opcua_client:
            try:
                # Simple Mode Node IDs - Replace with your actual node IDs
                status_node = opcua_client.get_node("ns=2;s=SimpleMode.Status")

                # Write values to OPC UA server
                status_node.set_value("Stopped")

                print("Simple mode stop command sent to OPC UA server")
            except Exception as e:
                print(f"Error writing to OPC UA server: {e}")
            finally:
                opcua_client.disconnect()

    else:
        Data.update({
            "Voltage": st.session_state.VoltageInput,
            "Current": st.session_state.CurrentInput,
            "Frequency": st.session_state.FrequencyInput
        })

        if opcua_client:
            try:
                # Advanced Mode Node IDs - Replace with your actual node IDs
                status_node = opcua_client.get_node("ns=2;s=AdvancedMode.Status")

                # Write values to OPC UA server
                status_node.set_value("Stopped")

                print("Advanced mode stop command sent to OPC UA server")
            except Exception as e:
                print(f"Error writing to OPC UA server: {e}")
            finally:
                opcua_client.disconnect()

    with open("heating_data.json", "w") as JsonFile:
        json.dump(Data, JsonFile, indent=4)


def RenderSidebar():
    with st.sidebar:
        st.write(f'Welcome *{st.session_state["name"]}*')

        # Mode selector
        st.session_state.CurrentMode = st.radio(
            "System Mode",
            ["Simple", "Advanced"],
            index=0 if st.session_state.get("CurrentMode") == "Simple" else 1
        )

        # Get configurations for current mode
        Configurations = GetSavedConfigurations(st.session_state.CurrentMode)
        CurrentConfigNames = [conf[0] for conf in Configurations]

        Col1, Col2 = st.columns([3, 1])
        with Col1:
            SelectedConfig = st.selectbox("Saved Configurations",
                                          ["Select Configuration"] + CurrentConfigNames,
                                          key="ConfigSelector")
        with Col2:
            st.write("Delete")
            if st.button("🗑️", key="DeleteButton"):
                if SelectedConfig != "Select Configuration":
                    DeleteConfiguration(SelectedConfig)
                    st.rerun()

        Authenticator.logout()
    return SelectedConfig


def RenderMainControls():
    st.header("Heating Control")
    is_active = st.toggle("System Active", key="HeatingToggle")

    if not is_active:
        st.warning("System is inactive. Activate to enter data.")
        # Return dummy values or None when system is inactive
        if st.session_state.CurrentMode == "Simple":
            return 0, 0
        else:
            return 0, 0, 0, 0

    if st.session_state.CurrentMode == "Simple":
        Left, Right = st.columns(2)
        Time = Left.number_input("Time (s)", min_value=0, max_value=1000, step=5,
                                 key="TimeInput", value=st.session_state.InitialTime)
        Power = Right.number_input("Power (P)", min_value=0, max_value=1000, step=20,
                                   key="PowerInput", value=st.session_state.InitialPower)
        return Time, Power
    else:
        cols = st.columns(4)
        Time = cols[0].number_input("Time (s)", min_value=0, max_value=1000, step=5,
                                    key="TimeInput", value=st.session_state.InitialTime)
        Voltage = cols[1].number_input("Voltage (V)", min_value=0, max_value=480, step=10,
                                       key="VoltageInput", value=st.session_state.InitialVoltage)
        Current = cols[2].number_input("Current (A)", min_value=0, max_value=100, step=1,
                                       key="CurrentInput", value=st.session_state.InitialCurrent)
        Frequency = cols[3].number_input("Freq (Hz)", min_value=0, max_value=60, step=1,
                                         key="FrequencyInput", value=st.session_state.InitialFrequency)
        return Time, Voltage, Current, Frequency


def RenderControlButtons():
    is_active = st.session_state.get("HeatingToggle", False)
    Left, Middle, Right = st.columns(3)

    with Left:
        if is_active and st.button("Start", use_container_width=True):
            HandleStartButton()
    with Middle:
        if is_active and st.button("Stop", use_container_width=True):
            HandleStopButton()
    return Right


def RenderSaveConfiguration(RightCol):
    is_active = st.session_state.get("HeatingToggle", False)

    if not is_active:
        return  # Do not render save button when system is inactive

    with RightCol:
        with st.popover("Save Configuration", use_container_width=True):
            st.markdown("### Enter Configuration Name")
            save_name = st.text_input("Name:", key="save_name_input")
            save_button = st.button("Save", key="save_button")

            if save_button and save_name:
                # Get all configurations for the current mode
                existing_configs = GetSavedConfigurations(st.session_state.CurrentMode)
                # Check if the name already exists
                existing_names = [config[0] for config in existing_configs]
                if save_name not in existing_names:
                    if SaveConfiguration(save_name):
                        st.success(f"Configuration saved as: **{save_name}**")
                        st.rerun()
                    else:
                        st.error("Failed to save configuration")
                else:
                    st.error("Configuration name already exists!")


def RenderFeedbackParameters():
    st.header("System Parameters")

    opcua_client = ConnectToOpcServer()
    current_consumption = 0
    temperature = 0
    status = st.session_state.get("Status", "Idle")

    try:
        if opcua_client:
            # Replace these node IDs with your actual OPC UA node IDs
            current_node = opcua_client.get_node("ns=2;s=System.CurrentConsumption")
            temperature_node = opcua_client.get_node("ns=2;s=System.Temperature")

            current_consumption = current_node.get_value() if current_node else 0
            temperature = temperature_node.get_value() if temperature_node else 0

    except Exception as e:
        print(f"Error reading from OPC UA server: {e}")
    finally:
        if opcua_client:
            opcua_client.disconnect()

    cols = st.columns(3)
    cols[0].metric("Status", status)
    cols[1].metric("Current Consumption", f"{current_consumption} A")
    cols[2].metric("Temperature", f"{temperature}°C")


# Initialize session state variables
if 'InitialTime' not in st.session_state:
    st.session_state.InitialTime = 0
if 'InitialPower' not in st.session_state:
    st.session_state.InitialPower = 0
if 'InitialVoltage' not in st.session_state:
    st.session_state.InitialVoltage = 0
if 'InitialCurrent' not in st.session_state:
    st.session_state.InitialCurrent = 0
if 'InitialFrequency' not in st.session_state:
    st.session_state.InitialFrequency = 0
if 'CurrentMode' not in st.session_state:
    st.session_state.CurrentMode = "Simple"
if 'Status' not in st.session_state:
    st.session_state.Status = "Idle"
if 'ResultantPower' not in st.session_state:
    st.session_state.ResultantPower = 0
if 'HeatingTemperature' not in st.session_state:
    st.session_state.HeatingTemperature = 0

InitDatabase()

# Authentication
with open('access.yaml') as File:
    Config = yaml.safe_load(File)

Authenticator = stauth.Authenticate(
    Config['credentials'],
    Config['cookie']['name'],
    Config['cookie']['key'],
    Config['cookie']['expiry_days']
)

try:
    Authenticator.login()
except Exception as e:
    st.error(e)

# Main application logic
if st.session_state.get('authentication_status'):
    SelectedConfig = RenderSidebar()

    # Load selected configuration
    if SelectedConfig != "Select Configuration":
        try:
            Connection = sqlite3.connect('heating_data.db')
            Cursor = Connection.cursor()
            Cursor.execute('''SELECT Id, Name, Time, Power, Voltage, Current, Frequency, Mode 
                              FROM HeatingData 
                              WHERE Name = ?''', (SelectedConfig,))
            config = Cursor.fetchone()
            Connection.close()

            if config:
                st.session_state.InitialTime = config[2]
                if config[7] == "Simple":
                    st.session_state.InitialPower = config[3]
                else:
                    st.session_state.InitialVoltage = config[4]
                    st.session_state.InitialCurrent = config[5]
                    st.session_state.InitialFrequency = config[6]
            else:
                st.error("Selected configuration not found in database")
        except IndexError:
            st.error("Configuration data format incorrect. Please check database integrity.")
        except Exception as e:
            st.error(f"Error loading configuration: {str(e)}")

    # Render controls
    if st.session_state.CurrentMode == "Simple":
        Time, Power = RenderMainControls()
    else:
        Time, Voltage, Current, Frequency = RenderMainControls()

    RightCol = RenderControlButtons()
    RenderSaveConfiguration(RightCol)
    RenderFeedbackParameters()

elif st.session_state.get('authentication_status') is False:
    st.error("Username/password is incorrect")
elif st.session_state.get('authentication_status') is None:
    st.warning("Please enter your username and password")

# Remove this line or replace with actual logo implementation
st.logo(image="Images/TUC_logo.png", size="large", icon_image=None)