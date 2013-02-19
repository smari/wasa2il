
var _is = {
	'Add reference' : 'Bæta við tilvísun',
}

/* The gettext / _ function used to get translation or return default */
gettext = _ = function(_1) {
    try {
        return (typeof _is[_1] != 'undefined' ? _is[_1] : '*'+_1+'*');
    } catch(e) {
        return '*'+_1+'*';
    }
}