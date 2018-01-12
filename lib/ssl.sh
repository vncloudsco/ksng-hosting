# KUSANAGI SSL setting
# 2016/03/14
#

if [[ -v __KUSANAGI_SSL ]] ; then
	__KUSANAGI_SSL=1
	return
fi
source $LIBDIR/autorenewal.sh

function k_cert_change() {
	local CERT="$1"
	local KEY="$2"
	local TARGETDIR=/etc/kusanagi.d/ssl/$PROFILE
	if [ -n "$CERT" -a -n "$KEY" ] ; then
		if [ \! -d $TARGETDIR ] ; then
			mkdir -p $TARGETDIR
		fi
		local TARGET_CERT=$TARGETDIR/"${CERT##*/}"
		if [ -f "$TARGET_CERT" ] ; then
			local DATESTR=$(stat -c '%y' "$TARGET_CERT" | awk -F. '{print $1}'|sed 's/ /_/')
			mv "$TARGET_CERT" "${TARGET_CERT}.${DATESTR}"
		fi
		cp "$CERT" "$TARGET_CERT"
		local TARGET_KEY="$TARGETDIR/${KEY##*/}"
		if [ -f "$TARGET_KEY" ] ; then
			local DATESTR=$(stat -c '%y' "$TARGET_KEY" | awk -F. '{print $1}'|sed 's/ /_/')
			mv "$TARGET_KEY" "${TARGET_KEY}.${DATESTR}"
		fi
		cp "$KEY" "$TARGET_KEY"

		sed -i "s|^\(\s*ssl_certificate\s\+\)\S\+;|\\1${TARGET_CERT};|" $NGINX_HTTPS
		sed -i "s|^\(\s*ssl_certificate_key\s\+\)\S\+;|\\1${TARGET_KEY};|" $NGINX_HTTPS
		sed -i "s|^\(\s*SSLCertificateFile\s\+\)\S\+|\\1${TARGET_CERT}|" $HTTPD_HTTPS
		sed -i "s|^\(\s*SSLCertificateKeyFile\s\+\)\S\+|\\1${TARGET_KEY}|" $HTTPD_HTTPS

		echo $(eval_gettext "Change SSL Certificate configuration.")

		# modify WP configure
		local fqdn=$(k_get_fqdn $PROFILE)
		wp_replace_proto "http" "https" $fqdn
	fi
}
function k_hsts() {
	local opt=$1
	local arg=$2
	local RET1= RET2=
	local STS="add_header Strict-Transport-Security"
	if [ "$arg" = "off" ] ; then
		echo $(eval_gettext "Disabling HSTS")
		echo $(eval_gettext "If you switch from weak or mid,It takes a lot of times for enable.")
		echo $(eval_gettext "And, Can not switch from high to off.")
		sed -i 's/set $hsts [0-3];/set $hsts 0;/g' $NGINX_HTTPS ; RET1=$?
		sed -i "1,/$STS\s*/s/^\(\s\+\)#\?\s*$STS\s\+/\1#$STS /" $NGINX_HTTPS; RET1=$?
		sed -i 's/Define hsts [0-3]/Define hsts 0/g' $HTTPD_HTTPS ; RET2=$?
	elif [ "$arg" = "weak" ] ; then
		echo $(eval_gettext "Enabling HSTS(not IncludeSubDomain)")
		echo $(eval_gettext "If you switch from mid,It takes a lot of times for enable.")
		echo $(eval_gettext "And, Can not switch from high to weak.")
		sed -i 's/set $hsts [0-3];/set $hsts 0;/g' $NGINX_HTTPS ; RET1=$?
		sed -i "1,/$STS\s*/s/^\(\s\+\)#\?\s*$STS\s\+.*;$/\1$STS \"max-age=31536000\";/" $NGINX_HTTPS; RET1=$?
		sed -i 's/Define hsts [0-3]/Define hsts 1/g' $HTTPD_HTTPS ; RET2=$?
	elif [ "$arg" = "mid" ] ; then
		echo $(eval_gettext "Enabling HSTS w/IncludeSubDomain (not Preloading)")
		echo $(eval_gettext "If you switch from weak,It takes a lot of times for enable.")
		echo $(eval_gettext "And, Can not switch from high to mid." )
		sed -i 's/set $hsts [0-3];/set $hsts 0;/g' $NGINX_HTTPS ; RET1=$?
		sed -i "1,/$STS\s*/s/^\(\s\+\)#\?\s*$STS\s\+.*;$/\1$STS \"max-age=31536000; includeSubDomains\";/" $NGINX_HTTPS; RET1=$?
		sed -i 's/Define hsts [0-3]/Define hsts 2/g' $HTTPD_HTTPS ; RET2=$?
	elif [ "$arg" = "high" ] ; then
		echo $(eval_gettext "Enabling HSTS w/IncludeSubDomain,Preloading")
		sed -i 's/set $hsts [0-3];/set $hsts 0;/g' $NGINX_HTTPS ; RET1=$?
		sed -i "1,/$STS\s*/s/^\(\s\+\)#\?\s*$STS\s\+.*;$/\1$STS \"max-age=31536000; includeSubDomains; preload\";/" $NGINX_HTTPS; RET1=$?
		sed -i 's/Define hsts [0-3]/Define hsts 3/g' $HTTPD_HTTPS ; RET2=$?
		echo $(eval_gettext "Setting changed,Try to register HSTS Preloading List")
		local fqdn=$(k_get_fqdn $PROFILE)
		wget -q -O /dev/null https://hstspreload.appspot.com/submit/${fqdn}
	else
		echo $(eval_gettext "Cannot use \$arg.")
		echo $(eval_gettext "kusanagi \$opt [off|weak|mid|high].")
		return 1
	fi
}

