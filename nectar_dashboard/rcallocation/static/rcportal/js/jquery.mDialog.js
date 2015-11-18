/**
 * mDialog - Dialog Popup window
 * @author Simon Yu
 */

var mDialog = {

    /**
     * The window owner. the display window will be based on this owner
     */
    owner:undefined,

    /**
     * The mouse hovered position
     */
    hovered:false,

    /**
     * Settings
     */
    settings:{
        /**
         * The most outside window id
         */
        id:"mDialog",
        /**
         * Window title
         */
        title:"Title",
        /**
         * The dialog content
         */
        content:"",

        /**
         * The most outside window css class
         */
        className:"",

        /**
         * The default window width size
         */
        width:250,

        /**
         * flag  whether it should close if mouse click outside the popup windows
         */
        close_on_body_click:true,

        /**
         * flag whether it should hide the title or not
         */
        title_visiable:true,

        /**
         * The top offset of the window in px
         */
        top_offset:5,

        /**
         * The left offset of the window in px
         */
        left_offset:5,

        /**
         * Check if popup window already showed or not
         */
        pwDone:false,

        /*
         * version
         */
        version:"1.0"
    },

    /**
     * Display the Dialog
     */
    show:function (options) {
        var position = mDialog.getPosition();
        // reset the default to avoid the conflicts between multiple windows
        mDialog.settings.close_on_body_click = true;
        mDialog.settings.title_visiable = true;
        mDialog.settings.top_offset = 5;
        mDialog.settings.left_offset = 5;
        mDialog.settings.width = 250;
        mDialog.settings.content = "";
        mDialog.settings.title = "Title";
        mDialog.settings.id = "mDialog";
        mDialog.settings.className = "";
        mDialog.settings.pwDone = false;
        $.extend(mDialog.settings, options);

        //close the dialog window
        mDialog.close();

        //create dialog window object
        var dialog = $("#" + mDialog.settings.id);
        if (dialog.size() == 0) {
            var topPosition = position.top + position.height + mDialog.settings.top_offset;
            var leftPosition = position.left + mDialog.settings.left_offset;
            var browserHalfSize = mDialog.getBrowserHalfSize();
            var browserSize = mDialog.getBrowserSize();

            //get the left start position
            if ((leftPosition + mDialog.settings.width) > browserSize.width) {
                leftPosition = browserSize.width - (mDialog.settings.width + mDialog.settings.left_offset) - 100;
            } else {
                if (leftPosition > browserHalfSize.width) {
                    leftPosition = position.left;
                }
            }

            var positionCss = 'top:' + topPosition + 'px;left:' + leftPosition + 'px;';
            //popup window
            var html = '';
            html += '<div id="' + mDialog.settings.id + '" class="mdialog_outter_panel ' + mDialog.settings.className + '" style="position:absolute;display:none;' + positionCss + '">';
            html += '    <div class="mdialog_popup_panel" style="width:' + mDialog.settings.width + 'px">';
            html += '        <div class="mdialog_inner_panel">';
            if (mDialog.settings.title_visiable) {
                html += '	     <div class="mdialog_header">';
                html += '              <div class="mdialog_title">' + mDialog.settings.title + '</div>';
                html += '              <div class="mdialog_close" onclick="mDialog.close();" title="Close"></div>';
                html += '		 </div>';
            }
            html += '            <div class="mdialog_content">';
            html += '                <div class="mdialog_content_display">';
            html += '                    ' + mDialog.settings.content;
            html += '                </div>';
            html += '            </div>';
            html += '	         <div class="mdialog_footer">';
            html += '               <div class="mdialog_footer_txt">&nbsp;</div>';
            html += '		     </div>';
            html += '        </div>';
            html += '    </div>';
            html += '    <div style="clear:both"></div>';
            html += '</div>';

            $("body").append($(html));

            dialog = $("#" + mDialog.settings.id);
            dialog.hover(function () {
                mDialog.hovered = true;
            });
        }

        //show the pop-up windows
        dialog.show();

        //set the popup window already showed
        mDialog.pwDone = true;

        // auto close when body click
        $(document).mousedown(function () {
            if (!mDialog.hovered && mDialog.settings.close_on_body_click) {
                mDialog.close();
            }
        });

        jQuery(mDialog.owner).addClass("active");

        dialog.mouseover(function () {
            mDialog.hovered = true;
        });

        dialog.mouseout(function () {
            mDialog.hovered = false;
        });

        jQuery(mDialog.owner).mouseover(function () {
            mDialog.hovered = true;
        });

        jQuery(mDialog.owner).mouseout(function () {
            mDialog.hovered = false;
        });
    },

    /**
     * Update the contents
     */
    update:function (content) {
        $("#" + mDialog.settings.id + " .mdialog_content_display").html(content);
    },

    /**
     * Close the dialog
     */
    close:function () {
        var dialog = $("#" + mDialog.settings.id);
        $(mDialog.owner).removeClass("active");
        dialog.fadeOut('slow');
        dialog.remove();
    },

    /**
     * Get be half size of the browser
     *
     * */
    getBrowserHalfSize:function () {
        var browserWidth = window.innerWidth || document.documentElement.clientWidth ||
            document.body.clientWidth;
        var browserHeight = window.innerHeight || document.documentElement.clientHeight ||
            document.body.clientHeight;
        var scrollX = document.documentElement.scrollLeft || document.body.scrollLeft;
        var scrollY = document.documentElement.scrollTop || document.body.scrollTop;
        return {width:( browserWidth / 2) + scrollX, height:( browserHeight / 2) + scrollY};
    },
    /**
     * Get the current Window Size
     */
    getBrowserSize:function () {
        var browserWidth = window.innerWidth || document.documentElement.clientWidth ||
            document.body.clientWidth;
        var browserHeight = window.innerHeight || document.documentElement.clientHeight ||
            document.body.clientHeight;
        var scrollX = document.documentElement.scrollLeft || document.body.scrollLeft;
        var scrollY = document.documentElement.scrollTop || document.body.scrollTop;
        return {width:browserWidth + scrollX, height:browserHeight + scrollY};
    },

    /**
     * Get the owner position - top, left, width and height
     */
    getPosition:function () {
        if (mDialog.owner == undefined) {
            return {top:0, left:0, width:0, height:0};
        }

        var e = mDialog.owner;
        var oTop = e.offsetTop;
        var oLeft = e.offsetLeft;
        var oWidth = e.offsetWidth;
        var oHeight = e.offsetHeight;

        while (e = e.offsetParent) {
            oTop += e.offsetTop;
            oLeft += e.offsetLeft;
        }

        return {
            top:oTop,
            left:oLeft,
            width:oWidth,
            height:oHeight
        }
    }
};

$(document).ready(function () {
    $(document).bind('keypress', function (e) {
        if (mDialog.pwDone) {
            if (e.which == 13) {
                //do nothing,
            }
            //click the Esc key, it will close the pop-up window.
            if (e.keyCode == 27) {

                mDialog.close();
            }
        }
    });
});


jQuery.fn.mDialog = function (settings) {
    if (mDialog.ownder == this[0]) {
        return false;
    }
    mDialog.close();
    mDialog.owner = this[0];
    mDialog.show(settings);
};

jQuery.fn.mDialog.close = function () {
    mDialog.close();
};


jQuery.fn.mDialog.update = function (content) {
    mDialog.update(content);
}