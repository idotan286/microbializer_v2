let MAX_CUSTOM_SPECIES = 1;
let SPECIES_FORM_PREFIX = ''
let ACCESSION_FORM_PREFIX = ''
const help_text = document.getElementById("help_text");
help_text.innerText = HELP_TEXT_INSERTING_MAIL.trim()

const PageStates = {
  Mail: 0,
  File: 1,
  SettingConfiguration: 2,
  Parameters: 3,
  Summary: 4
}

function initScript(){
  //MAX_CUSTOM_SPECIES = max_custom;
  //SPECIES_FORM_PREFIX = species_prefix;
  //ACCESSION_FORM_PREFIX = accession_prefix;
}

const job_form = document.getElementById("theForm")
const theFile = document.getElementById("theFile");

const resetHome = () => {
  job_form.reset();
  document.getElementById("mail_div").classList.remove("hidden");
  document.getElementById("file_div").classList.add("hidden");
  document.getElementById("summary_div").classList.add("hidden");
  document.getElementById("paramaters_div").classList.add("hidden");
  document.getElementById("is_advanced_div").classList.add("hidden");

  reset_continue_after_mail();
  checkMail({"target": document.getElementById("theMail")})

  return true;
}

const buttonClick = () => {
  document.getElementById("page_title").classList.add("hidden");
  document.getElementById("page_liscene").classList.add("hidden");
  resetHome();
  const form_div = document.getElementById("formdiv")
  const job_button = document.getElementById("job_button")
  const nav_btns = document.getElementById("nav_btns");
  
  job_button.classList.remove('opacity-100');
  job_button.classList.add('opacity-0');
  nav_btns.classList.add("hidden");
  
  setTimeout(() => {
    job_button.classList.add('hidden');
    form_div.classList.remove('hidden');
    nav_btns.classList.add("hidden");
    setTimeout(() => {
      form_div.classList.remove('opacity-0');
      
      checkMail({"target": document.getElementById("theMail")})
      // form_div.classList.add('opacity-100');

    }, 50);
  }, 250);

}

const reset_continue_after_mail = () => {
    const continue_button_mail = document.getElementById("continue_after_mail");

    continue_button_mail.classList.remove("hover:bg-lime-600","hover:text-white", "text-green-600", "cursor-pointer")
    continue_button_mail.classList.add("bg-gray-600","text-white")
    continue_button_mail.removeEventListener("click", () => formForward(PageStates.File))

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
        continue_button_mail.classList.add("hover:bg-lime-600","hover:text-white", "text-green-600", "cursor-pointer")
        theFile.disabled = false;
        continue_button_mail.addEventListener("click", () => formForward(PageStates.File))
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
    formForward(PageStates.File);
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

const formForward = (state) => {
    console.log('formForward ', state)
    if (state == PageStates.File && (job_form[0].value == "" || job_form[0].value)) {
        document.getElementById("mail_div").classList.add("hidden");
        document.getElementById("file_div").classList.remove("hidden");
        help_text.innerText = HELP_TEXT_UPLOADING_FILE.trim()
    }
    if (state == PageStates.SettingConfiguration && theFile.valid){
        document.getElementById("file_div").classList.add("hidden");
        document.getElementById("is_advanced_div").classList.remove("hidden");
        document.getElementById("defaultSetting").addEventListener("click", () => formForward(PageStates.Summary))
        document.getElementById("advancedSetting").addEventListener("click", () => formForward(PageStates.Parameters))
    }
    if (state == PageStates.Parameters){
        document.getElementById("is_advanced_div").classList.add("hidden");
        document.getElementById("paramaters_div").classList.remove("hidden");
        document.getElementById("continue_after_parameters").addEventListener("click", () => formForward(PageStates.Summary))
    }
    if (state == PageStates.Summary){
        document.getElementById("is_advanced_div").classList.add("hidden");
        document.getElementById("paramaters_div").classList.add("hidden");
        showSummaryPage();
    }
}

function showSummaryPage() {

  document.getElementById("summary_div").classList.remove("hidden");
  
  document.getElementById("user_job_name").innerText = job_form[1].value;
  document.getElementById("user_email_adress").innerText = job_form[0].value;
  document.getElementById("user_file0").classList.add("text-xs");

  document.getElementById("user_file0").innerText = document.getElementById("file_name" + "0").innerText;
  document.getElementById("user_coverage_cutoff").innerText = document.getElementById("coverageCutoff").value;
  document.getElementById("user_identity").innerText = document.getElementById("minIdentity").value;
  document.getElementById("user_core_gene").innerText = document.getElementById("orthologsPercent").value;
  document.getElementById("user_outgroup").innerText = document.getElementById("outgroup").value;
  document.getElementById("user_is_bootstrap").innerText = document.getElementById("isApplyBootstrap").checked;
  document.getElementById("user_is_filter").innerText = document.getElementById("isApplyFilter").checked;
  document.getElementById("user_is_orpan").innerText = document.getElementById("isAddOrphan").checked;
  if (document.getElementById("genomeFastaType").checked){
        document.getElementById("user_fasta_type").innerText = "Genomes"
  } else {
        document.getElementById("user_fasta_type").innerText = "ORFs"
  }

  
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
        console.log(file1Size, event.loaded)
        if (event.loaded <= file1Size) {
            var percent = Math.round(event.loaded / (file1Size) * 100);
        //   document.getElementById('progress-bar').style.width = percent + '%';
            document.getElementById('progress-bar').innerHTML = 'Your sequences are being uploaded. Do not close this window. Uploaded: ' + percent + '%';
        }
        if(event.loaded == event.total){
        //   document.getElementById('progress-bar').style.width = '100%';
            document.getElementById('progress-bar').innerHTML = 'Your file has been uploaded. We are processing and validating your file. Don\'t close or refresh the window. This may take an hour for a small number of genomes and up to several days for a large one.';
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

theFile.value = null

theFile.addEventListener('input', (event) => {
    checkFile(event.target, 0);
    formForward(PageStates.SettingConfiguration);
});

function getCookie(name) {
    let match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
}

function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + "; path=/" + expires;
}

function acceptCookies() {
    setCookie("cookieConsent", "true", 365);
    document.getElementById("cookie-banner").style.display = "none";
}

window.onload = function () {
    if (!getCookie("cookieConsent")) {
        document.getElementById("cookie-banner").style.display = "block";
    }
};

window.dataLayer = window.dataLayer || [];
function gtag(){ dataLayer.push(arguments); }
gtag('consent', 'default', {
  'analytics_storage': 'denied'
});

