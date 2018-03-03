var _pj;
function _pj_snippets(container) {
    function set_decorators(cls, props) {
        var deco, decos;
        var _pj_a = props;
        for (var p in _pj_a) {
            if (_pj_a.hasOwnProperty(p)) {
                decos = props[p];
                function reducer(val, deco) {
                    return deco(val, cls, p);
                }
                deco = decos.reduce(reducer, cls.prototype[p]);
                if (((! ((deco instanceof Function) || (deco instanceof Map) || (deco instanceof WeakMap))) && (deco instanceof Object) && (("value" in deco) || ("get" in deco)))) {
                    delete cls.prototype[p];
                    Object.defineProperty(cls.prototype, p, deco);
                } else {
                    cls.prototype[p] = deco;
                }
            }
        }
    }
    container["set_decorators"] = set_decorators;
    return container;
}
_pj = {};
_pj_snippets(_pj);
class Foo3 {
    foo() {
        return "bar";
    }
}
_pj.set_decorators(Foo3, {"foo": [a_deco]});
