let wordsToHighlight = []
const acc = document.querySelectorAll(".right_topics");
console.log(acc)


textElement=document.getElementById("text");
// console.log(textElement.innerText)
const original_text = textElement.innerText;
const viewButtons = document.querySelectorAll(".view");



viewButtons.forEach((btn, index) => {
    btn.addEventListener("click", function (event) {
        // removeAllActive()
        let topic_el = btn.parentElement.nextElementSibling.getElementsByTagName("span");
        
        const wordsArr = [];
        Array.from(topic_el).forEach(function (ele) {
            wordsArr.push(ele.innerText);
        });
        console.log(wordsArr)
        highlighWords(wordsArr);

    });
});



function highlighWords(words) {
    var text = original_text;
    words.forEach((word) => {
      if (word.length>2){
        const pattern = new RegExp(word, "gi");
        text = text.replace(
          pattern,
          "<span style='background-color:yellow'>" + word + "</span>"
        );
        textElement.innerHTML = text;
        // console.log(textElement)
      }
    });
  }



  function openForm() {
    document.getElementById("loginPopup").style.display = "block";
  }
  function closeForm() {
    document.getElementById("loginPopup").style.display = "none";
  }
  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function (event) {
    let modal = document.getElementById('loginPopup');
    if (event.target == modal) {
      closeForm();
    }
  }
  

