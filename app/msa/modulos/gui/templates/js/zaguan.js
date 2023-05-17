function send(action, data) {
    if(window.zaguan === undefined){
        const url = get_url(action, data);
        fetch(url);
    } else {
        if(typeof zaguan_logging != 'undefined' && zaguan_logging){
            console.log("send", Date.now() / 1000, action);
        }
        window.zaguan(get_url(action, data));
    }
}

function log(msg){
    send('log', msg);
}

function run_op(operacion, data){
    if(typeof zaguan_logging != 'undefined' && zaguan_logging){
        console.log("run_op", Date.now() / 1000, operacion);
    }
    func = window[operacion];
    data = JSON.parse(data);
    if (typeof(func) !== "function"){
        console.warn(`Error en la operación ${operacion}: '${func}' no es una función.`);
        return;
    }
    func(data);
}

function get_url_function(prefix){
  function _inner(action, data){
      if(data === undefined) {
          data = "";
      }
      var json_data = JSON.stringify(data);
      if(typeof debug_enabled != 'undefined' && debug_enabled){
          server = debug_server + "/";
      } else{
          server = "";
      }
      var url = "http://" + server + prefix + "/" + action + "?" + json_data;
      return url;
  }
  return _inner;
}

