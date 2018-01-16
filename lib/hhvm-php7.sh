#!

function pro_php7() {
     echo $(eval_gettext "use TARGET") | sed "s|TARGET|$1|"
	 if [ 0 -eq $(k_is_enabled hhvm.$1) ] ; then
	     systemctl stop hhvm.$1 && systemctl disable hhvm.$1
	 fi
	 if [ -f "/usr/lib/systemd/system/php7-fpm.$1.service" ]; then
	     systemctl start php7-fpm.$1 && systemctl enable php7-fpm.$1
	 else 
	     /usr/src/create-php7-conf -d $1 -u $2
	 fi
	 ## edit nginx configuration
	 ## disable using hhvm unix socket
	 CMD="sed -i 's/^.*\(fastcgi_pass unix:\/var\/cache\/hhvmd\/$1.sock;*$\)/\t\t#\1/' /etc/nginx/conf.d/$1_http.conf"
	 echo $CMD | bash
	 CMD="sed -i 's/^.*\(fastcgi_pass unix:\/var\/cache\/hhvmd\/$1.sock;*$\)/\t\t#\1/' /etc/nginx/conf.d/$1_ssl.conf"
	 echo $CMD | bash
     ## enable using php7-fpm unix socket
	 CMD="sed -i 's/^.*\(fastcgi_pass unix:\/var\/cache\/php7-fpm\/$1.sock;*$\)/\t\t\1/' /etc/nginx/conf.d/$1_http.conf"
	 echo $CMD | bash
	 CMD="sed -i 's/^.*\(fastcgi_pass unix:\/var\/cache\/php7-fpm\/$1.sock;*$\)/\t\t\1/' /etc/nginx/conf.d/$1_ssl.conf"
	 echo $CMD | bash

	 ## reload nginx configuration
	 systemctl reload nginx

 }

function pro_hhvm() {
     echo $(eval_gettext "use TARGET") | sed "s|TARGET|$1|"
	 if [ 0 -eq $(k_is_enabled php7-fpm.$1) ] ; then    
		 systemctl stop php7-fpm.$1 && systemctl disable php7-fpm.$1
	 fi
	 if [ -f "/etc/hhvm/conf.d/$1.ini" ]; then
	     systemctl start hhvm.$1 && systemctl enable hhvm.$1
	 else 
	     /usr/src/create-hhvm-ini -d $1 -u $2
	 fi
	 ## edit nginx configuration
	 ## disable using php7-fpm unix socket
	 CMD="sed -i 's/^.*\(fastcgi_pass unix:\/var\/cache\/php7-fpm\/$1.sock;*$\)/\t\t#\1/' /etc/nginx/conf.d/$1_http.conf"
	 echo $CMD | bash
	 CMD="sed -i 's/^.*\(fastcgi_pass unix:\/var\/cache\/php7-fpm\/$1.sock;*$\)/\t\t#\1/' /etc/nginx/conf.d/$1_ssl.conf"
	 echo $CMD | bash
     ## enable using hhvm unix socket
	 CMD="sed -i 's/^.*\(fastcgi_pass unix:\/var\/cache\/hhvmd\/$1.sock;*$\)/\t\t\1/' /etc/nginx/conf.d/$1_http.conf"
	 echo $CMD | bash
	 CMD="sed -i 's/^.*\(fastcgi_pass unix:\/var\/cache\/hhvmd\/$1.sock;*$\)/\t\t\1/' /etc/nginx/conf.d/$1_ssl.conf"
	 echo $CMD | bash
     
	 ## reload nginx configuration
	 systemctl reload nginx
}
