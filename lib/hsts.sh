function k_hsts() {
	local opt=$1
	local arg=$2
	if [ "$arg" = "off" ] ; then
		echo $(eval_gettext "Disabling HSTS")
		echo $(eval_gettext "If you switch from weak or mid,It takes a lot of times for enable.")
		echo $(eval_gettext "And, Can not switch from high to off.")
		sed -i 's/set $hsts [12];/set $hsts 0;/g' $NGINX_HTTPS ; RET1=$?
		sed -i 's/Define hsts [12]/Define hsts 0/g' $HTTPD_HTTPS ; RET2=$?
	elif [ "$arg" = "weak" ] ; then
		echo $(eval_gettext "Enabling HSTS(not IncludeSubDomain)")
		echo $(eval_gettext "If you switch from mid,It takes a lot of times for enable.")
		echo $(eval_gettext "And, Can not switch from high to weak.")
		sed -i 's/set $hsts 0;/set $hsts 1;/g' $NGINX_HTTPS ; RET1=$?
		sed -i 's/Define hsts [02]/Define hsts 1/g' $HTTPD_HTTPS ; RET2=$?
	elif [ "$arg" = "mid" ] ; then
		echo $(eval_gettext "Enabling HSTS w/IncludeSubDomain (not Preloading)")
		echo $(eval_gettext "If you switch from weak,It takes a lot of times for enable.")
		echo $(eval_gettext "And, Can not switch from high to mid." )
		sed -i 's/set $hsts 0;/set $hsts 2;/g' $NGINX_HTTPS ; RET1=$?
		sed -i 's/Define hsts [01]/Define hsts 2/g' $HTTPD_HTTPS ; RET2=$?
	elif [ "$arg" = "high" ] ; then
		echo $(eval_gettext "Enabling HSTS w/IncludeSubDomain,Preloading")
		sed -i 's/set $hsts [012];/set $hsts 3;/g' $NGINX_HTTPS ; RET1=$?
		echo $(eval_gettext "Setting changed,Try to register HSTS Preloading List")
		local fqdn=$(k_get_fqdn $PROFILE)
		wget -q -O /dev/null https://hstspreload.appspot.com/submit/${fqdn}
	else
		echo $(eval_gettext "Cannot use \$arg.")
		echo $(eval_gettext "kusanagi \$opt [off|weak|mid|high].")
		return 1
	fi
}
