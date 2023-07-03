let wordsToHighlight = []
const acc = document.querySelectorAll(".right_topics");
// console.log(acc)


textElement=document.getElementById("text");
oritextElement=document.getElementById("original_text");
// console.log(textElement.innerText)
const original_text = oritextElement.innerText;
const viewButtons = document.querySelectorAll(".view");

// const REGEXP_SPECIAL_CHAR = /[\!\#\$\%\^\&\*\)\(\+\=\.\<\>\{\}\[\]\:\;\'\"\|\~\`\_\-]/g;
// const REGEXP_SPECIAL_CHAR = /[\&\*\)\(\+\=\.\<\>]/g;
const REGEXP_SPECIAL_CHAR = /[\<\>]/g;
num = 0

viewButtons.forEach((btn, index) => {
    btn.addEventListener("click", function (event) {
        // removeAllActive()
        let topic_el = btn.parentElement.nextElementSibling.getElementsByTagName("span");
        
        const wordsArr = [];
        Array.from(topic_el).forEach(function (ele) {
            wordsArr.push(ele.innerText);
        });
        // console.log(wordsArr)
        if (num % 2 === 0){
          highlighWords(wordsArr);
        }
        else {
          textElement.innerHTML = original_text;
        }
        num = num + 1
        

    });
});



// function highlighWords(words) {
//     var text = original_text;
//     words.forEach((word) => {
//       if (word.length>2){

//         // const escapedQuery = word.replace(REGEXP_SPECIAL_CHAR, '\\$&');

//         const pattern = new RegExp(escapedQuery, "gi");
//         text = text.replace(
//           pattern,
//           "<mark class='highlighted-word'>" + escapedQuery + "</mark>"
//         );
//         textElement.innerHTML = text;
//         // console.log(textElement)
//       }
//     });
//  }

function highlighWords(words) {
  var text = original_text;
  words.forEach((word) => {
    if (word.length > 2) {
      const pattern = new RegExp(word, "gi");
      text = text.replace(
        pattern,
        "<span class='highlighted-word' >" + word + "</span>"
      );
      textElement.innerHTML = text;
      // console.log(textElement)
    }
  });
}




  


const select = document.querySelector(".suggestion");
const label = document.querySelector(".text_input");
const submitButton = document.getElementById("myBtn")

submitButton.disabled = true;

let selectValue = 0;
let labelValue = 0;

select.addEventListener("change", (e) => {
  selectValue = e.target.value.length;
  // console.log(selectValue.length)
  // console.log(selectValue)
  checkButtonEnabled();
  // console.log(selectValue)
});

label.addEventListener("input", (e) => {
  labelValue = e.target.value.length;
  // console.log(labelValue)
  // console.log(labelValue.length)
  checkButtonEnabled();
});

function checkButtonEnabled() {
  if ((selectValue != 0) && (labelValue === 0) || ((selectValue === 0) && (labelValue != 0))){
    submitButton.disabled = false;
  }
  else {
    submitButton.disabled = true;
  }
}

var minutesLabel = document.getElementById("minutes");
var secondsLabel = document.getElementById("seconds");
var totalSeconds = 0;

console.log(minutesLabel)
console.log(secondsLabel)

setInterval(setTime, 1000);

function setTime()
{
    ++totalSeconds;
    secondsLabel.innerHTML = pad(totalSeconds%60);
    minutesLabel.innerHTML = pad(parseInt(totalSeconds/60));
}

function pad(val)
{
    var valString = val + "";
    if(valString.length < 2)
    {
        return "0" + valString;
    }
    else
    {
        return valString;
    }
}