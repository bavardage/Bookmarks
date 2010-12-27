function partial(fn) {
  return partialWithScope.apply(this,
    Array.prototype.concat.apply([fn, this],
      Array.prototype.slice.call(arguments, 1)));
}

function partialWithScope(fn, scope) {
  var args = Array.prototype.slice.call(arguments, 2);
  return function() {
    return fn.apply(scope, Array.prototype.concat.apply(args, arguments));
  };
}

function default_error_handler(req, status, error) {
  alert("" + req + status + error);
}
function default_success_handler(data) {
  alert('dsh');
}

function get_bookmarks(query, success, error) {
  error = error ? error : default_error_handler;
  $.ajax({'url': '/api/bookmarks/',
	  'dataType': 'json',
	  'data': query,
	  'error': error,
	  'success': success
	 });
}

function display_bookmarks(data) {
  var html = '';
  data.forEach(function(e) {
    html += '<li>'
	    + '<a class="title" href="' + e.link.url + '">'
	    + e.title
	    + '</a>'
	    + '<span class="tags">' + e.tags + '</span>'
	    + '</li>';
  });
  $('#bookmarks').html(html);
}

function new_submit(success, event) {
  var form_data = $('#new > form').serialize();
  success = success ? success : default_success_handler;
  $.ajax(
    {'url': '/api/bookmarks',
     'cache': 'false',
     'type': "POST",
     'data': form_data,
     'success': success,
     'error': default_error_handler
    });
  $('#new form > input[type!=submit]').val('');
  return false;
}

function setup() {
  get_bookmarks('', display_bookmarks);
  $('#new > form').submit(partial(new_submit, function() {
				    get_bookmarks('', display_bookmarks);
				  }));
}