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

    oldName: null,
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
  data = {name: form.name, link: form.link, password: form.password}
  $.getJSON($SCRIPT_ROOT + '/new_password', data, function(response)
  {
    if (response.result != "true")
    {
      alert("Couldn't save password.");
    }
  });
  window.location = "/";
}
