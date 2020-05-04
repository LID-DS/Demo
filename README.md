

What is this?
    
This is an environment for presenting and testing of intrusion detection systems (IDS) using system calls.
It consists of three parts.
    
1. Webserver running OWASP juice-shop webserver --> Vulnerable Application

2. Backend handling reading of syscalls and actual IDS

    2.1 IDS uses demo_stide, which forms ngrams of syscalls and saves them in dictionary

3. React Frontend for visualization of IDS 

    3.1 Graphs:

        3.1.1 Plot showing system calls in last second
        3.1.2 Plot showing current probability of an intrusion 
        3.1.3 PiePlot showing distribution of seen of all system calls
        3.1.4 PiePlot showing distribution of seen ngrams during training

    3.2 Available Actions

        3.2.1 User Actions
            -> Start/Stop automated user 
                -> Consists of :
                    * Register user 
                    * Login user
                    * Go shopping (put items into basket)
                    * Leave feedback
                    * Logout 
            -> Launch perfect/realistic SQLInjection
        3.2.2 Model Modifications
            -> Retrain model with specific training size
        

How do I install the environment?
1. run: ./startDemo.sh

How do I run the environment?
2. run: tmuxp load startDemo.yaml

