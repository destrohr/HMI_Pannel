
# Heating Control System

A Streamlit-based application for controlling and monitoring industrial heating systems with OPC UA integration.

## Features

- **User Authentication**: Secure login system using Streamlit Authenticator
- **Dual Control Modes**:
  - **Simple Mode**: Control heating with basic power and time parameters
  - **Advanced Mode**: Fine-tune with voltage, current, and frequency settings
- **Real-time Monitoring**: View system parameters including temperature, current consumption, and cooling metrics
- **Configuration Management**: Save, load, and delete heating configurations
- **OPC UA Integration**: Connect to industrial control systems via OPC UA protocol
- **SQLite Database**: Store configurations persistently

## Screenshots

### Login Screen
![Login Screen](https://github.com/user-attachments/assets/bc0eb42b-6196-4423-bbfa-a2cae27cdc10)

### Simple Control Mode
![Simple Mode](https://github.com/user-attachments/assets/12e73021-c4e5-4239-b65c-04d193b896e4)

### Advanced Control Mode
![Advanced Mode](https://github.com/user-attachments/assets/b9e3f0d4-7ea9-4c52-a02f-2f1930851d68)

## Dependencies

- [Streamlit](https://streamlit.io/)
- [Streamlit Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)
- [Python OPC UA](https://python-opcua.readthedocs.io/en/latest/)
- [SQLite3](https://docs.python.org/3/library/sqlite3.html)
- [PyYAML](https://pypi.org/project/PyYAML/)

## Installation

1. Clone this repository:
   ```bash
   git clone git clone https://github.com/destrohr/HMI_Pannel
   cd HMI_Pannel
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `access.yaml` file for authentication:(optional)
   ```yaml
   credentials:
     usernames:
       username1:
         email: user1@example.com
         name: User One
         password: hashedpassword1
       username2:
         email: user2@example.com
         name: User Two
         password: hashedpassword2
   cookie:
     name: heating_system_auth
     key: your_signature_key
     expiry_days: 30
   ```

4. Configure your OPC UA server settings:
   - Edit the `OpcServerUrl` variable in the code to point to your OPC server
   - Verify the node IDs match your OPC UA server structure

## Usage

1. Run the application:
   ```bash
   streamlit run Web.py
   ```

2. Log in using credentials from your `access.yaml` file

3. Select operation mode (Simple/Advanced)

4. Configure heating parameters and toggle system state

5. Start/Stop heating process and monitor parameters

6. Save configurations for future use

## System Requirements

- OPC UA Server running and accessible
- Python 3.7+
- Modern web browser

## Development

The application structure follows a modular approach with separate functions for:
- Database management
- OPC UA communication
- UI rendering
- Configuration handling

If extending the application, follow the established pattern for new features.




