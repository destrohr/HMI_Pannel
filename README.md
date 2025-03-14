This is a university coursework project where you can control generator parameters that influence the heating process. The app allows you to adjust settings like power, voltage, and current to optimize heating for different applications. The panel is built using Streamlit on Python.
And if you're wondering how to use this (I was in the same boat when i first started using Git) here are the steps to get you going:

Anyone can Run this 4 simple steps.

1. First, clone the project from GitHub. You can grab the link from the profile and run this in your terminal: 
    "git clone https://github.com/destrohr/HMI_Pannel"
   
2.  Navigate to the Folder. After cloning, go to the project folder: 
    **cd HMI_pannel**

3. Install Dependencies
   You will need to install some Python packages. Use this command: 
   **pip install -r requirements.txt**
   
4. Run the Web App
   Now go ahead and run the app. Just click on Web.py and then execute with below command:  This will open the window 
   **streamlit run web.py**

**HMI Snippet**
![image](https://github.com/user-attachments/assets/83be4b0c-13ae-42b2-9b50-5a666bc37201)

This HMI has 2 modes simplea nd advance allowing user to select their modes based on their usage.
The simple mode hase only power and time which can be saved in a seperate DB for furter reference.
For this operation we used SQlite.
