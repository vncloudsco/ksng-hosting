function k_autorenewal() {
	local CRONFILE=/var/spool/cron/root
	local opt=$1
	local arg=$2
	local MSG
	
	test -f $CRONFILE && cat $CRONFILE | grep "/usr/bin/kusanagi update cert" 2>&1 > /dev/null
	local FOUND=$?
	if [[ $arg =~ ^on ]] ; then
		if [ "$FOUND" -eq 0 ] ; then
			MSG=$(eval_gettext "Auto renewal certificate is already enabled. Nothing to do.")
		else
			local FULL=$(find /etc/letsencrypt/live -type l -name fullchain.pem)
			if [ -n "$FULL" ] ; then
				# run update certificates at 03:07 every monday.
				echo "07 03 * * 0 /usr/bin/kusanagi update cert" >> $CRONFILE
				MSG=$(eval_gettext "Enabling auto renewal certificate")
			else
				MSG=$(eval_gettext "Auto renewal certificate is already enabled. Nothing to do.")
			fi	
		fi
	elif [[ $arg =~ ^off ]] ; then
		if [ "$FOUND" -eq 0 ] ; then
			sed -i "/\/usr\/bin\/kusanagi update cert/d" $CRONFILE
			MSG=$(eval_gettext "Disabling auto renewal certificate")
		else
			MSG=$(eval_gettext "Auto renewal certificate is already disabled. Nothing to do.")
		fi
	else
		echo $(eval_gettext "Cannot use \$arg.")
		echo $(eval_gettext "kusanagi \$opt [on|off].")
		return 1
	fi
	echo $arg | grep quiet 2>&1 > /dev/null 
	[ $? -eq 1 -a -n "$MSG" ] && echo $MSG
	return 0
}