function k_https() {
	#All HTTPS or not
	local fqdn=$(k_get_fqdn $PROFILE)
	local opt=$1
	local arg=$2
	local OLDPROTO PROTO
	if [ "$arg" = "redirect" ] ; then
		echo $(eval_gettext "Set redirect all traffic on FQDN to HTTPS.(Permanently)") | sed "s|FQDN|$fqdn|"
		sed -i "s/\(\s\+\)#\s*rewrite ^(.*)$ https:/\1rewrite ^(.*)$ https:/g" $NGINX_HTTP
		sed -i "s/RewriteEngine Off/RewriteEngine On/g" $HTTPD_HTTP
		if [ -f "$WPCONFIG" ] ; then
			sed -i "s/^[#\s]\+define('FORCE_SSL_ADMIN/define('FORCE_SSL_ADMIN/g" $WPCONFIG
		fi
		OLDPROTO="http"
		PROTO="https"
	elif [ "$arg" = "noredirect" ] ; then
		echo $(eval_gettext "Release redirect all traffic on FQDN to HTTPS.") | sed "s|FQDN|$fqdn|"
		sed -i "s/\(\s\+\)rewrite ^(.*)$ https:/\1#rewrite ^(.*)$ https:/g" $NGINX_HTTP
		sed -i "s/RewriteEngine On/RewriteEngine Off/g" $HTTPD_HTTP
		if [ -f "$WPCONFIG" ] ; then
			sed -i "s/^define('FORCE_SSL_ADMIN/#define('FORCE_SSL_ADMIN/g" $WPCONFIG
		fi
		OLDPROTO="https"
		PROTO="http"
	else
		echo $(eval_gettext "Cannot use \$arg.")
		echo $(eval_gettext "kusanagi \$opt [redirect|noredirect].")
		return 1
	fi

	# modify WP configure
	wp_replace_proto $OLDPROTO $PROTO $fqdn
}

function wp_replace_proto {
	local OLDPROTO="$1://"
	local PROTO="$2://"
	local FQDN=$3
	if [ -e "$WPCONFIG" ] ; then
		local WP="sudo -u kusanagi -i -- /usr/local/bin/wp"
		local DOC_ROOT="$KUSANAGI_DIR/DocumentRoot"
		# override wp option home/siteurl when use 'http://'
		$WP option get home --path=$DOC_ROOT | grep "${OLDPROTO}" >/dev/null 2>&1
		if [ $? -eq 0 ] ; then
			$WP search-replace $OLDPROTO$FQDN $PROTO$FQDN --path=$DOC_ROOT --all-tables > /dev/null
		fi
	fi
}

