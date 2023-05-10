var each_document  = document.querySelectorAll(".each_document");

each_document.forEach((doc) =>{
    doc.addEventListener("click", event => {
    console.log(doc.id)
})})