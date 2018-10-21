oldName = null;
oldLink = null;
oldPassword = null;
oldLastUpdate = null;

Vue.use(VueMaterial.default)

var form = new Vue({
  el: '#form',
  name: 'TextFields',
  data: () => ({
    initial: 'Initial Value',
    type: null,
    withLabel: null,
    inline: null,
    number: null,
    textarea: null,
    autogrow: null,
    disabled: null,

    oldName: sessionStorage.getItem('oldName'),
    name: null,
    link: null,
    password: null

  })
})

var buttons = new Vue({
  el: '#buttons',
  name: 'IconButtons',
  data: {
    showModal: false
  }
})

function generatePassword() {
  var password = "";
  var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789#$%&?!";

  for (var i = 0; i < 12; i++)
    password += possible.charAt(Math.floor(Math.random() * possible.length));

  form.password = password;
}

function savePassword(){
  var lastUpdate = oldLastUpdate;
  if(form.password != form.oldPassword){
    var dateObj = new Date();
    var month = dateObj.getUTCMonth() + 1; //months from 1-12
    var day = dateObj.getUTCDate();
    var year = dateObj.getUTCFullYear();

    lastUpdate = year + "/" + month + "/" + day;
  }

  data = {oldName: oldName, name: form.name, link: form.link, lastUpdate: lastUpdate, password: form.password}
  $.getJSON($SCRIPT_ROOT + '/edit_password', data, function(response)
  {
    if (response.result != "true")
    {
      alert("Couldn't save password.");
    }
  });
  window.location = "/";
}

$(document).ready(function(){
  $.getJSON($SCRIPT_ROOT + '/get_password_list', {}, function(data)
  {
    for (var i in data) {
      if (data[i].name === form.oldName)
      {
        form.name = data[i].name;
        oldName = data[i].name;
        form.link = data[i].link;
        oldLink = data[i].link;
        form.password = data[i].password;
        oldPassword = data[i].password;
        oldLastUpdate = data[i].lastUpdate;
      }
    }
  });
});
