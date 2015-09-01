#Script to restart bisque server

#Enter the bisque directory.
cd /home/bw4sz/bisque/

#Activate the Bisque virtual environment (§3.2, step 5).
cd /home/bw4sz/bisque/engine
source bqenv/bin/activate
bq-admin server start 

echo "server restart"