# enable_ssl TARGET john@example.com example.com [renew]
function enable_ssl() {
	local TARGET=$1
	local MAILADDR=$2
	local FQDN=$3
	local OPT=$4
	
	local OPTION=

    if [ -z $MAILADDR ] ; then
		echo $(eval_gettext "Please use --email option for specified Mail address.")
		return 1
	fi

	if [ "renew" = "$OPT" ] ; then
		OPTION="--renew-by-default"
	else
		OPTION="-m $MAILADDR --agree-tos"
	fi

	if [ "" != "$MAILADDR" ] && [ -e $CERTBOT ]; then
		# create lets encrypt.
		is_root_domain $FQDN
		local RET=$?
		if [ "$RET" -eq 0 ] ; then
			$CERTBOT certonly --text --noninteractive --webroot -w $KUSANAGI_DIR/DocumentRoot -d $FQDN -d www.$FQDN $OPTION
		elif [ "$RET" -eq 1 ] ; then
			local APEX=`echo $FQDN | cut -c 5-`
			$CERTBOT certonly --text --noninteractive --webroot -w $KUSANAGI_DIR/DocumentRoot -d $FQDN -d $APEX $OPTION
		else
			$CERTBOT certonly --text --noninteractive --webroot -w $KUSANAGI_DIR/DocumentRoot -d $FQDN $OPTION
		fi
	
		local FULLCHAINPATH=$(ls -1t /etc/letsencrypt/live/$FQDN*/fullchain.pem 2> /dev/null |head -1)
		local LETSENCRYPTDIR=${FULLCHAINPATH%/*}  # dirname
		if [ -n "$FULLCHAINPATH" ] ; then
			env RENEWD_LINAGE=${LETSENCRYPTDIR} /usr/bin/ct-submit.sh
		else
			# certbot-auto was failed.
			echo $(eval_gettext "Cannot get Let\'s Encrypt SSL Certificate files.") #'
			return 1
		fi

		# exit if renew option
		if [ "$OPT" = 'renew' ] ; then
			return 0
		fi

		# set nginx/httpd configure
		sed -i -e "s|^\(\s*ssl_certificate\s\+\)\S\+;|\\1${LETSENCRYPTDIR}/fullchain.pem;|" \
		       -e "s|^\(\s*ssl_certificate_key\s\+\)\S\+;|\\1${LETSENCRYPTDIR}/privkey.pem;|" $NGINX_HTTPS
		sed -i -e "s|^\(\s*SSLCertificateFile\s\+\)\S\+|\\1${LETSENCRYPTDIR}/fullchain.pem|" \
		       -e "s|^\(\s*SSLCertificateKeyFile\s\+\)\S\+|\\1${LETSENCRYPTDIR}/privkey.pem|" $HTTPD_HTTPS

		# modify WP configure
		wp_replace_proto "http" "https" $FQDN
	fi
}

function k_ssl_ct() {
	local OPT=$1
	local SSLCT_NO=$2
	local SSLCERT=$(awk '/\s+ssl_certificate\s/ {gsub(";", "") ; print $2}' $NGINX_HTTPS)

	if [ ! -f "$SSLCERT" ] ; then
		echo $(eval-gettext "SSL Certificate file(\$SSLCERT) is not found.")
		return 1
	fi
	if [ "$OPT" = "on" ] ; then
		if [ $SSLCT_NO -eq 0 ] ; then
			/usr/bin/ct-submit.sh ${SSLCERT} || return 1
		fi
		find "${SSLCERT%/*}/scts" -type f 2>&1 > /dev/null
		if [ $? -eq 0 ] ; then
			sed -i -e 's|^\(\s*\)\#\s*\(ssl_ct\s\+on;\)|\1\2|' \
				-e "s|^\(\s*\)\#\s*\(ssl_ct_static_scts\s\+\)\S\+;|\1\2${SSLCERT%/*}/scts;|" $NGINX_HTTPS
			echo $(eval_gettext "Enabling CT.")
		else
			echo $(eval_gettext "Cannot enabling CT.")
			return 1
		fi
    elif [ "$OPT" = "off" ] ; then
		sed -i -e 's|^\(\s*\)\(ssl_ct\s\+on;\)|\1#\2|' \
			-e "s|^\(\s*\)\(ssl_ct_static_scts\s\+\S\+\s*;\)|\1#\2|" $NGINX_HTTPS
		echo $(eval_gettext "Disabling CT.")
	fi
	return 0
}

function k_ssl() {
	local MAILADDR=
	local OPT
	local PREOPT='none'
	local TARGET=$PROFILE
	local SSLCT_NO=0
	## parse argument
	for OPT in "$@"
	do
		# skip 1st argment "setting"
		if [ -n "$PREOPT" ] ; then
			case "$PREOPT" in
				'none')
					;;
				'--email')
					# for Let's encript
					if [[ ! ${OPT,,} =~ ^[a-z0-9!$\&*.=^\`|~#%\'+\/?_{}-]+@([a-z0-9_-]+\.)+(xx--[a-z0-9]+|[a-z]{2,})$ ]] ; then #'
						echo $(eval_gettext "Cannot use --email \$OPT.")
						echo $(eval_gettext "Please specified valid mail address.")
						return 1
					fi
					local EMAIL=$OPT
				;;
				'--https')
					# for https redirect or noredirect
					if [[ ! $OPT =~ ^(redirect|noredirect)$ ]] ; then 
						echo $(eval_gettext "Cannot use --https \$OPT.")
						echo $(eval_gettext "kusanagi ssl --https [redirect|noredirect].")
						return 1
					fi
					local HTTPS=$OPT
				;;
				'--hsts')
					# for hsts setting
					if [[ ! $OPT =~ ^(off|weak|mid|high)$ ]] ; then 
						echo $(eval_gettext "Cannot use --hsts \$OPT.")
						echo $(eval_gettext "kusanagi ssl --hsts [off|weak|mid|high].")
						return 1
					fi
					local HSTS=$OPT
				;;
				'--auto')
					# for Let's Encrypt automatic reset cert
					if [[ ! $OPT =~ ^(on|off)$ ]] ; then 
						echo $(eval_gettext "Cannot use --auto \$OPT.")
						echo $(eval_gettext "kusanagi ssl --auto [on|off].")
						return 1
					fi
					local AUTO=$OPT
				;;
				'--cert')
					# set cert file
					if [ ! -e $OPT ] ; then
						echo $(eval_gettext "file \$OPT is not found.")
						return 1
					fi
					local CERT=$OPT
				;;
				'--key')
					# set key file
					if [ ! -e $OPT ] ; then
						echo $(eval_gettext "file \$OPT is not found.")
						return 1
					fi
					local KEY=$OPT
				;;
				'--ct')
					# for CT(Certificate Transparency)
					if [[ ! $OPT =~ ^(on|off)$ ]] ; then 
						echo $(eval_gettext "Cannot use --ct \$OPT.")
						echo $(eval_gettext "kusanagi ssl --ct [on|off].")
						return 1
					fi
					local SSLCT=$OPT
				;;
			esac
			PREOPT=
		else
			case "$OPT" in
				'--email'|'--https'|'--hsts'|'--auto'|'--cert'|'--key'|'--ct')
					PREOPT=$OPT
					;;
				'--no-register'|'--noregister')
					# do not register to ct log server
					SSLCT_NO=1
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
	# check empty option
	if [ $PREOPT ] ; then
		echo $(eval_gettext "Option \$PREOPT needs more argument.")
		return 1
	fi

	if [ -n "$EMAIL" ] && [ -n "$CERT" -o -n "$KEY" ] ; then
		echo $(eval_gettext "Cannot specify option --email and option --cert/--key at the same time.")
		return 1
	fi
	if [ -n "$CERT" -a -n "$KEY" ] || [ -z "$CERT" -a -z "$KEY" ] ; then
		:
	else
		echo $(eval_gettext "Please specify option --cert and --key at the same time.")
		return 1
	fi

	local NEEDRESTART=0
	k_read_profile $TARGET || return 1
	if [ -n "$EMAIL" ] ; then
		enable_ssl "$TARGET" "$EMAIL" "$KUSANAGI_FQDN" '' || return 1
		AUTO=on
		NEEDRESTART=1
	fi
	if [ -n "$CERT" -a -n "$KEY" ] ; then
		k_cert_change "$CERT" "$KEY" || return 1
		NEEDRESTART=1
	fi
	if [ -n "$HSTS" ] ; then
		k_hsts "ssl --hsts" $HSTS || return 1
		NEEDRESTART=1
	fi
	if [ -n "$HTTPS" ] ;then
		k_https 'ssl --https' $HTTPS || return 1
		NEEDRESTART=1
	fi
	if [ -n "$AUTO" ] ;then
		k_autorenewal 'ssl --auto' $AUTO || return 1
	fi
	if [ -n "$SSLCT" ] ; then
		k_ssl_ct $SSLCT $SSLCT_NO || return 1
		NEEDRESTART=1
	fi
	if [ "$NEEDRESTART" -eq 1 ] ; then
		echo $(eval_gettext "Modified nginx/httpd config files and restart.")
		k_reload nginx httpd monit
		sleep 1
		k_monit_reloadmonitor
	fi
}


