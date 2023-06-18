let MAX_CUSTOM_SPECIES = 1;
let SPECIES_FORM_PREFIX = ''
let ACCESSION_FORM_PREFIX = ''
const help_text = document.getElementById("help_text");
help_text.innerText = HELP_TEXT_INSERTING_MAIL.trim()


function initScript(){
  //MAX_CUSTOM_SPECIES = max_custom;
  //SPECIES_FORM_PREFIX = species_prefix;
  //ACCESSION_FORM_PREFIX = accession_prefix;
}

const job_form = document.getElementById("theForm")


const theFile = document.getElementById("theFile");
const theFile2 = document.getElementById("theFile2");
const isPaired = document.getElementById("isPaired");
const isNotPaired = document.getElementById("isNotPaired");

isPaired.checked = false;
isNotPaired.checked = true;


const resetHome = () => {
  job_form.reset();
  document.getElementById("mail_div").classList.remove("hidden");
  document.getElementById("file_div").classList.add("hidden");
  document.getElementById("summary_div").classList.add("hidden");
  isPaired.checked = false;
  isNotPaired.checked = true;

  reset_continue_after_mail();
  checkMail({"target": document.getElementById("theMail")})

  showTheFile2();
  return true;
}


const buttonClick = () => {
  document.getElementById("page_title").classList.add("hidden");
  resetHome();
  const form_div = document.getElementById("formdiv")
  const job_button = document.getElementById("job_button")

  job_button.classList.remove('opacity-100');
  job_button.classList.add('opacity-0');
  setTimeout(() => {
    job_button.classList.add('hidden');
    form_div.classList.remove('hidden');
    setTimeout(() => {
      form_div.classList.remove('opacity-0');
      
      checkMail({"target": document.getElementById("theMail")})
      // form_div.classList.add('opacity-100');

    }, 50);
  }, 250);

}


const reset_continue_after_mail = () => {
    const continue_button_mail = document.getElementById("continue_after_mail");

    continue_button_mail.classList.remove("hover:bg-green-600","hover:text-white", "text-green-600", "cursor-pointer")
    continue_button_mail.classList.add("bg-gray-600","text-white")
    continue_button_mail.removeEventListener("click", formForward)

}

const checkMail = (event) => {
    let res = String(event.target.value).toLowerCase().match(
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    );
    if (event.target.value == "" || res) {
        res =  true;
        event.target.valid = true;
    } else {
        event.target.valid = false;
    }

    const continue_button_mail = document.getElementById("continue_after_mail");

    if (res == null) {
        event.target.classList.remove("text-green-600");
        event.target.classList.add("text-red-500");
        event.target.valid = false;
        reset_continue_after_mail();
        theFile.disabled = true;
        return false;
    } else {
        event.target.classList.remove("text-red-500");
        event.target.classList.add("text-green-600");
        event.target.valid = true;
        continue_button_mail.classList.remove("bg-gray-600","text-white")
        continue_button_mail.classList.add("hover:bg-green-600","hover:text-white", "text-green-600", "cursor-pointer")
        theFile.disabled = false;
        continue_button_mail.addEventListener("click", formForward)
        return true;
    }

}


const email = document.getElementById("theMail");
email.value = ""
email.addEventListener('input', checkMail);
email.addEventListener("keypress", (e) => {
  let flag = false;
  if (e.key === 'Enter') {
    flag = checkMail(e);
  }
  if (flag === true){
    formForward();
  }
});

const job_name = document.getElementById("theJobName");
job_name.value = "";


const resetFile = (target, file_num) => {
    target.value = null;
    target.valid = false;
    const icon_state = document.getElementById("file_icon" + file_num);
    const label_state = document.getElementById("upload_button" + file_num);
    const file_name_span = document.getElementById("file_name" + file_num);

    label_state.classList.remove("bg-green-600");
    icon_state.classList = "fa fa-upload text-black";
    file_name_span.innerText = "";
}

const checkFile = (target,file_num) => {
    const file_name = target.value;
    const extensions = target.accept;

    const file_extension = file_name.split('.').pop();
    const icon_state = document.getElementById("file_icon" + file_num);
    const label_state = document.getElementById("upload_button" + file_num);
    const file_name_span = document.getElementById("file_name" + file_num);

    if (!extensions.includes(file_extension) || file_extension == '') {
        resetFile(target, file_num);
        alert("please select a valid file!")
        return false;
    }
    
    target.valid = true;
    label_state.classList.add("bg-green-600");
    icon_state.classList = "fa fa-check text-white";
    file_name_span.innerText = target.files[0].name;;

    return true;
}



