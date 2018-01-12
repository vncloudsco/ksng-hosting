# KUSANAGI Image Optimization
# 2017/04/18
#

if [ -v __KUSANAGI_IMAGE ]; then
	return
fi
__KUSANAGI_IMAGE=1

function k_images() {
	local TARGET=$PROFILE
	local PREOPT='__________NO/NE__________'
	local OPT_JPG=1 OPT_PNG=1 OPT_VERBOSE=0 OPT_ALL=1 OPT_DIR=
	local OPT_SIZE= OPT_QUALITY= OPT_COLOR= OPT_STRIP=0
	local OPT_SIZE_DEFAULT="1280x1024" OPT_QUALITY_DEFAULT=80 OPT_COLOR_DEFAULT=256
	local OPT_OWNER="kusanagi:kusanagi" OPT_MOD="0644"

	# オプション処理
	local OPT
	for OPT in "$@"
	do
		if [[ ! $OPT =~ ^-- ]] && [ -n "$PREOPT" ] ; then
			case "$PREOPT" in
				# skip 1st argment "image"
				'__________NO/NE__________')
					;;
				'--dir'|'--directory')
					#if [ ! -d "$OPT" ] ; then
					#       echo $(eval_gettext "Cannot use \$PREOPT \$OPT.")
					#       echo $(eval_gettext "directory $OPT is not found.")
					#       return 1
					#fi
					OPT_DIR=$OPT
					OPT_ALL=0
					;;
				'--quality') ## jpeg only
					if [[ ! $OPT =~ ^[0-9]+$ ]] || [ $OPT -lt 1 -o $OPT -gt 100 ] ; then
						echo $(eval_gettext "Cannot use \$PREOPT \$OPT.")
						echo $(eval_gettext "Option \$PREOPT needs 0-100.")
						return 1
					fi
					OPT_QUALITY=$OPT
					;;
				'--resize')
					if [[ ! $OPT =~ ^[0-9]+x[0-9]+$ ]] ; then
						echo $(eval_gettext "Cannot use \$PREOPT \$OPT.")
						echo $(eval_gettext "Option \$PREOPT needs WIDTHxHEIGHT(ex. 1280x1024).")
						return 1
					fi
					OPT_SIZE=$OPT
					;;
				'--color')
					if [[ ! $OPT =~ ^[0-9]+$ ]] || [ $OPT -lt 1 -o $OPT -gt 256 ] ; then
						echo $(eval_gettext "Cannot use \$PREOPT \$OPT.")
						echo $(eval_gettext "Option \$PREOPT needs 1-256.")
						return 1
					fi
					OPT_COLOR=$OPT
					;;
				'--owner')
					local OWN= GRP= DELIM=
					echo $OPT | grep : > /dev/null && DELIM=:
					echo $OPT | fgrep . > /dev/null && DELIM=.
					if [ -n "$DELIM" ] ; then
						OWN=$(echo $OPT | cut -d $DELIM -f 1)
						GRP=$(echo $OPT | cut -d $DELIM -f 2)
					else
						OWN=$OPT
					fi
					if [ $(getent passwd $OWN 2>&1 > /dev/null; echo $? ) -ne 0 ] ; then
						echo $(eval_gettext "Cannot use \$PREOPT \$OPT.")
						echo $(eval_gettext "User \$OWN is not found.")
						return 1
					fi
					if [ -n "$GRP" ] && [ $(getent group $GRP 2>&1 > /dev/null; echo $?) -ne 0 ] ; then
						echo $(eval_gettext "Cannot use \$PREOPT \$OPT.")
						echo $(eval_gettext "Group \$GRP is not found.")
						return 1
					fi
					OPT_OWNER=$OPT
					;;
				'--mode')
					if [[ ! $OPT =~ ^[0-7]+$ ]] ; then
						echo $(eval_gettext "Cannot use \$PREOPT \$OPT.")
						return 1
					fi
					OPT_MOD=$OPT
					;;

				*)
					;;
			esac
			PREOPT=
		else
			case "$OPT" in
				'--jpg'|'--jpeg')
					OPT_JPG=2
					[ $OPT_PNG -eq 1 ] && OPT_PNG=0
					;;
				'--png')
					OPT_PNG=2
					[ $OPT_JPG -eq 1 ] && OPT_JPG=0
					;;
				'--verbose')
					OPT_VERBOSE=1
					;;
				'--dir'|'--directory')
					PREOPT=$OPT
					;;
				'--quality')
					PREOPT=$OPT
					OPT_QUALITY=$OPT_QUALITY_DEFAULT
					OPT_ALL=0
					;;
				'--resize')
					PREOPT=$OPT
					OPT_SIZE=$OPT_SIZE_DEFAULT
					OPT_ALL=0
					;;
				'--color')
					PREOPT=$OPT
					OPT_COLOR=$OPT_COLOR_DEFAULT
					OPT_ALL=0
					;;
				'--owner')
					PREOPT=$OPT
					;;
				'--mode')
					PREOPT=$OPT
					;;
				'--strip')
					OPT_STRIP=1
					;;
				-*)
					# SKIP if specified unknown option
					echo $(eval_gettext "Cannot use option \$OPT")
					return 1
					;;
				'optimize')
					;;
				*)
					TARGET=$OPT
					break
			esac
		fi
	done

	# 初期値
	if [ "$OPT_ALL" -eq 1 ] ; then
		OPT_QUALITY=$OPT_QUALITY_DEFAULT
		OPT_SIZE=$OPT_SIZE_DEFAULT
		OPT_COLOR=$OPT_COLOR_DEFAULT
	fi

	k_read_profile $TARGET || return 1
	local DIRS=$OPT_DIR
	if [ -z "$DIRS" ] &&
		[ $KUSANAGI_TYPE = "WordPress" ]; then
		DIRS="wp-content/uploads"
	fi

	# work files
	local WORKJPG=$(mktemp)
	local WORKPNG=$(mktemp)
	local WORKPNG_LARGE=$(mktemp)
	touch $WORKJPG
	touch $WORKPNG
	touch $WORKPNG_LARGE

	local dir
	for dir in $(echo "$DIRS" |sed 's/:/ /')
	do
		local DIR=
		if [[ $dir =~ ^/ ]] ; then
			DIR=$dir
		else
			DIR=$TARGET_DIR/DocumentRoot/$dir
		fi
		if [ -d $DIR ] ; then
			[ "$OPT_VERBOSE" -ne 0 ] && echo $DIR
			if [ $OPT_JPG -ne 0 ] ; then
				find $DIR \( -iname '*.jpg' -o -iname '*.jpeg' \) -print0 >> $WORKJPG
			fi
			if [ $OPT_PNG -ne 0 ] ; then
				find $DIR -name '*.png' -print0 >> $WORKPNG
				find $DIR -name '*.PNG' -print0 >> $WORKPNG_LARGE
			fi
		else
			echo $(eval_gettext "Directory \$DIR is not found.")
		fi
	done
	#check
	if [ $(cat $WORKJPG $WORKPNG| wc -c) -eq 0 ] ; then
		echo $(eval_gettext "Target file is not found.")
		rm $WORKJPG $WORKPNG $WORKPNG_LARGE
		return 0
	fi
	#resize and quality
	local opt=
	if [ -n "$OPT_SIZE" ] ; then
		opt="$opt -resize $OPT_SIZE>"
	fi
	if [ -n "$OPT_QUALITY" ] ; then
		opt="$opt -quality $OPT_QUALITY"
	fi
	if [ -n "$OPT_STRIP" ] ; then
		opt="$opt -strip"
	fi
	if [ -n "$opt" ] ; then
		export MAGICK_THREAD_LIMIT=$(nproc)
		echo $(eval_gettext "Convert jpg/png size and quality:")
		if [ $OPT_VERBOSE -ne 0 ] ; then
			cat $WORKJPG $WORKPNG $WORKPNG_LARGE \
				| xargs -0 mogrify $opt -verbose 2>&1 \
				| grep -e JPEG -e PNG
		else
			cat $WORKJPG $WORKPNG \
				| xargs -0 mogrify $opt
		fi
	fi
	# png
	if [ "$OPT_PNG" -ne 0 ] ; then
		# color
		if [ -n "$OPT_COLOR" ] ; then
			echo $(eval_gettext "Convert png color:")
			if [ $OPT_VERBOSE -ne 0 ] ; then
				cat $WORKPNG | xargs -0 -P$(nproc)  pngquant \
					-v --skip-if-larger --ext=.png --force $OPT_COLOR 2>&1| grep ':' | sed 's/:$//'
				cat $WORKPNG_LARGE | xargs -0 -P$(nproc)  pngquant \
					-v --skip-if-larger --ext=.PNG --force $OPT_COLOR 2>&1| grep ':' | sed 's/:$//'
			else
				cat $WORKPNG | xargs -0 -P$(nproc) pngquant \
					--skip-if-larger --ext=.png --force $OPT_COLOR
				cat $WORKPNG_LARGE | xargs -0 -P$(nproc)  pngquant \
					--skip-if-larger --ext=.PNG --force $OPT_COLOR
			fi
		fi
		echo $(eval_gettext "Optimize png files:")
		if [ $OPT_VERBOSE -ne 0 ] ; then
			cat $WORKPNG $WORKPNG_LARGE | \
				xargs -0 -P$(nproc) optipng --preserve 2>&1 | grep '** Processing'
		else
			cat $WORKPNG $WORKPNG_LARGE |  \
				xargs -0 -P$(nproc) optipng --preserve --quiet
		fi
	fi

	# chown/chmod
	cat $WORKJPG $WORKPNG $WORKPNG_LARGE | \
		xargs -0 chown $OPT_OWNER
	cat $WORKJPG $WORKPNG $WORKPNG_LARGE | \
		xargs -0 chmod $OPT_MOD
	rm $WORKJPG $WORKPNG $WORKPNG_LARGE

	return 0
}
