# KUSANAGI Setting
# 2016/03/14
#

# kusanagi setting [--fqdn example.com] [profile]

function k_setting() {
	local _PROV=1
	local FQDN OPT_FQDN
	local TARGET=$PROFILE
	for OPT in "$@"
	do
		# skip 1st argment "setting"
		if [ $_PROV ] ; then
			_PROV=
			continue
		elif [ $OPT_FQDN ] ; then
			FQDN=$OPT
			OPT_FQDN=
		else
			case "$OPT" in
				'--fqdn')
					OPT_FQDN=1
					;;
				-*)
					# SKIP if specified unknown option
					echo $(eval_gettext "Cannot use option \$OPT")
					return 1
					;;
				*)
					TARGET=$OPT
					break
			esac
		fi
	done

	# read profile
	[[ -v KUSANAGI_FQDN ]] || k_read_profile $TARGET dont

	if [ -z $FQDN ] ; then
		echo $(eval_gettext "Please use --fqdn option for specified FQDN.")
		return 1 
	fi

	local DOC_ROOT="${KUSANAGI_DIR}/DocumentRoot"
	## main 
	if [ "$KUSANAGI_FQDN" = "$FQDN" ] ; then
		echo $(eval_gettext "FQDN(\$KUSANAGI_FQDN) is already set")
		return
	fi
	# PREV ADDFQDN
	local ADDFQDN= ADD_NEWFQDN=
	local IS_ROOT_DOMAIN=$(is_root_domain $KUSANAGI_FQDN;echo $?)
	if [ "$IS_ROOT_DOMAIN" -eq 0 ] ; then
		ADDFQDN="www.${KUSANAGI_FQDN}"
	elif [ "$IS_ROOT_DOMAIN" -eq 1 ] ; then
		ADDFQDN=`echo $KUSANAGI_FQDN | cut -c 5-`
	fi
	# NEW ADDFQDN
	local IS_ROOT_DOMAIN=$(is_root_domain $FQDN;echo $?)
	if [ "$IS_ROOT_DOMAIN" -eq 0 ] ; then
		ADD_NEWFQDN="www.${FQDN}"
	elif [ "$IS_ROOT_DOMAIN" -eq 1 ] ; then
		ADD_NEWFQDN=`echo $FQDN | cut -c 5-`
	fi

	# WordPress db replace
	if [ "WordPress" = "${KUSANAGI_TYPE:-}" ] ; then
		local WP="sudo -u kusanagi -i -- /usr/local/bin/wp"
		$WP search-replace $KUSANAGI_FQDN $FQDN --path=$DOC_ROOT --all-tables > /dev/null
	fi
	# backup prev setting
	if [ -n "$ADDFQDN" ] ; then
		sed -i "s|https://$ADDFQDN\b|https://fqdn|" $NGINX_HTTP # for redirect
		sed -i "s/Server\(Name\|Alias\)\s\+$ADDFQDN/ServerAlias fqdn/" $HTTPD_HTTP
		sed -i "s/Server\(Name\|Alias\)\s\+$ADDFQDN/ServerAlias fqdn/" $HTTPD_HTTPS
	fi
	# replace OLD FQDN to NEW FQDN
	sed -i -e "s/server_name\s\+$KUSANAGI_FQDN\s*$ADDFQDN;/server_name $FQDN $ADD_NEWFQDN;/g" \
		-e "s|https://$KUSANAGI_FQDN\b|https://$FQDN|" $NGINX_HTTP
	sed -i -e "s/server_name\s\+$KUSANAGI_FQDN\s*$ADDFQDN;/server_name $FQDN $ADD_NEWFQDN;/g" $NGINX_HTTPS
	sed -i "s/ServerName\s\+$KUSANAGI_FQDN/ServerName $FQDN/" $HTTPD_HTTP
	sed -i "s/ServerName\s\+$KUSANAGI_FQDN/ServerName $FQDN/" $HTTPD_HTTPS
	# replace OLD ADD FQDN to NEW ADD FQDN
	if [ -n "$ADDFQDN" -a -n "$ADD_NEWFQDN" ] ; then
		sed -i "s|https://fqdn\b|https://$ADD_NEWFQDN|" $NGINX_HTTP # for redirect
		sed -i "s/ServerAlias\s\+fqdn/ServerAlias $ADD_NEWFQDN/" $HTTPD_HTTP
		sed -i "s/ServerAlias\s\+fqdn/ServerAlias $ADD_NEWFQDN/" $HTTPD_HTTPS
	else
		if [ -n "$ADDFQDN" ] ; then
			sed -i "/https:\/\/fqdn\b/d" $NGINX_HTTP # for redirect
			sed -i "/ServerAlias\s\+fqdn/d" $HTTPD_HTTP
			sed -i "/ServerAlias\s\+fqdn/d" $HTTPD_HTTPS
		elif [ -n "$ADD_NEWFQDN" ] ; then
			sed -i -e "/# SSL ONLY/a\	# rewrite ^(.*)$ https:\/\/$ADD_NEWFQDN\$request_uri permanent; # SSL ONLY/" $NGINX_HTTP
			sed -i "/^\s\+ServerName\s/a\	ServerAlias ${ADD_NEWFQDN}" $HTTPD_HTTP
			sed -i "/^\s\+ServerName\s/a\	ServerAlias ${ADD_NEWFQDN}" $HTTPD_HTTPS
		fi
	fi
	# replace rewrite setting if it has https redirect setting.
	if [ 0 -eq $(grep '^\s*rewrite \^(.*)$ https:' $NGINX_HTTP 2>&1 > /dev/null ; echo $?) ] ; then 
		sed -i "s/\(\s\+\)#\s*rewrite ^(.*)$ https:/\1rewrite ^(.*)$ https:/g" $NGINX_HTTP
	fi

	grep /etc/letsencrypt/live/"$KUSANAGI_FQDN"/ $HTTPD_HTTPS > /dev/null 2>&1
	if [ $? -eq 0 ] ; then
		echo $(eval_gettext "Please execute 'kusanagi ssl --email <YOUR EMAIL ADDRESS>' again.")
	else
		cat /etc/httpd/conf.d/"$TARGET"_ssl.conf | grep /etc/pki/ > /dev/null 2>&1
		if [ $? -eq 0 ] ; then 
			echo $(eval_gettext "You chose /etc/pki certificate, so not changed in server config.")
		else
			echo $(eval_gettext "=== WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN ===")
			echo $(eval_gettext "Your certificate config in /etc/""[nginx|httpd]/conf.d/\${TARGET}_ssl.conf was not changed.")
			echo $(eval_gettext "Please change certificate config you need.")
			echo $(eval_gettext "=== WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN WARN ===")
		fi
	fi
	sed -i -e "s/\s\+$ADDFQDN\s\+/ fqdn /g" -e "s/\s\+$ADDFQDN$/ fqdn/g" /etc/hosts
	sed -i -e "s/\s\+$KUSANAGI_FQDN\s\+/ $FQDN /g" -e "s/\s\+$KUSANAGI_FQDN$/ $FQDN/g" /etc/hosts
	sed -i -e "s/\s\+fqdn\s\+/ $ADD_NEWFQDN /g" -e "s/\s\+fqdn$/ $ADD_NEWFQDN/g" /etc/hosts

	KUSANAGI_FQDN=$FQDN
	PROFILE=$TARGET

	k_reload nginx httpd
	k_write_profile $PROFILE
}
