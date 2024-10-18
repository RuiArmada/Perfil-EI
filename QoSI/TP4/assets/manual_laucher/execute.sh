for file in $(doctl compute droplet list --format "PublicIPv4" --no-header); do
	ssh -o "StrictHostKeyChecking no" root@$file "killall python"
	scp ./config.yaml root@$file:/netlat/
	scp ./run.sh root@$file:/
	ssh root@$file "sh /run.sh </dev/null >/dev/null 2>&1 & disown -h"
done