const formForward = () => {
    if (job_form[0].value == "" || job_form[0].value) {
        document.getElementById("mail_div").classList.add("hidden");
        document.getElementById("file_div").classList.remove("hidden");
        help_text.innerText = HELP_TEXT_UPLOADING_FILE.trim()
    }
    if(isPaired.checked && theFile.valid && theFile2.valid ||
        !isPaired.checked && theFile.valid){
        document.getElementById("file_div").classList.add("hidden");
        showSummaryPage();
    }
}

function showSummaryPage() {

  document.getElementById("summary_div").classList.remove("hidden");
  
  document.getElementById("user_job_name").innerText = job_form[1].value;
  document.getElementById("user_email_adress").innerText = job_form[0].value;
  document.getElementById("user_is_paired").innerText = isPaired.checked;
  document.getElementById("user_file0").classList.add("text-xs");
  document.getElementById("user_file1").classList.add("text-xs");

  document.getElementById("user_file0").innerText = document.getElementById("file_name" + "0").innerText;
  document.getElementById("user_file1").innerText = document.getElementById("file_name" + "1").innerText;
  
  const submit_button = document.getElementById("submit_button");
  submit_button.classList.remove("hover:bg-green-600","hover:text-white", "text-green-600", "cursor-pointer")
  submit_button.classList.add("bg-gray-600","text-white")
  
  help_text.innerText = HELP_TEXT_SUMMARY_PAGE.trim()
  // should be removed from here once the recaptcha is ready (and then will be callaed from enablePostForm
  submit_button.classList.remove("bg-gray-600","text-white")
  submit_button.classList.add("hover:bg-green-600","hover:text-white", "text-green-600", "cursor-pointer")
  submit_button.addEventListener("click", postForm)
}

function enablePostForm(event) {
  submit_button.classList.remove("bg-gray-600","text-white")
  submit_button.classList.add("hover:bg-green-600","hover:text-white", "text-green-600", "cursor-pointer")
  submit_button.addEventListener("click", postForm)
}

function postForm() {
    document.getElementById("submit_button").removeEventListener("click", postForm);
    document.getElementById("formdiv").classList.add("hidden")
    document.getElementById("after_post").classList.remove("hidden")

    let formdata = new FormData(document.getElementById("theForm"));

    let request = new XMLHttpRequest();

    request.upload.addEventListener('progress', (event) => {

        var file1Size = document.getElementById('theFile').files[0].size;
        var file2Size = document.getElementById('theFile2');
        file2Size = file2Size.valid ? file2Size.files[0].size : 0;
        console.log(file1Size, file2Size, event.loaded)
        if (event.loaded <= file1Size) {
            var percent = Math.round(event.loaded / (file1Size+file2Size) * 100);
        //   document.getElementById('progress-bar').style.width = percent + '%';
            document.getElementById('progress-bar').innerHTML = 'Your sequences are being uploaded. Do not close this window. Uploaded: ' + percent + '%';
        }
        if(event.loaded == event.total){
        //   document.getElementById('progress-bar').style.width = '100%';
            document.getElementById('progress-bar').innerHTML = 'Your file has been uploaded. We are processing and validating your file. Don\'t close or refresh the window. This may take a few minutes for a small file and up to two hours for a large one.';
        }
    });


    request.open('POST', '');
    request.send(formdata);

    request.onreadystatechange = () => {
        if (request.readyState == XMLHttpRequest.DONE) {
            var OK = 200;

            if (request.status === OK) {
                window.location.href = request.responseURL;
            }
            else {
                console.log ('Error: ' + request.status); 
            }
        }
    };

}

const showTheFile2 = () => {
    theFile2_button = document.getElementById('upload_button1');

    isPaired.checked ? theFile2_button.classList.remove('hidden') : theFile2_button.classList.add('hidden');
    resetFile(theFile,0)
    resetFile(theFile2,1)
}

isPaired.addEventListener('click', showTheFile2);
isNotPaired.addEventListener('click', showTheFile2);

theFile.value = null
theFile2.value = null

theFile.addEventListener('input', (event) => {
    checkFile(event.target, 0);
    formForward();
});
theFile2.addEventListener('input', (event) => {
    checkFile(event.target, 1);
    formForward();
});

document.getElementById("custom_button").addEventListener("click", customDBSelector)
document.getElementById("cont_summary_button").addEventListener("click", showSummaryPage)

