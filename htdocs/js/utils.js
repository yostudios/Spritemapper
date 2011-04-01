
// mootools element accessor mixin
var ElementMixin = new Class({

  _element: null,

  setElement: function(element) {
    this.attachEvents(element);
    this._element = element;
  },

  toElement: function() {
    if (!this._element) this.setElement(this.buildElement());
    return this._element;
  },

  buildElement: function() {
    return new Element('div');
  },

  attachEvents: function(element) {}
});

function isElement(obj) {
  try {
    return obj instanceof HTMLElement;
  } catch(e) {
    // browsers not supporting W3 DOM2 don't have HTMLElement and
    // an exception is thrown and we end up here. Testing some
    // properties that all elements have. (works on IE7)
    return ((typeof obj === 'object')
            && (obj.nodeType == 1)
            && (typeof obj.style == 'object')
            && (typeof obj.ownerDocument == 'object'));
  }
};
