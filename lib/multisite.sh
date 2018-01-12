function k_multisite() {
	
	if [ "WordPress" = "${KUSANAGI_TYPE:-}" ] ; then
		echo $(eval_gettext "Enabling multisite.")
		echo $(eval_gettext "1) Sub directory type")
		echo $(eval_gettext "2) Sub domain type")
		echo -n $(eval_gettext "Which you choose create multisite mode?(Default:2): ")
		read msmode
		case "$msmode" in
		1)
			echo $(eval_gettext "You choose: Sub directory type")
			sed -i 's>#include templates.d/multisite.conf;>include templates.d/multisite.conf;>g' $NGINX_HTTP
			sed -i 's>#include templates.d/multisite.conf;>include templates.d/multisite.conf;>g' $NGINX_HTTPS
			;;
		*)
			echo $(eval_gettext "You choose: Sub domain type")
		esac
		[ 0 -eq $(k_is_enabled nginx) ] && k_nginx
		sed -i "s>#define('WP_ALLOW_MULTISITE', true);>define('WP_ALLOW_MULTISITE', true);>g" $WPCONFIG
	else
		echo $(eval_gettext "kusanagi multisite is for WordPress. Nothing to do.")
		return 1
	fi
}
