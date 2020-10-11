var file_area = document.getElementById('drag-drop-area');
var fileInput = document.getElementById('fileInput');

file_area.addEventListener('dragover', function(evt){
  evt.preventDefault();
  file_area.classList.add('dragover');
});

file_area.addEventListener('dragleave', function(evt){
    evt.preventDefault();
    file_area.classList.remove('dragover');
});
file_area.addEventListener('drop', function(evt){
    evt.preventDefault();
    file_area.classList.remove('dragenter');
    var files = evt.dataTransfer.files;
    fileInput.files = files;
});
