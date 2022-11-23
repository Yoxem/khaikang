$name = (x) => document.getElementsByName(x);
$ = (x) => document.getElementById(x);

avatarSelector = $name('avatar')[0];

avatarSelector.addEventListener('change', updateAvatarPreview);


function updateAvatarPreview(event) {
    tmpFilename = avatarSelector.files[0];
    if (tmpFilename) {
        
        fileSizeMaxBound = 4 * (1024 ** 2); // in MB
        if (tmpFilename.size > fileSizeMaxBound){
            alert(`The file size is ${tmpFilename.size / (1024 ** 2)} MB, exceeding ${fileSizeMaxBound / (1024 ** 2)}MB`);
            avatarSelector.value = "";
        }else{
            $('avatar-img').src = URL.createObjectURL(tmpFilename);
        }
    }
}