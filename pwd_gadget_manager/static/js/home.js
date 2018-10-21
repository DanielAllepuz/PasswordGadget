Vue.use(VueMaterial.default)

var buttons = new Vue({
  el: '#buttons',
  name: 'IconButtons',
  data: {
    showModal: false
  }
})

var pwdlist = new Vue({
  el: '#pwdlist',
  data:{
    passwords:[]
  }
})

$(document).ready(function(){
  $.getJSON($SCRIPT_ROOT + '/get_password_list', {}, function(data)
  {
    pwdlist.passwords = data;
  });
});

function editPassword(oldName) {
  sessionStorage.setItem('oldName', oldName);
  window.location = "/edit_password_page";
}

function saveToArduino(){
  $.getJSON($SCRIPT_ROOT + '/save_to_arduino', {}, function(data)
  {
    console.log(data);
  });
}

function deletePassword(name)
{
  $.getJSON($SCRIPT_ROOT + '/delete_password', {name: name}, function(data)
  {
    if(data.result == "true")
    {
      $.getJSON($SCRIPT_ROOT + '/get_password_list', {}, function(data)
      {
        pwdlist.passwords = data;
      });
    }
  });
}





// upload(){
//   // Find arduino --> Error if not found
//   // Upload --> Show loading bar
//   // Finish --> success message
//
// }
