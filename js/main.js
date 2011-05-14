/*

      _
    .--' |
   /___^ |     .--.
       ) |    /    \
      /  |  /`      '.
     |   '-'    /     \
     \         |      |\
      \    /   \      /\|
       \  /'----`\   /
       |||       \\ |
       ((|        ((|
       |||        |||
      //_(       //_(

*/

function main() {

  function setSource(el, source) {
    el.set('text', source);
    hljs.highlightBlock(el, '  ', false);
    var expander = new Element('span', {'class': 'expander', 'text': 'expand'});
    expander.addEvent('click', function(e) {
      e.preventDefault();
      el.addClass('expanded');
    });
    el.adopt(expander);
  }

  new Request({
    url: 'css/awesome-font.css',
    onSuccess: function(response) {
      setSource(document.id('source').getElement('pre'), response);
      // quick n dirty find all the images,
      var list = document.id('source').getElement('ul');
      response.match(/url\(.*\)/ig).each(function(match) {
        var relative = match.substring(match.indexOf('(') + 1, match.lastIndexOf(')'));
        var src = 'css/' + relative;
        list.adopt(new Element('li', {
          'html': '<img src="' + src + '">'
        }));
      });
    }
  }).get();

  new Request({
    url: 'css/awesome.css',
    onSuccess: function(response) {
      setSource(document.id('output').getElement('pre'), response);
    }
  }).get();

  // awesome-font-o-matic
  var fontInput = document.id('font-text'),
      fontContainer = document.getElement('.awesome'),
      fontLen = fontInput.get('value').length;

  function updateAwesome() {
    var text = fontInput.get('value').toLowerCase();
    fontContainer.empty();

    for (var i = 0; i < text.length; i++) {
      var letter = text[i];
      if (!letter.test(/[a-z ]/))
        continue;
      fontContainer.adopt(new Element('span', {
        'class': 'letter ' + (letter == ' ' ? 'space' : letter),
        'text': letter
      }));
    }
    if (text.length > fontLen) {
      fontContainer.getElements('span').getLast().addClass('anim');
    }
    fontLen = text.length;
  }

  fontInput.addEvents({
    change: updateAwesome,
    keyup: updateAwesome
  });

};

window.addEvent('domready', main);
