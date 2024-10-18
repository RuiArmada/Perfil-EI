for file in $(doctl compute droplet list --format "PublicIPv4" --no-header); do
	ssh -o "StrictHostKeyChecking no" root@$file "killall python"
done
