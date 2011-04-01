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
  }

  new Request({
    url: 'css/example_source.css',
    onSuccess: function(response) {
      setSource(document.id('source').getElement('pre'), response);
    }
  }).get();

  new Request({
    url: 'css/example.css',
    onSuccess: function(response) {
      setSource(document.id('output').getElement('pre'), response);
    }
  }).get();

  var testCode = document.id('test-code').get('html');

  // clean up & remove indentation
  var indentLevel = testCode.indexOf('<') - 1;
  testCode = testCode.split('\n').filter(function(line){
    return line.length;
  }).map(function(line) {
    return line.substr(indentLevel);
  }).join('\n');

  setSource(document.id('test').getElement('pre'), testCode);
};

window.addEvent('domready', main);
