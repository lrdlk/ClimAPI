FOR /L %%N IN () DO (
 ssh -p 443 -R0:127.0.0.1:80 -L4300:127.0.0.1:4300 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz^+force@free.pinggy.io
timeout /t 10)