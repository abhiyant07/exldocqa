function show() {
  document.getElementById('loader').style.visibility = 'visible';
}

function hide() {
  document.getElementById('loader').style.visibility = 'hidden';
}

function clear() {
        document.getElementById("output").innerHTML = "";
    }

function uploadFile() {
    clear()
	show()
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files;
    /*alert(file)*/
    if (!file) {
        alert("Please select a file!");
        return;
    }
    const formData = new FormData();
        for (var i = 0; i < file.length; ++i){
        /*alert(i +" " +file.item(i))*/
        formData.append("file", file.item(i));
        }
    fetch("http://192.168.1.11:5000/upload", {
        method: "POST",
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
            hide()
            document.getElementById("output").innerHTML = data.result;
    })
    .catch(error => {
        console.error("Error uploading file:", error);
    });
}

function ask_ques() {

        const textBoxValue = document.getElementById("question").value;
        if (!textBoxValue) {
        alert("Please ask a question!");
        return;
    }
        const data = {
    questions: textBoxValue    
        };
        const jsonData = JSON.stringify(data);
    const headers = {
    "Content-Type": "application/json"
    // Add any other headers you need
        };
    
    fetch("http://192.168.1.11:5000/askQuestion", {
        method: "POST",
                headers: headers,
        body: jsonData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("quesoutput").innerHTML = data.answer;
    })
    .catch(error => {
        console.error("Error in asking question:", error);
    });
}