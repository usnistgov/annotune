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



  // function openForm() {
  //   document.getElementById("loginPopup").style.display = "block";
  // }
  // function closeForm() {
  //   document.getElementById("loginPopup").style.display = "none";
  // }
  // // When the user clicks anywhere outside of the modal, close it
  // window.onclick = function (event) {
  //   let modal = document.getElementById('loginPopup');
  //   if (event.target == modal) {
  //     closeForm();
  //   }
  // }


// written = document.getElementById("written")
// sugg= document.getElementById("suggestion")

// // label = document.forms["responses"]["label"].value

// var write  = written.value
// var suggest = sugg.value


// written.onkeyup = function() {
//   console.log(this.value);
// };



// sugg.addEventListener("click", function(event){
//   console.log(sugg.value)

// })


// // console.log(written)
// // console.log(sugg)

// traps = document.getElementById("myBtn")
// traps.disabled = false;
// traps.classList.add("fadeIn");
  


const select = document.querySelector(".suggestion");
const label = document.querySelector(".text_input");
const submitButton = document.querySelector("#myBtn");
console.log({ select, submitButton });

submitButton.disabled = true;

let selectValue;
let labelValue;

select.addEventListener("change", (e) => {
  selectValue = e.target.value;
  checkButtonEnabled();
});

label.addEventListener("change", (e) => {
  labelValue = e.target.value;
  checkButtonEnabled();
});

function checkButtonEnabled() {
  if (selectValue && labelValue) {
    submitButton.disabled = true;
  } else if (selectValue || labelValue) {
    submitButton.disabled = false;
  }
}