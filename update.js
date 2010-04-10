port = null;

function getPort() {
  if (!port) {
    port = chrome.extension.connect({name: "css-editor"});
    port.onMessage.addListener(function(msg, port) {
        console.log( 'css-editor got a message' );
        updateCSS(msg);
    });
   }
  return port;
}

function updateCSS(msg) {
  if(msg) {
    console.log(msg)
    for (var i=0; i<document.styleSheets.length; i++) {
        document.styleSheets[i].href = "file://" + msg[i].tmp
    }
  }
}

function findCSS() {
    if (document.styleSheets) {
        var post_data = extractCSS()
        getPort().postMessage( post_data );
    }
}

function extractCSS(){
    var stylesheets = {id:[], rules:[], href:[], media:[], origin:document.location.href}
    var styles = []
    for (var i=0; i<document.styleSheets.length; i++) {
        var style = document.styleSheets[i];
        var rules = [];
        if (style.rules != null){
            for (var j=0; j<style.rules.length; j++){
                rules.push(style.rules[j].cssText);
            }
        }
        stylesheets.id.push(i)
        stylesheets.href.push(style.href)
        stylesheets.rules.push(rules.join("\n"))
        stylesheets.media.push(style.media.mediaText)
    }
    query =  {id:stylesheets.id.join(","), rules:stylesheets.rules.join("||"), href:stylesheets.href.join(","), media:stylesheets.media.join(","), origin:document.location.href }
    return query
}
function testPost(){
   port = chrome.extension.connect({name: "css-editor"});
   port.onMessage.addListener(function(msg, port) {
        console.log( 'css-editor got a message' );
   });
   data = {id:"1,2,3",
        rules:" || || || ",
        href:" , , ",
        media:" ,screen,  ",
        origin:" , , "};
   port.postMessage( data );
}
findCSS();

