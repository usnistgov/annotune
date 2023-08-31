
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
var hoursLabel = document.getElementById("hour");

var minutesLabels = document.getElementById("minutess");
var secondsLabels = document.getElementById("secondss");
var hoursLabels = document.getElementById("hours");
var colon = document.getElementById('colon')
var colons = document.getElementById('colons')
// var totalSeconds = 0;
var totalSeconds = document.getElementById("secs").innerText;

console.log(minutesLabel)
console.log(secondsLabel)

setInterval(setTime, 1000);

function setTime()
{
    ++totalSeconds;
    secondsLabels.innerHTML = pad(totalSeconds%60);
    minutesLabels.innerHTML = pad(parseInt((totalSeconds/60)%60));
    hoursLabels.innerHTML = pad(parseInt(Math.floor(totalSeconds/60)/60));
    colon.innerHTML=':';
    colons.innerHTML=':';

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

setTimeout(() => {
  const box = document.getElementById('loader');

  // 👇️ removes element from DOM
  box.style.display = 'none';

  // 👇️ hides element (still takes up space on page)
  // box.style.visibility = 'hidden';
}, 1000);