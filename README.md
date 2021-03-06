

# What is this?
    
This is an environment for presenting and testing of intrusion detection systems (IDS) using system calls.
It consists of three parts.
    
**1. Webserver running OWASP juice-shop webserver --> Vulnerable Application**
    ![OWASP Juice Shop](/images/JuiceShop2.png)

**2. Backend handling reading of syscalls and actual IDS**

    1. IDS uses demo_stide, which forms ngrams of syscalls and saves them in a dictionary
        Depending on how many ngrams of syscalls are previously saved in the dictionary,
        an anomaly score is calculated.
    2. Below a path of one syscall triggered by the juice-shop application is shown.
 ![Path of a System-Call](/Explanations/syscall_dataflow.svg)

**3. React Frontend for visualization of IDS**
    ![OWASP Juice Shop](/images/Dashboard.png)

    1. Graphs:

        1. Plot showing system calls in last second
        2. Plot showing current probability of an intrusion 
        3. PiePlot showing distribution of all seen system calls
        4. PiePlot showing distribution of seen ngrams during training

    2. Available Actions

        1. User Actions
            * Start/Stop automated user 
                * Consists of :
                    * Register user 
                    * Login user
                    * Go shopping (put items into basket)
                    * Leave feedback
                    * Logout 
            * Launch perfect/realistic SQLInjection
        2. Model Modifications
            * Retrain model with specific training size

**Prerequisites**
* Preferably clean installation of Ubuntu 18.04LTS
* Clone repo and switch to dev-branch

**How do I install the environment?**
* Run: ./installDemo.sh
* (observe installation and accept or decline sharing of user statistics for angular (twice))

**How do I run the environment?**
* Run: tmuxp load startDemo.yaml
* Alternativly: 
    * Terminal 1: 
        * cd demo-app
        * npm start
    * Terminal 2:
        * python3 backend.py
* Monitoring: http://localhost:3001/
* Web-App: http://localhost:3000/
