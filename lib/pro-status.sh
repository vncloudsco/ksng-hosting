#!

## show brief provision information

function show_pro() {
	  #php7=`ps aux| grep $1| grep php7-fpm`
	  if [ -n "$1" ]; then
	  	local exist=`grep PROFILE /etc/kusanagi.d/profile.conf | grep $1  2>/dev/null`
	  	if [ -n "$exist" ]; then
	  		php7=`[ -n "$1" ] && systemctl is-active php7-fpm.$1 | grep active 2>&1 > /dev/null;echo $?`
	  		if [ $php7 -eq 0 ]; then
	      		echo "PHP7-FPM is running for $1"
	  		elif [ -f "/var/cache/hhvmd/$1.pid" ]; then
	      		echo "HHVM is running for $1"
	  		else
	      		echo "$1 is not running"
	  		fi
	  		HOME=`grep $1 /etc/kusanagi.d/profile.conf | grep KUSANAGI_DIR | cut -d'=' -f2`
	  		echo "DocumentRoot = "$HOME  
		else
			echo "Provision $1 does not exist "
		fi	
	  else
	  	echo "No input ! Please enter any provision ! "
	  fi	
}
#show_pro $1
