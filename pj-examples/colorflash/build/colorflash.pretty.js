(function() {
  var __extends = function(child, parent) {
    var ctor = function() {
    };
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.prototype.__init__ = child;
    if(typeof parent.extended === "function") {
      parent.extended(child)
    }
    child.__super__ = parent.prototype
  };
  var clamp, easeIn, linear, randint, Color, bind, random, easeInOut, Tween, Controller, TRANSITION_DURATION, CHANGE_EVERY, main, hex_encode_256, easeOut;
  hex_encode_256 = function hex_encode_256(n) {
    var result;
    if(n === 0) {
      result = "00"
    }else {
      if(0 <= n && n <= 15) {
        result = "0" + n.toString(16)
      }else {
        result = n.toString(16)
      }
    }
    return result
  };
  clamp = function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max)
  };
  bind = function bind(f, obj) {
    return function() {
      return f.apply(obj, arguments)
    }
  };
  linear = function linear(t) {
    return t
  };
  easeIn = function easeIn(t) {
    return 1 - Math.pow(1 - t, 3)
  };
  easeOut = function easeOut(t) {
    return t * t * t
  };
  easeInOut = function easeInOut(t) {
    return 3 * t * t - 2 * t * t * t
  };
  Tween = function __init__(info) {
    this._startedAt = (new Date).getTime();
    this._duration = info._duration;
    this._callback = info._callback;
    this._easing = info._easing || linear;
    this._tick();
    return this
  };
  Tween.prototype._tick = function _tick() {
    var t;
    t = clamp(((new Date).getTime() - this._startedAt) / this._duration, 0, 1);
    this._callback(t);
    if(t < 1) {
      setTimeout(bind(this._tick, this), 1)
    }
  };
  random = function random() {
    var x;
    x = Math.random();
    return x === 1 ? 0 : x
  };
  randint = function randint(a, b) {
    return Math.floor(random() * (b - a + 1)) + a
  };
  Color = function __init__(r, g, b) {
    this.r = clamp(Math.round(r), 0, 255);
    this.g = clamp(Math.round(g), 0, 255);
    this.b = clamp(Math.round(b), 0, 255);
    return this
  };
  Color.prototype._interpolatedToward = function _interpolatedToward(c2, fraction) {
    return new Color(this.r + (c2.r - this.r) * fraction, this.g + (c2.g - this.g) * fraction, this.b + (c2.b - this.b) * fraction)
  };
  Color.prototype._webString = function _webString() {
    return"#" + hex_encode_256(this.r) + hex_encode_256(this.g) + hex_encode_256(this.b)
  };
  CHANGE_EVERY = 1E3;
  TRANSITION_DURATION = 250;
  Controller = function __init__() {
    this._newColor = this._oldColor = new Color(255, 255, 255);
    this._changeColor();
    return this
  };
  Controller.prototype._changeColor = function _changeColor() {
    var onComplete, callback;
    this._oldColor = this._newColor;
    this._newColor = new Color(randint(0, 255), randint(0, 255), randint(0, 255));
    callback = function callback(t) {
      document.body.style.background = this._oldColor._interpolatedToward(this._newColor, t)._webString()
    };
    onComplete = function onComplete(t) {
      document.title = this._newColor._webString()
    };
    new Tween({_duration:TRANSITION_DURATION, _callback:bind(callback, this), _easing:easeInOut, _onComplete:bind(onComplete, this)});
    setTimeout(bind(arguments.callee, this), CHANGE_EVERY)
  };
  main = function main() {
    new Controller
  };
  window.colorflash = {main:main}
})();
