

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