#Script to restart bisque server

#Enter the bisque directory.
cd /home/bw4sz/bisque/

#Activate the Bisque virtual environment (§3.2, step 5).
source bqenv/bin/activate

#Restart your engine.
bq-admin server restart

echo "server restart"
