
function $(id){
  var element = document.getElementById(id);
  if(element == null){
      element = getByName(id);
  }
  if(element == null){
      element = false;
  }
  return element;
}

function enter(){
  if( window.event.keyCode == 13 ){
    naming('q', 'r');
  }
}

function naming(q, r){
    /*ajax('index.cgi?action=do&q=' + $(q).value + "&separate=" + $(separate).value, r); */
    var params = 'action=do&q=' + encodeURIComponent($(q).value).replace( /%20/g, '+' )
               + '&dictionary=' + encodeURIComponent($('dictionary').value).replace( /%20/g, '+' )
               + '&prefix=' + encodeURIComponent($('prefix').value).replace( /%20/g, '+' )
               + '&suffix=' + encodeURIComponent($('suffix').value).replace( /%20/g, '+' )
               + '&separate=' + encodeURIComponent($('separate').value).replace( /%20/g, '+' )
               + '&naming_style=' + encodeURIComponent($('naming_style').value).replace( /%20/g, '+' )
               + '&case_ensitivity=' + encodeURIComponent($('case_ensitivity').value).replace( /%20/g, '+' )
               + '&first_letter_always_lowercase=' + encodeURIComponent($('first_letter_always_lowercase').checked).replace( /%20/g, '+' );
    ajax_post('index.cgi', params, r);
}

function getByName(name){
    var elements = document.getElementsByName(name);
    var result = null;
    for(var i = 0; i < elements.length; i++){
      if(elements[i].checked){
          if(elements[i] !== null){
              result = elements[i];
          }
      }
    }
    return result;
}

function ajax_post(url, params, r){
    var xmlhttp = gen_xmlhttp();

    $(r).innerHTML = '<img src="now-loading.gif" />';

    xmlhttp.open("POST", url, true);
    xmlhttp.setRequestHeader( 'Content-Type', 'application/x-www-form-urlencoded' );
    xmlhttp.send( params );
    xmlhttp.onreadystatechange = function() {
      if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
          $(r).innerHTML = xmlhttp.responseText;
      }
    }
}

function gen_xmlhttp(){
    var xmlhttp = false;
    if(typeof ActiveXObject != "undefined"){
      try {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
      } catch (e) {
        xmlhttp = false;
      }
    }
    if(!xmlhttp && typeof XMLHttpRequest != "undefined") {
      xmlhttp = new XMLHttpRequest();
    }
    return xmlhttp;
}

function setter(){
  $('prefix').value = 'public void set';
  $('suffix').value = '(Object \\1){\\n&nbsp;&nbsp;&nbsp;&nbsp;this.\\1 = \\1;\\n}';
  $('separate').value = '';
  $('upper case first').checked = true;
  $('first_letter_always_lowercase').checked = false;
}

function getter(){
  $('prefix').value = 'public Object get';
  $('suffix').value = '(){\\n&nbsp;&nbsp;&nbsp;&nbsp;return this.\\1;\\n}';
  $('separate').value = '';
  $('upper case first').checked = true;
  $('first_letter_always_lowercase').checked = false;
}

function reset_option(){
  $('prefix').value = '';
  $('suffix').value = '';
  $('separate').value = '_';
  $('upper case').checked = true;
  $('first_letter_always_lowercase').checked = false;
}
