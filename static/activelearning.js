const select = document.querySelector(".suggestion");
const label = document.querySelector(".text_input");
const submitButton = document.getElementById("myBtn")

submitButton.disabled = true;

let selectValue = 0;
let labelValue = 0;

select.addEventListener("change", (e) => {
  selectValue = e.target.value.length;
  // console.log(selectValue.length)
  console.log(selectValue)
  checkButtonEnabled();
  // console.log(selectValue)
});

label.addEventListener("input", (e) => {
  labelValue = e.target.value.length;
  console.log(labelValue)
  // console.log(labelValue.length)
  checkButtonEnabled();
});

// function checkButtonEnabled() {
//   if (selectValue && labelValue) {
//     submitButton.disabled = true;
//   } else if (selectValue || labelValue) {
//     submitButton.disabled = false;
//   }
// }
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
// var totalSeconds = 0;
var totalSeconds = document.getElementById("secs").innerText;

console.log(minutesLabel.innerText)
console.log(secondsLabel.innerText)

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