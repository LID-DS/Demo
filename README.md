

What is this?
    
This is an environment for presenting and testing of intrusion detection systems (IDS) using system calls.
It consists of three parts.
    
1. Webserver running OWASP juice-shop webserver
2. React Frontend for visualization of IDS
3. Backend handling reading of syscalls and actual IDS
    3.1 IDS uses demo_stide, which forms ngrams of syscalls and saves them in dictionary

How do I install the environment?
1. run startDemo.sh


How do I run the environment?
2. run tmuxp load startDemo.yaml
