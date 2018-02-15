var _pj;
function _pj_snippets(container) {
    function _in(left, right) {
        if (((right instanceof Array) || ((typeof right) === "string"))) {
            return (right.indexOf(left) > (- 1));
        } else {
            return (left in right);
        }
    }
    container["_in"] = _in;
    return container;
}
_pj = {};
_pj_snippets(_pj);
_pj._in(foo, bar);
