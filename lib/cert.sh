
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
	fi
}
